"""Phase 2 staff Google and private-config contracts; synthetic data only."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import smtplib
import ssl
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
import urllib.error
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
import test_local_service as base
from email_access import EmailAccess, MailError
from google_login import GoogleLogin, GoogleLoginError
from local_service import connect


class PrivateConfig(unittest.TestCase):
    smtp = {'host': 'smtp.example.org', 'port': 465, 'security': 'ssl',
            'sender': 'sender@example.org', 'username': 'synthetic',
            'password': 'synthetic-secret', 'research_domains': ['institute.org']}
    oauth = {'client_id': 'synthetic.apps.googleusercontent.com',
             'client_secret': 'synthetic-oauth-secret',
             'redirect_uris': ['http://127.0.0.1:8797/api/auth/google/callback']}

    def test_smtp_bad_private_files_fail_closed_without_exposing_values(self):
        invalid = [None, [], 'synthetic-secret', {},
                   {**self.smtp, 'port': 0}, {**self.smtp, 'security': 'none'},
                   {**self.smtp, 'host': 'https://smtp.example.org'},
                   {**self.smtp, 'research_domains': ['gmail.com']}]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            for raw in invalid:
                with self.subTest(shape=type(raw).__name__):
                    (path/'email-settings.json').write_text(json.dumps(raw), 'utf-8')
                    mail = EmailAccess(path)
                    self.assertFalse(mail.enabled)
                    self.assertNotIn('synthetic-secret', json.dumps(mail.public()))
                    self.assertNotIn('synthetic-secret', json.dumps(mail.settings()))

    def test_smtp_validator_normalizes_and_rejects_non_objects(self):
        normalized = EmailAccess.validate_config({**self.smtp, 'port': '587', 'security': 'starttls'})
        self.assertEqual(normalized['port'], 587)
        for raw in [None, [], {'password': 'synthetic-secret'}]:
            with self.assertRaises(MailError):
                EmailAccess.validate_config(raw)

    def test_google_bad_private_files_fail_closed_and_validate_exact_callback(self):
        invalid = [None, [], 'synthetic-oauth-secret', {},
                   {**self.oauth, 'client_secret': []},
                   {**self.oauth, 'redirect_uris': 'http://127.0.0.1:8797/api/auth/google/callback'},
                   {**self.oauth, 'redirect_uris': ['http://localhost:8797/api/auth/google/callback']}]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            for raw in invalid:
                with self.subTest(shape=type(raw).__name__):
                    (path/'google-oauth.json').write_text(json.dumps(raw), 'utf-8')
                    google = GoogleLogin(path, 8797)
                    self.assertFalse(google.public()['enabled'])
                    self.assertNotIn('synthetic-oauth-secret', json.dumps(google.public()))
        normalized = GoogleLogin.validate_config({'web': self.oauth}, 8797)
        self.assertEqual(normalized['redirect_uri'], self.oauth['redirect_uris'][0])

    def test_google_unreadable_config_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path/'google-oauth.json').write_text('{}', 'utf-8')
            with patch.object(Path, 'read_text', side_effect=PermissionError('synthetic-secret')):
                google = GoogleLogin(path, 8797)
            self.assertFalse(google.public()['enabled'])
            self.assertNotIn('synthetic-secret', json.dumps(google.public()))

    def test_smtp_ssl_and_starttls_require_certificate_checks_and_send_real_message_shape(self):
        with tempfile.TemporaryDirectory() as folder:
            mail = EmailAccess(Path(folder))
            for security, factory, port in [('ssl', 'SMTP_SSL', 465), ('starttls', 'SMTP', 587)]:
                with self.subTest(security=security), patch('email_access.smtplib.'+factory) as transport:
                    mail.config = {**self.smtp, 'security': security, 'port': port}
                    mail.send_code('recipient@example.edu', '123456')
                    connection = transport.return_value
                    self.assertEqual(transport.call_args.args, ('smtp.example.org', port))
                    self.assertEqual(transport.call_args.kwargs['timeout'], 10)
                    context = transport.call_args.kwargs['context'] if security == 'ssl' else connection.starttls.call_args.kwargs['context']
                    self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
                    self.assertTrue(context.check_hostname)
                    if security == 'starttls':
                        self.assertEqual(connection.ehlo.call_count, 2)
                        connection.starttls.assert_called_once()
                    connection.login.assert_called_once_with('synthetic', 'synthetic-secret')
                    message = connection.send_message.call_args.args[0]
                    self.assertEqual(message['To'], 'recipient@example.edu')
                    self.assertEqual(message['From'].addresses[0].addr_spec, 'sender@example.org')
                    self.assertIn('123456', message.get_body(preferencelist=('plain',)).get_content())

    def test_smtp_transport_failure_has_only_sanitized_error(self):
        with tempfile.TemporaryDirectory() as folder:
            mail = EmailAccess(Path(folder));mail.config = self.smtp.copy()
            with patch('email_access.smtplib.SMTP_SSL', side_effect=smtplib.SMTPAuthenticationError(535, b'synthetic-secret')):
                with self.assertRaises(MailError) as error:
                    mail.send_code('recipient@example.edu', '123456')
            self.assertNotIn('synthetic-secret', str(error.exception))
            self.assertIn('No account was created', str(error.exception))


class StaffGoogle(unittest.TestCase):
    setUp = base.ServiceContract.setUp
    tearDown = base.ServiceContract.tearDown
    reviewer = base.ServiceContract.reviewer

    def configure_google(self):
        self.server.google.config = {'client_id': 'synthetic.apps.googleusercontent.com',
                                    'client_secret': 'synthetic-only',
                                    'redirect_uri': self.base+'/api/auth/google/callback'}
        self.server.google.exchange = lambda code, state: {'subject': 'synthetic-subject',
                                                          'email': 'staff@gmail.com',
                                                          'name': 'Synthetic staff'}

    def new_admin(self):
        status, result = self.admin.call('POST', '/api/admin/roles', {
            'email': 'admin@example.edu', 'role': 'admin', 'password': 'Changed-test-password-42'})
        self.assertEqual(status, 200, result)
        client = base.Client(self.base)
        status, result = client.call('POST', '/api/auth/register', {
            'email': 'admin@example.edu', 'name': 'Synthetic admin', 'password': 'Admin-password-42'})
        self.assertEqual(status, 201, result)
        return client, result['user']['id']

    def start_link(self, client, password):
        status, result = client.call('POST', '/api/auth/google/start', {'mode': 'link', 'password': password})
        self.assertEqual(status, 200, result)
        return parse_qs(urlsplit(result['authorization_url']).query)['state'][0]

    def callback(self, client, state):
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args, **kwargs):
                return None
        jar = next(handler.cookiejar for handler in client.opener.handlers
                   if isinstance(handler, urllib.request.HTTPCookieProcessor))
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar), NoRedirect())
        try:
            response = opener.open(self.base+'/api/auth/google/callback?state='+state+'&code=synthetic')
        except urllib.error.HTTPError as error:
            response = error
        with response:
            return response.status, response.headers['Location']

    def test_admin_can_explicitly_link_then_login_without_promotion(self):
        self.configure_google()
        admin, account = self.new_admin()
        state = self.start_link(admin, 'Admin-password-42')
        self.assertEqual(self.callback(admin, state), (303, '/contribute.html?view=account'))
        self.assertTrue(admin.call('GET', '/api/me')[1]['google_linked'])
        guest = base.Client(self.base)
        status, result = guest.call('POST', '/api/auth/google/start', {'accept_terms': True})
        self.assertEqual(status, 200, result)
        state = parse_qs(urlsplit(result['authorization_url']).query)['state'][0]
        self.assertEqual(self.callback(guest, state), (303, '/contribute.html?view=my-work'))
        user = guest.call('GET', '/api/session')[1]['user']
        self.assertEqual((user['id'], user['role']), (account, 'admin'))
        self.assertEqual(admin.call('GET', '/api/admin/email-settings')[0], 403)

    def test_reviewer_cannot_link_and_unlinked_google_cannot_create_user(self):
        self.configure_google()
        reviewer, _ = self.reviewer()
        self.assertEqual(reviewer.call('POST', '/api/auth/google/start', {
            'mode': 'link', 'password': 'Reviewer-test-password-42'})[0], 403)
        guest = base.Client(self.base)
        status, result = guest.call('POST', '/api/auth/google/start', {'accept_terms': True})
        self.assertEqual(status, 200, result)
        state = parse_qs(urlsplit(result['authorization_url']).query)['state'][0]
        with connect(self.server.db_path) as db:
            before = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        status, destination = self.callback(guest, state)
        self.assertEqual(status, 303)
        self.assertIn('maintainer=1', destination)
        self.assertIn('auth_error=', destination)
        with connect(self.server.db_path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM users').fetchone()[0], before)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM google_identities').fetchone()[0], 0)

    def test_admin_link_requires_own_password_and_matching_csrf(self):
        self.configure_google();admin, _ = self.new_admin()
        for password, token in [('incorrect', admin.csrf), ('Admin-password-42', ''),
                                ('Admin-password-42', self.admin.csrf)]:
            status, result = admin.call('POST', '/api/auth/google/start',
                                        {'mode': 'link', 'password': password}, {'X-CSRF-Token': token})
            self.assertEqual(status, 403, result)
        with connect(self.server.db_path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM oauth_states').fetchone()[0], 0)

    def test_matching_admin_email_alone_never_links_google(self):
        self.configure_google();self.new_admin()
        self.server.google.exchange = lambda code, state: {
            'subject': 'unlinked-subject', 'email': 'admin@example.edu', 'name': 'Synthetic admin'}
        guest = base.Client(self.base)
        status, result = guest.call('POST', '/api/auth/google/start', {'accept_terms': True})
        self.assertEqual(status, 200, result)
        state = parse_qs(urlsplit(result['authorization_url']).query)['state'][0]
        self.assertIn('auth_error=', self.callback(guest, state)[1])
        self.assertIsNone(guest.call('GET', '/api/session')[1]['user'])
        with connect(self.server.db_path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM google_identities').fetchone()[0], 0)

    def test_linked_google_login_is_denied_after_admin_demotion(self):
        self.configure_google();admin, account = self.new_admin()
        self.assertEqual(self.callback(admin, self.start_link(admin, 'Admin-password-42'))[0], 303)
        with connect(self.server.db_path) as db:
            db.execute("UPDATE users SET role='reviewer' WHERE id=?", (account,))
        guest = base.Client(self.base)
        status, result = guest.call('POST', '/api/auth/google/start', {'accept_terms': True})
        self.assertEqual(status, 200, result)
        state = parse_qs(urlsplit(result['authorization_url']).query)['state'][0]
        self.assertIn('auth_error=', self.callback(guest, state)[1])
        self.assertIsNone(guest.call('GET', '/api/session')[1]['user'])

    def test_link_rechecks_role_force_change_suspension_and_session_after_exchange(self):
        self.configure_google()
        for change in ['role', 'force_change', 'suspension', 'session']:
            with self.subTest(change=change):
                state = self.start_link(self.admin, 'Changed-test-password-42')
                def exchange(code, pending):
                    with connect(self.server.db_path) as db:
                        actor = pending['actor']
                        if change == 'role':
                            db.execute("UPDATE users SET role='reviewer' WHERE id=?", (actor,))
                        elif change == 'force_change':
                            db.execute('UPDATE users SET force_change=1 WHERE id=?', (actor,))
                        elif change == 'suspension':
                            db.execute('INSERT INTO account_controls VALUES(?,1,?,?,?)', (actor, 'Synthetic suspension', actor, '2026-10-21'))
                        else:
                            db.execute('DELETE FROM sessions WHERE token=?', (pending['session_token'],))
                    return {'subject': 'synthetic-'+change, 'email': 'staff@gmail.com', 'name': 'Synthetic staff'}
                self.server.google.exchange = exchange
                status, destination = self.callback(self.admin, state)
                self.assertEqual(status, 303)
                self.assertIn('auth_error=', destination)
                with connect(self.server.db_path) as db:
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM google_identities').fetchone()[0], 0)
                    db.execute("UPDATE users SET role='maintainer',force_change=0 WHERE login='minhao'")
                    db.execute('DELETE FROM account_controls')
                self.assertEqual(self.admin.call('POST', '/api/auth/login', {
                    'login': 'minhao', 'password': 'Changed-test-password-42'})[0], 200)


if __name__ == '__main__':
    unittest.main()
