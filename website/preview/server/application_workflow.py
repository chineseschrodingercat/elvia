"""Reviewer application history and a transactional, retryable mail outbox.

Existing application rows and event history are never rewritten by migration.
SMTP delivery is at least once: a crash after SMTP acceptance but before the
sent receipt may retry the same stable Message-ID.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import threading
import time

CATALOG = json.loads((Path(__file__).parent / 'catalogs/research-profile.json').read_text('utf-8'))
FIELDS = frozenset(item for group in CATALOG['fields'] for item in group['items'])
ACTIONS = {'application_submitted': 'pending', 'application_under_review': 'under_review',
           'application_approved': 'approved', 'application_needs_information': 'needs_information',
           'application_declined': 'declined'}


def migrate(db):
    db.execute('''CREATE TABLE IF NOT EXISTS application_notifications(
        event_id INTEGER PRIMARY KEY REFERENCES events(id),
        user_id TEXT NOT NULL REFERENCES users(id), recipient TEXT NOT NULL,
        status TEXT NOT NULL, note TEXT NOT NULL, created TEXT NOT NULL,
        sent_at TEXT, attempts INTEGER NOT NULL DEFAULT 0,
        next_attempt REAL NOT NULL DEFAULT 0, lease_until REAL NOT NULL DEFAULT 0,
        last_error TEXT NOT NULL DEFAULT '')''')


def profile(data, clean, require, web_url):
    result = {key: clean(data.get(key, ''), limit, key.replace('_', ' ')) for key, limit in [
        ('position', 150), ('institution', 300), ('expertise', 3000),
        ('profile_type', 100), ('profile_other', 100), ('profile_url', 2000),
        ('expertise_other', 3000), ('eligibility_note', 2000)]}
    if result['position'] in ('Doctoral researcher', 'Master’s student', "Master's student"):
        result['position'] = 'Graduate student'
    require(result['position'] != 'Independent researcher', 'Choose your current position or Other.')
    require(result['position'] and result['institution'], 'Current position and institution are required.')
    selected = data.get('expertise_fields', [])
    require(isinstance(selected, list) and len(selected) <= 5,
            'Choose at most five areas of expertise, including Other.')
    require(all(isinstance(x, str) and (x in FIELDS or x == 'Other') for x in selected),
            'Choose expertise from the list, or use Other.')
    require(len(set(selected)) == len(selected), 'Choose each area of expertise only once.')
    require(('Other' in selected) == bool(result['expertise_other']),
            'Select Other and describe the additional area, or leave both blank.')
    result['expertise_fields'] = selected
    if 'expertise_fields' in data:
        result['expertise'] = '; '.join(result['expertise_other'] if x == 'Other' else x for x in selected)
    kind = result['profile_type']
    require(not kind or kind in CATALOG['profile_types'], 'Choose a research profile type from the list.')
    require(not kind or result['profile_url'], 'Enter the URL for the selected research profile.')
    require(kind != 'Other' or result['profile_other'], 'Name the other research profile service.')
    require(not result['profile_other'] or kind == 'Other', 'Choose Other for a custom profile service.')
    require(not result['profile_url'] or web_url(result['profile_url']), 'Use a full http or https profile URL.')
    if result['profile_url'] and not kind:
        result['profile_type'] = 'Other'
        result['profile_other'] = 'Research profile'
    return result


def record_transition(db, actor, user_id, status, note, created):
    action = next(action for action, value in ACTIONS.items() if value == status)
    event = db.execute('INSERT INTO events(actor,target,action,note,created) VALUES(?,?,?,?,?)',
                       (actor, user_id, action, note, created)).lastrowid
    verified = db.execute('SELECT email FROM verified_emails WHERE user_id=?', (user_id,)).fetchone()
    if verified:
        db.execute('''INSERT INTO application_notifications
            (event_id,user_id,recipient,status,note,created) VALUES(?,?,?,?,?,?)''',
            (event, user_id, verified['email'], status, note, created))


def application_json(db, row):
    if row is None:
        return None
    events = [dict(item) | {'status': ACTIONS[item['action']]} for item in db.execute(
        "SELECT id,action,note,created FROM events WHERE target=? AND action IN (?,?,?,?,?) ORDER BY id",
        (row['user_id'], *ACTIONS))]
    # Progress concerns the current application cycle; full events remain stored.
    start = max((i for i, event in enumerate(events) if event['status'] == 'pending'), default=0)
    version = db.execute("SELECT COALESCE(MAX(id),0) FROM events WHERE target=? AND (action IN (?,?,?,?,?) OR action='application_note_updated')", (row['user_id'], *ACTIONS)).fetchone()[0]
    return dict(row) | {'profile': json.loads(row['profile']), 'timeline': events[start:],
                        'version': version}


@contextmanager
def connection(path):
    db = sqlite3.connect(path, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    try:
        with db:
            yield db
    finally:
        db.close()


def deliver_one(path, mailer, *, now=None):
    now = time.time() if now is None else now
    with connection(path) as db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('''SELECT n.* FROM application_notifications n
            WHERE n.sent_at IS NULL AND n.next_attempt<=? AND n.lease_until<=?
            AND NOT EXISTS(SELECT 1 FROM application_notifications earlier
                WHERE earlier.user_id=n.user_id AND earlier.event_id<n.event_id AND earlier.sent_at IS NULL)
            ORDER BY n.event_id LIMIT 1''', (now, now)).fetchone()
        if row is None:
            return False
        db.execute('UPDATE application_notifications SET lease_until=?,attempts=attempts+1 WHERE event_id=?',
                   (now + 120, row['event_id']))
    try:
        mailer.send_application_update(row['recipient'], row['status'], row['note'], row['event_id'])
    except Exception as exc:
        with connection(path) as db:
            db.execute('''UPDATE application_notifications SET lease_until=0,next_attempt=?,last_error=?
                          WHERE event_id=?''',
                       (now + min(3600, 30 * 2 ** min(row['attempts'], 7)), type(exc).__name__, row['event_id']))
    else:
        with connection(path) as db:
            db.execute('UPDATE application_notifications SET sent_at=?,lease_until=0,last_error=? WHERE event_id=?',
                       (datetime.now(timezone.utc).isoformat(), '', row['event_id']))
    return True


class NotificationWorker:
    """Only service entrypoints start mail delivery; constructing test state cannot."""
    def __init__(self, path, mailer):
        self.path, self.mailer = path, mailer
        self.stop = threading.Event()
        self.wake = threading.Event()
        self.thread = threading.Thread(target=self.run, name='application-mail', daemon=True)

    def run(self):
        while not self.stop.is_set():
            try:
                for _ in range(20):
                    if self.stop.is_set() or not deliver_one(self.path, self.mailer):
                        break
            except (OSError, sqlite3.Error):
                # The durable queue is retained. Never log addresses or SMTP data.
                pass
            self.wake.wait(15)
            self.wake.clear()

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.stop.set()
        self.wake.set()
        self.thread.join(timeout=20)
