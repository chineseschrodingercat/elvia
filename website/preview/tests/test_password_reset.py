"""Password recovery risk checks use isolated accounts and synthetic mail only."""
from pathlib import Path
import json
import secrets
import smtplib
import ssl
import sys
import threading
import time
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
import test_local_service as base
from email_access import EmailAccess, MailError
from local_service import connect, make_server, password_matches

REQUEST = '/api/auth/password-reset/request'
COMPLETE = '/api/auth/password-reset/complete'
NEW_PASSWORD = 'Synthetic replacement password 42!'


class ResetMailTransport(unittest.TestCase):
    def test_reset_message_uses_authenticated_tls_and_keeps_link_out_of_headers(self):
        import tempfile
        token = secrets.token_urlsafe(32)
        url = 'http://127.0.0.1:8998/?view=reset-password#token='+token
        with tempfile.TemporaryDirectory() as folder:
            mail = EmailAccess(Path(folder))
            for security, factory, port in [('ssl', 'SMTP_SSL', 465), ('starttls', 'SMTP', 587)]:
                with self.subTest(security=security), patch('email_access.smtplib.'+factory) as transport:
                    mail.config = {'host': 'smtp.example.org', 'port': port, 'security': security,
                                   'sender': 'sender@example.org', 'username': 'synthetic',
                                   'password': 'synthetic-app-password', 'research_domains': []}
                    mail.send_password_reset('recipient@example.edu', url)
                    connection = transport.return_value
                    context = transport.call_args.kwargs['context'] if security == 'ssl' else connection.starttls.call_args.kwargs['context']
                    self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
                    self.assertTrue(context.check_hostname)
                    connection.login.assert_called_once_with('synthetic', 'synthetic-app-password')
                    message = connection.send_message.call_args.args[0]
                    self.assertEqual(message['To'], 'recipient@example.edu')
                    self.assertEqual(message['Subject'], 'Reset your ELVIA password')
                    self.assertNotIn(token, json.dumps(list(message.items())))
                    self.assertIn(url, message.get_body(preferencelist=('plain',)).get_content())
                    self.assertIn('15 minutes', message.get_body(preferencelist=('plain',)).get_content())

    def test_reset_transport_failure_never_echoes_link_or_credentials(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            mail = EmailAccess(Path(folder))
            mail.config = {'host': 'smtp.example.org', 'port': 465, 'security': 'ssl',
                           'sender': 'sender@example.org', 'username': 'synthetic',
                           'password': 'synthetic-app-password', 'research_domains': []}
            with patch('email_access.smtplib.SMTP_SSL', side_effect=smtplib.SMTPException('synthetic-app-password')):
                with self.assertRaises(MailError) as error:
                    mail.send_password_reset('recipient@example.edu', 'http://127.0.0.1:8998/?view=reset-password#token=synthetic-token')
            self.assertNotIn('synthetic-app-password', str(error.exception))
            self.assertNotIn('synthetic-token', str(error.exception))


class PasswordReset(unittest.TestCase):
    tearDown = base.ServiceContract.tearDown

    def reviewer(self,*args,**kwargs):
        result=base.ServiceContract.reviewer(self,*args,**kwargs)
        # This recovery fixture represents an established account, outside the
        # registration-mail hour. Production budgets are never cleared here.
        with connect(self.server.db_path) as db:
            db.execute('UPDATE abuse_mail_reservations SET created=created-3601')
        return result

    def setUp(self):
        base.ServiceContract.setUp(self)
        self.messages = []
        self.delivered = threading.Event()
        self.mail_config = self.server.mailer.config.copy()
        self.install_mailbox()

    def install_mailbox(self):
        def send(email, url):
            self.messages.append((email, url));self.delivered.set()
        self.server.mailer.send_password_reset = send

    def wait_mail(self, count=1):
        deadline = time.monotonic()+3
        while time.monotonic() < deadline:
            with connect(self.server.db_path) as db:
                sent = db.execute('SELECT COUNT(*) FROM password_reset_tokens WHERE sent=1').fetchone()[0]
            if len(self.messages) >= count and sent >= count:
                return
            time.sleep(.01)
        self.fail('The synthetic mail worker did not finish.')

    def issue(self, email):
        status, result = base.Client(self.base).call('POST', REQUEST, {'email': email})
        self.assertEqual(status, 202, result)
        self.wait_mail(len(self.messages) or 1)
        url = urlsplit(self.messages[-1][1])
        self.assertEqual(url.scheme+'://'+url.netloc, self.base)
        self.assertEqual(url.path, '/')
        self.assertEqual(parse_qs(url.query), {'view': ['reset-password']})
        return parse_qs(url.fragment)['token'][0]

    def finish(self, token, password=NEW_PASSWORD, client=None, **extra):
        return (client or base.Client(self.base)).call('POST', COMPLETE,
                {'token': token, 'newpassword': password, **extra})

    def test_unknown_invalid_unverified_alias_and_delivery_failure_are_identical(self):
        reviewer, account = self.reviewer(approve=False)
        with connect(self.server.db_path) as db:
            db.execute('DELETE FROM verified_emails WHERE user_id=?', (account,))
        expected = None
        guest = base.Client(self.base)
        for email in ['missing@example.edu', 'reviewer1@example.edu', 'minhao', '', None, [], 'bad address']:
            response = guest.call('POST', REQUEST, {'email': email})
            self.assertEqual(response[0], 202, response)
            expected = expected or response
            self.assertEqual(response, expected)
        self.assertEqual(self.messages, [])
        with connect(self.server.db_path) as db:
            db.execute('INSERT INTO verified_emails VALUES(?,?,?)', (account, 'reviewer1@example.edu', '2026-10-21'))
        failed = threading.Event()
        def fail(email, url):
            failed.set();raise MailError('Synthetic transport rejection')
        self.server.mailer.send_password_reset = fail
        self.assertEqual(guest.call('POST', REQUEST, {'email': 'reviewer1@example.edu'}), expected)
        self.assertTrue(failed.wait(1))
        with connect(self.server.db_path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM password_reset_tokens WHERE sent=1').fetchone()[0], 0)
        self.server.mailer.config = {}
        self.assertEqual(guest.call('POST', REQUEST, {'email': 'reviewer1@example.edu'}), expected)

    def test_token_is_fragment_only_hashed_at_rest_and_reset_needs_no_old_password(self):
        reviewer, account = self.reviewer(approve=False)
        token = self.issue('REVIEWER1@EXAMPLE.EDU')
        self.assertEqual(len(token), 43)
        self.assertEqual(self.messages[0][0], 'reviewer1@example.edu')
        with connect(self.server.db_path) as db:
            rows = [tuple(row) for row in db.execute('SELECT * FROM password_reset_tokens')]
            self.assertNotIn(token, json.dumps(rows))
        status, result = self.finish(token, client=reviewer, email='attacker@example.edu', role='maintainer')
        self.assertEqual(status, 200, result)
        self.assertTrue(result['reset'])
        self.assertIsNone(reviewer.call('GET', '/api/session')[1]['user'])
        guest = base.Client(self.base)
        self.assertEqual(guest.call('POST', '/api/auth/login', {'login': 'reviewer1@example.edu', 'password': 'Reviewer-test-password-42'})[0], 401)
        self.assertEqual(guest.call('POST', '/api/auth/login', {'login': 'reviewer1@example.edu', 'password': NEW_PASSWORD})[0], 200)
        with connect(self.server.db_path) as db:
            self.assertEqual(db.execute('SELECT role FROM users WHERE id=?', (account,)).fetchone()[0], 'reviewer')
            self.assertNotIn(token, json.dumps([tuple(row) for row in db.execute('SELECT * FROM events')]))

    def test_replay_expired_unknown_and_weak_password_do_not_change_password(self):
        _, account = self.reviewer(approve=False)
        token = self.issue('reviewer1@example.edu')
        for bad in ['', None, [], secrets.token_urlsafe(32)]:
            self.assertEqual(self.finish(bad)[0], 400)
        self.assertEqual(self.finish(token, 'short')[0], 400)
        with connect(self.server.db_path) as db:
            db.execute('UPDATE password_reset_tokens SET expires=0')
        self.assertEqual(self.finish(token)[0], 400)
        with connect(self.server.db_path) as db:
            db.execute('UPDATE password_reset_tokens SET expires=?', (time.time()+900,))
        self.assertEqual(self.finish(token)[0], 200)
        self.assertEqual(self.finish(token, 'Another synthetic password 42!')[0], 400)
        with connect(self.server.db_path) as db:
            self.assertTrue(password_matches(NEW_PASSWORD, db.execute('SELECT password FROM users WHERE id=?', (account,)).fetchone()[0]))

    def test_new_request_invalidates_previous_link_and_rate_survives_restart(self):
        self.reviewer(approve=False)
        first = self.issue('reviewer1@example.edu')
        for number in range(1, 5):
            with connect(self.server.db_path) as db:
                db.execute('UPDATE password_reset_tokens SET created=created-61')
                db.execute('UPDATE abuse_mail_reservations SET created=created-61')
            self.delivered.clear()
            status, result = base.Client(self.base).call('POST', REQUEST, {'email': 'reviewer1@example.edu'})
            self.assertEqual(status, 202, result);self.wait_mail(number+1)
        self.assertEqual(self.finish(first)[0], 400)
        port = self.server.server_port
        self.server.shutdown();self.server.server_close();self.thread.join()
        self.server = make_server(Path(self.tmp.name), port)
        self.server.mailer.config = self.mail_config.copy();self.install_mailbox()
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True);self.thread.start()
        response = base.Client(self.base).call('POST', REQUEST, {'email': 'reviewer1@example.edu'})
        self.assertEqual(response[0], 202)
        with connect(self.server.db_path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM password_reset_tokens').fetchone()[0], 5)
        self.assertEqual(len(self.messages), 5)

    def test_request_acknowledges_before_delivery_and_has_a_bounded_worker_limit(self):
        for number in range(1, 4):
            self.reviewer(number, approve=False)
        release = threading.Event();started = threading.Event();calls = []
        def blocked(email, url):
            calls.append(email);started.set();release.wait(3)
        self.server.mailer.send_password_reset = blocked
        response = [];returned = threading.Event()
        def request():
            response.append(base.Client(self.base).call('POST', REQUEST, {'email': 'reviewer1@example.edu'}));returned.set()
        requester = threading.Thread(target=request);requester.start()
        try:
            self.assertTrue(returned.wait(1), 'Request acknowledgement must not wait for SMTP.')
            self.assertEqual(response[0][0], 202)
            self.assertTrue(started.wait(1))
            for number in (2, 3):
                self.assertEqual(base.Client(self.base).call('POST', REQUEST, {'email': f'reviewer{number}@example.edu'})[0], 202)
            self.assertLessEqual(len(calls), 2)
            with connect(self.server.db_path) as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM password_reset_tokens').fetchone()[0], 2)
        finally:
            release.set();requester.join()
        deadline = time.monotonic()+2
        while time.monotonic() < deadline:
            with connect(self.server.db_path) as db:
                sent = db.execute('SELECT COUNT(*) FROM password_reset_tokens WHERE sent=1').fetchone()[0]
            if sent == 2:
                break
            time.sleep(.01)

    def test_completion_preserves_role_google_and_suspension_but_revokes_sessions_states(self):
        reviewer, account = self.reviewer(approve=False)
        other = base.Client(self.base)
        other.call('POST', '/api/auth/login', {'login': 'reviewer1@example.edu', 'password': 'Reviewer-test-password-42'})
        with connect(self.server.db_path) as db:
            db.execute("UPDATE users SET role='admin' WHERE id=?", (account,))
            db.execute('INSERT INTO google_identities VALUES(?,?,?,?)', ('synthetic-linked', account, 'staff@gmail.com', '2026-10-21'))
            db.execute('INSERT INTO account_controls VALUES(?,1,?,?,?)', (account, 'Synthetic suspension', account, '2026-10-21'))
            session_token = db.execute('SELECT token FROM sessions WHERE user_id=? LIMIT 1', (account,)).fetchone()[0]
            db.execute('INSERT INTO oauth_states VALUES(?,?,?,?,?,?,?,?)', ('synthetic-state', 'binding', 'verifier', 'nonce', time.time()+600, account, session_token, 'link'))
            db.execute('INSERT INTO email_challenges VALUES(?,?,?,?,?,?,?)', ('synthetic-code', 'reviewer1@example.edu', 'hash', time.time(), time.time()+600, 0, 1))
        token = self.issue('reviewer1@example.edu')
        self.assertEqual(self.finish(token)[0], 200)
        with connect(self.server.db_path) as db:
            self.assertEqual(db.execute('SELECT role FROM users WHERE id=?', (account,)).fetchone()[0], 'admin')
            self.assertEqual(db.execute('SELECT suspended FROM account_controls WHERE user_id=?', (account,)).fetchone()[0], 1)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM google_identities WHERE user_id=?', (account,)).fetchone()[0], 1)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM sessions WHERE user_id=?', (account,)).fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM oauth_states WHERE actor=?', (account,)).fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM email_challenges WHERE email=?', ('reviewer1@example.edu',)).fetchone()[0], 0)
        self.assertIsNone(other.call('GET', '/api/session')[1]['user'])
        self.assertEqual(other.call('POST', '/api/auth/login', {'login': 'reviewer1@example.edu', 'password': NEW_PASSWORD})[0], 403)

    def test_manual_password_change_and_revoked_email_invalidate_pending_reset(self):
        reviewer, account = self.reviewer(approve=False)
        token = self.issue('reviewer1@example.edu')
        self.assertEqual(reviewer.call('POST', '/api/auth/password', {
            'current': 'Reviewer-test-password-42', 'password': 'Manual synthetic password 42!'})[0], 200)
        self.assertEqual(self.finish(token)[0], 400)
        with connect(self.server.db_path) as db:
            db.execute('UPDATE password_reset_tokens SET created=created-61')
            db.execute('UPDATE abuse_mail_reservations SET created=created-61')
        token = self.issue('reviewer1@example.edu')
        with connect(self.server.db_path) as db:
            db.execute('DELETE FROM verified_emails WHERE user_id=?', (account,))
        self.assertEqual(self.finish(token)[0], 400)

    def test_concurrent_redemptions_accept_exactly_one_without_auto_login(self):
        self.reviewer(approve=False)
        token = self.issue('reviewer1@example.edu')
        barrier = threading.Barrier(3);results = []
        def redeem():
            barrier.wait();results.append(self.finish(token)[0])
        workers = [threading.Thread(target=redeem) for _ in range(2)]
        for worker in workers:
            worker.start()
        barrier.wait()
        for worker in workers:
            worker.join()
        self.assertEqual(sorted(results), [200, 400])

    def test_explicitly_linked_staff_google_email_recovers_alias_without_link_or_role_changes(self):
        account = self.admin.call('GET', '/api/session')[1]['user']['id']
        with connect(self.server.db_path) as db:
            db.execute('INSERT INTO google_identities VALUES(?,?,?,?)', ('synthetic-owner', account, 'bound@gmail.com', '2026-10-21'))
        token = self.issue('bound@gmail.com')
        self.assertEqual(self.finish(token)[0], 200)
        with connect(self.server.db_path) as db:
            owner = db.execute('SELECT * FROM users WHERE id=?', (account,)).fetchone()
            self.assertEqual((owner['login'], owner['role']), ('minhao', 'maintainer'))
            self.assertEqual(db.execute('SELECT COUNT(*) FROM verified_emails').fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT subject FROM google_identities WHERE user_id=?', (account,)).fetchone()[0], 'synthetic-owner')
        self.assertEqual(base.Client(self.base).call('POST', '/api/auth/login', {'login': 'minhao', 'password': NEW_PASSWORD})[0], 200)

    def test_ambiguous_recovery_address_never_selects_either_account(self):
        self.reviewer(approve=False)
        account = self.admin.call('GET', '/api/session')[1]['user']['id']
        with connect(self.server.db_path) as db:
            db.execute('INSERT INTO google_identities VALUES(?,?,?,?)', ('synthetic-owner', account, 'reviewer1@example.edu', '2026-10-21'))
        self.assertEqual(base.Client(self.base).call('POST', REQUEST, {'email': 'reviewer1@example.edu'})[0], 202)
        self.assertEqual(self.messages, [])
        with connect(self.server.db_path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM password_reset_tokens').fetchone()[0], 0)

    def test_google_recovery_link_is_invalid_after_email_subject_link_or_role_change(self):
        account = self.admin.call('GET', '/api/session')[1]['user']['id']
        with connect(self.server.db_path) as db:
            db.execute('INSERT INTO google_identities VALUES(?,?,?,?)', ('synthetic-owner', account, 'bound@gmail.com', '2026-10-21'))
        for change in ['email', 'subject', 'link', 'role']:
            with self.subTest(change=change):
                token = self.issue('bound@gmail.com')
                with connect(self.server.db_path) as db:
                    if change == 'email':
                        db.execute("UPDATE google_identities SET email='changed@gmail.com' WHERE user_id=?", (account,))
                    elif change == 'subject':
                        db.execute("UPDATE google_identities SET subject='changed-subject' WHERE user_id=?", (account,))
                    elif change == 'link':
                        db.execute('DELETE FROM google_identities WHERE user_id=?', (account,))
                    else:
                        db.execute("UPDATE users SET role='reviewer' WHERE id=?", (account,))
                self.assertEqual(self.finish(token)[0], 400)
                with connect(self.server.db_path) as db:
                    db.execute("UPDATE users SET role='maintainer' WHERE id=?", (account,))
                    db.execute('DELETE FROM google_identities WHERE user_id=?', (account,))
                    db.execute('INSERT INTO google_identities VALUES(?,?,?,?)', ('synthetic-owner', account, 'bound@gmail.com', '2026-10-21'))
                    db.execute('UPDATE password_reset_tokens SET created=created-61')
                    db.execute('UPDATE abuse_mail_reservations SET created=created-61')


if __name__ == '__main__':
    unittest.main()
