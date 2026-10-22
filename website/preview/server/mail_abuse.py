"""Bounded, persistent automatic-mail budgets; no raw recipient or IP storage."""
from datetime import datetime, timezone
import hashlib
import hmac

MAIL_LIMITS = {'cooldown_seconds': 60, 'recipient_hour': 5, 'recipient_day': 10,
               'global_hour': 20, 'global_day': 80, 'global_utc_month': 1000,
               'maximum_rows': 1100}
REQUEST_LIMITS = {'identity_quarter_hour': 12, 'identity_day': 40,
                  'global_quarter_hour': 120, 'global_day': 500, 'maximum_rows': 512}


def initialize_abuse(db):
    db.execute('CREATE TABLE IF NOT EXISTS abuse_mail_reservations(recipient_key TEXT NOT NULL,created REAL NOT NULL)')
    db.execute('CREATE INDEX IF NOT EXISTS abuse_mail_time ON abuse_mail_reservations(created)')
    db.execute('CREATE INDEX IF NOT EXISTS abuse_mail_recipient ON abuse_mail_reservations(recipient_key,created)')
    db.execute('CREATE TABLE IF NOT EXISTS abuse_requests(identity_key TEXT NOT NULL,created REAL NOT NULL)')
    db.execute('CREATE INDEX IF NOT EXISTS abuse_request_time ON abuse_requests(created)')
    db.execute('CREATE INDEX IF NOT EXISTS abuse_request_identity ON abuse_requests(identity_key,created)')


class AbuseBudget:
    """Call reservations only in a caller-owned BEGIN IMMEDIATE transaction.

    Every attempted automatic delivery consumes its reservation, including SMTP
    failure. There is no refund/retry loop that could exceed the local ceiling.
    Request denial records no new key. Existing valid codes/links are untouched.
    """
    def __init__(self, key):
        self.key = key

    def digest(self, scope, identity):
        return hmac.new(self.key, ('elvia-abuse-v1\0'+scope+'\0'+identity).encode(), hashlib.sha256).hexdigest()

    def reserve_request(self, db, identity, now):
        if not db.in_transaction:
            raise ValueError('An immediate write transaction is required.')
        limits = REQUEST_LIMITS
        db.execute('DELETE FROM abuse_requests WHERE created<=?', (now-86400,))
        global_rows = db.execute('SELECT COUNT(*),COALESCE(SUM(created>?),0) FROM abuse_requests', (now-900,)).fetchone()
        if global_rows[0] >= min(limits['global_day'], limits['maximum_rows']) or global_rows[1] >= limits['global_quarter_hour']:
            return False
        identity_key = self.digest('request', identity.strip().casefold())
        own = db.execute('SELECT COUNT(*),COALESCE(SUM(created>?),0) FROM abuse_requests WHERE identity_key=?', (now-900,identity_key)).fetchone()
        if own[0] >= limits['identity_day'] or own[1] >= limits['identity_quarter_hour']:
            return False
        db.execute('INSERT INTO abuse_requests VALUES(?,?)', (identity_key,now))
        return True

    def reserve_mail(self, db, recipient, now):
        if not db.in_transaction:
            raise ValueError('An immediate write transaction is required.')
        limits = MAIL_LIMITS
        month_start = datetime.fromtimestamp(now,timezone.utc).replace(day=1,hour=0,minute=0,second=0,microsecond=0).timestamp()
        # Keep a rolling day across the month boundary, in addition to this month.
        db.execute('DELETE FROM abuse_mail_reservations WHERE created<?', (min(month_start,now-86400),))
        total = db.execute('SELECT COUNT(*),COALESCE(SUM(created>?),0),COALESCE(SUM(created>?),0),COALESCE(SUM(created>=?),0) FROM abuse_mail_reservations', (now-3600,now-86400,month_start)).fetchone()
        if (total[0] >= limits['maximum_rows'] or total[1] >= limits['global_hour'] or
                total[2] >= limits['global_day'] or total[3] >= limits['global_utc_month']):
            return False
        recipient_key = self.digest('recipient', recipient.strip().casefold())
        own = db.execute('SELECT MAX(created),COALESCE(SUM(created>?),0),COALESCE(SUM(created>?),0) FROM abuse_mail_reservations WHERE recipient_key=?', (now-3600,now-86400,recipient_key)).fetchone()
        if ((own[0] is not None and own[0] > now-limits['cooldown_seconds']) or
                own[1] >= limits['recipient_hour'] or own[2] >= limits['recipient_day']):
            return False
        db.execute('INSERT INTO abuse_mail_reservations VALUES(?,?)', (recipient_key,now))
        return True
