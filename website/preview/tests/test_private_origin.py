"""Private-domain authentication uses isolated state and fake providers only."""
from http.client import HTTPConnection
from http.cookies import SimpleCookie
import hashlib
import hmac
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
from local_service import connect, make_server
from google_login import GoogleLogin, GoogleLoginError
from trusted_login_proxy import protected_action,sign_context
from test_trusted_login_proxy import make_synthetic_proxy_key

PRIVATE = 'https://elvia-atlas.org'
CALLBACK = '/api/auth/google/callback'
PASSWORD = 'Synthetic private password 42!'
SMTP = {'host': 'smtp.example.org', 'port': 465, 'security': 'ssl',
        'sender': 'sender@example.org', 'username': 'synthetic',
        'password': 'synthetic-secret', 'research_domains': []}


class WireClient:
    """Numeric test transport; simulate canonical browser Host/Origin and cookies."""
    def __init__(self, server, origin,*,sign_private=True):
        self.server = server
        self.origin = origin
        self.cookies = SimpleCookie()
        self.csrf = ''
        self.last_headers = []
        self.sign_private=sign_private

    def call(self, method, path, data=None, headers=None):
        body = json.dumps(data).encode() if data is not None else None
        outgoing = {'Host': urlsplit(self.origin).netloc, 'Origin': self.origin,
                    'X-CSRF-Token': self.csrf}
        if body is not None:
            outgoing['Content-Type'] = 'application/json'
        if self.sign_private and protected_action(method,path) and self.origin==PRIVATE and hasattr(self.server,'origins'):
            outgoing.update(sign_context(self.server.login_proxy_key,method,path,'192.0.2.10',body))
        if self.cookies:
            outgoing['Cookie'] = '; '.join(name+'='+item.value for name, item in self.cookies.items())
        outgoing.update(headers or {})
        connection = HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        try:
            connection.request(method, path, body, outgoing)
            response = connection.getresponse()
            self.last_headers = response.getheaders()
            blob = response.read()
            result = json.loads(blob) if 'json' in response.getheader('Content-Type', '') else blob
            for name, value in self.last_headers:
                if name.casefold() == 'set-cookie':
                    self.cookies.load(value)
            if isinstance(result, dict) and 'csrf' in result:
                self.csrf = result['csrf']
            return response.status, result
        finally:
            connection.close()


class PrivateOriginHTTP(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.proxy_key,_=make_synthetic_proxy_key(Path(self.tmp.name))
        # The fallback makes the failing-before test demonstrate the existing
        # private Host rejection rather than just a new keyword import error.
        try:
            self.server = make_server(Path(self.tmp.name), bootstrap_password=PASSWORD, private_origin=PRIVATE,login_proxy_key_file=self.proxy_key)
        except TypeError as error:
            if 'private_origin' not in str(error):
                raise
            self.server = make_server(Path(self.tmp.name), bootstrap_password=PASSWORD)
        self.mailbox = {}
        self.reset_messages = []
        self.server.mailer.config = SMTP.copy()
        self.server.mailer.send_code = lambda email, code: self.mailbox.update({email: code})
        self.server.mailer.send_password_reset = lambda email, url: self.reset_messages.append((email, url))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.local_origin = f'http://127.0.0.1:{self.server.server_port}'
        self.local = WireClient(self.server, self.local_origin)
        self.private = WireClient(self.server, PRIVATE)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.tmp.cleanup()

    def register(self, client=None):
        client = client or self.private
        status, result = client.call('POST', '/api/auth/email-code', {'email': 'member@example.edu'})
        self.assertEqual(status, 200, result)
        status, result = client.call('POST', '/api/auth/register', {
            'name': 'Synthetic member', 'email': 'member@example.edu',
            'email_code': self.mailbox['member@example.edu'], 'password': PASSWORD, 'accept_terms': True})
        self.assertEqual(status, 201, result)
        return result['user']['id']

    def configure_google(self, include_private=True):
        self.server.google.config = {'client_id': 'synthetic.apps.googleusercontent.com',
                                    'client_secret': 'synthetic-only',
                                    'redirect_uri': self.local_origin+CALLBACK}
        if include_private:
            self.server.google.config['redirect_uris'] = [self.local_origin+CALLBACK, PRIVATE+CALLBACK]
        self.server.google.exchange = lambda code, state: {
            'subject': 'synthetic-linked-owner', 'email': 'owner@example.org', 'name': 'Synthetic owner'}

    def test_private_registration_and_readonly_guest_preserve_loopback(self):
        self.assertEqual(self.private.call('GET', '/api/session')[0], 200)
        self.assertEqual(self.local.call('GET', '/api/session')[0], 200)
        self.assertEqual(self.private.call('POST', '/api/contributions', {})[0], 401)
        self.register()
        cookie = self.private.cookies['elvia_session']
        self.assertTrue(cookie['secure'])
        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['samesite'], 'Strict')
        self.assertEqual(cookie['domain'], '')
        self.assertEqual(self.private.call('GET', '/api/session')[1]['user']['role'], 'reviewer')
        self.assertIsNone(self.local.call('GET', '/api/session')[1]['user'])
        self.assertEqual(self.private.call('POST', '/api/contributions', {}, {'X-CSRF-Token': 'wrong'})[0], 403)
        self.assertEqual(self.private.call('POST', '/api/auth/logout', {})[0], 200)
        self.assertTrue(self.private.cookies['elvia_session']['secure'])
        self.assertEqual(self.private.cookies['elvia_session']['max-age'], '0')

    def test_exact_host_origin_and_untrusted_proxy_headers_fail_closed(self):
        self.assertEqual(self.private.call('GET', '/api/session')[0], 200)
        for headers in [
            {'Host': 'other.example.org'}, {'Host': 'elvia-atlas.org:443'},
            {'Host': 'elvia-private.minhaoliu.com'},
            {'Origin': self.local_origin}, {'Origin': 'null'}, {'Origin': PRIVATE+'/'},
            {'Forwarded': 'host=elvia-atlas.org;proto=https'},
            {'X-Forwarded-Host': 'elvia-atlas.org'},
            {'X-Forwarded-Proto': 'https'}, {'X-Elvia-Origin': PRIVATE}]:
            with self.subTest(headers=headers):
                self.assertEqual(self.private.call('POST', '/api/auth/login', {
                    'login': 'minhao', 'password': PASSWORD}, headers)[0], 403)
        connection = HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        try:
            connection.putrequest('GET', '/api/session', skip_host=True)
            connection.putheader('Host', 'elvia-atlas.org')
            connection.putheader('Host', 'elvia-atlas.org')
            connection.endheaders()
            response = connection.getresponse()
            self.assertEqual(response.status, 403)
            response.read()
        finally:
            connection.close()

    def test_private_callback_is_disabled_until_exact_uri_is_configured(self):
        self.configure_google(include_private=False)
        self.assertTrue(self.local.call('GET', '/api/session')[1]['google']['enabled'])
        self.assertFalse(self.private.call('GET', '/api/session')[1]['google']['enabled'])
        self.assertEqual(self.private.call('POST', '/api/auth/google/start', {'accept_terms': True})[0], 503)

    def test_private_google_keeps_role_linking_and_origin_bound_callback(self):
        self.configure_google()
        self.assertEqual(self.private.call('POST', '/api/auth/login', {'login': 'minhao', 'password': PASSWORD})[0], 200)
        self.assertEqual(self.private.call('POST', '/api/auth/password', {'current': PASSWORD, 'password': PASSWORD+' changed'})[0], 200)
        owner = self.private.call('GET', '/api/session')[1]['user']['id']
        with connect(self.server.db_path) as db:
            db.execute('INSERT INTO google_identities VALUES(?,?,?,?)', ('synthetic-linked-owner', owner, 'owner@example.org', '2026-10-21'))
        guest = WireClient(self.server, PRIVATE)
        status, result = guest.call('POST', '/api/auth/google/start', {'accept_terms': True})
        self.assertEqual(status, 200, result)
        query = parse_qs(urlsplit(result['authorization_url']).query)
        self.assertEqual(query['redirect_uri'], [PRIVATE+CALLBACK])
        self.assertEqual(guest.cookies['elvia_oauth']['samesite'], 'Lax')
        self.assertTrue(guest.cookies['elvia_oauth']['secure'])
        path = CALLBACK+'?state='+query['state'][0]+'&code=synthetic'
        self.local.cookies.load(guest.cookies.output(header=''))
        self.assertIn('auth_error=', dict(self.local_call_callback(path))['Location'])
        status, _ = guest.call('GET', path)
        self.assertEqual(status, 303)
        self.assertIn(('Location', '/contribute.html?view=maintainer'), guest.last_headers)
        self.assertEqual(guest.call('GET', '/api/session')[1]['user']['id'], owner)
        self.assertTrue(guest.cookies['elvia_session']['secure'])
        self.assertIn('auth_error=', dict(self.callback_headers(guest, path))['Location'])

    def callback_headers(self, client, path):
        client.call('GET', path)
        return client.last_headers

    def local_call_callback(self, path):
        return self.callback_headers(self.local, path)

    def test_private_recovery_origin_binding_single_use_and_session_revocation(self):
        account = self.register()
        with connect(self.server.db_path) as db:
            db.execute('UPDATE abuse_mail_reservations SET created=created-61')
        status, result = self.private.call('POST', '/api/auth/password-reset/request', {'email': 'member@example.edu'})
        self.assertEqual(status, 202, result)
        deadline = time.monotonic()+3
        while time.monotonic() < deadline:
            with connect(self.server.db_path) as db:
                sent = db.execute('SELECT COUNT(*) FROM password_reset_tokens WHERE sent=1').fetchone()[0]
            if sent and self.reset_messages:
                break
            time.sleep(.01)
        self.assertTrue(self.reset_messages)
        url = urlsplit(self.reset_messages[0][1])
        self.assertEqual(url.scheme+'://'+url.netloc, PRIVATE)
        self.assertEqual(parse_qs(url.query), {'view': ['reset-password']})
        token = parse_qs(url.fragment)['token'][0]
        body = {'token': token, 'newpassword': PASSWORD+' replacement'}
        self.assertEqual(self.local.call('POST', '/api/auth/password-reset/complete', body)[0], 400)
        self.assertEqual(self.private.call('POST', '/api/auth/password-reset/complete', body)[0], 200)
        self.assertTrue(self.private.cookies['elvia_session']['secure'])
        self.assertEqual(self.private.call('POST', '/api/auth/password-reset/complete', body)[0], 400)
        self.assertIsNone(self.private.call('GET', '/api/session')[1]['user'])
        with connect(self.server.db_path) as db:
            self.assertEqual(db.execute('SELECT role FROM users WHERE id=?', (account,)).fetchone()[0], 'reviewer')
            self.assertEqual(db.execute('SELECT COUNT(*) FROM sessions WHERE user_id=?', (account,)).fetchone()[0], 0)
            self.assertNotIn(token, json.dumps([tuple(row) for row in db.execute('SELECT * FROM password_reset_tokens')]))

    def test_contributors_cannot_link_google_and_unknown_google_never_creates_accounts(self):
        self.configure_google()
        self.register()
        self.assertEqual(self.private.call('POST', '/api/auth/google/start', {'mode': 'link', 'password': PASSWORD})[0], 403)
        guest = WireClient(self.server, PRIVATE)
        status, result = guest.call('POST', '/api/auth/google/start', {'accept_terms': True})
        self.assertEqual(status, 200, result)
        state = parse_qs(urlsplit(result['authorization_url']).query)['state'][0]
        with connect(self.server.db_path) as db:
            before = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        guest.call('GET', CALLBACK+'?state='+state+'&code=synthetic')
        self.assertIn('auth_error=', dict(guest.last_headers)['Location'])
        self.assertIsNone(guest.call('GET', '/api/session')[1]['user'])
        with connect(self.server.db_path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM users').fetchone()[0], before)

    def test_private_admin_explicit_link_and_new_google_login_preserve_admin(self):
        self.configure_google()
        account = self.register()
        with connect(self.server.db_path) as db:
            # Fixture-only role assignment; no real admin is created by QA.
            db.execute("UPDATE users SET role='admin' WHERE id=?", (account,))
        for headers, password in [({'X-CSRF-Token': 'wrong'}, PASSWORD), ({}, 'incorrect')]:
            self.assertEqual(self.private.call('POST', '/api/auth/google/start', {
                'mode': 'link', 'password': password}, headers)[0], 403)
        status, result = self.private.call('POST', '/api/auth/google/start', {'mode': 'link', 'password': PASSWORD})
        self.assertEqual(status, 200, result)
        state = parse_qs(urlsplit(result['authorization_url']).query)['state'][0]
        self.private.call('GET', CALLBACK+'?state='+state+'&code=synthetic')
        self.assertEqual(dict(self.private.last_headers)['Location'], '/contribute.html?view=account')
        self.assertTrue(self.private.call('GET', '/api/me')[1]['google_linked'])
        guest = WireClient(self.server, PRIVATE)
        status, result = guest.call('POST', '/api/auth/google/start', {'accept_terms': True})
        self.assertEqual(status, 200, result)
        state = parse_qs(urlsplit(result['authorization_url']).query)['state'][0]
        guest.call('GET', CALLBACK+'?state='+state+'&code=synthetic')
        self.assertEqual(dict(guest.last_headers)['Location'], '/contribute.html?view=my-work')
        user = guest.call('GET', '/api/session')[1]['user']
        self.assertEqual((user['id'], user['role']), (account, 'admin'))
        self.assertEqual(guest.call('GET', '/api/admin/email-settings')[0], 403)

    def test_old_unbound_reset_links_expire_without_schema_or_account_changes(self):
        account = self.register()
        token = 'a'*43
        digest = hmac.new(self.server.mailer.key, ('password-reset-token:'+token).encode(), hashlib.sha256).hexdigest()
        with connect(self.server.db_path) as db:
            db.execute('INSERT INTO password_reset_tokens VALUES(?,?,?,?,?,?,0,1)',
                       (digest, account, 'member@example.edu', 'legacy-binding', time.time(), time.time()+900))
            before = tuple(db.execute('SELECT password,role FROM users WHERE id=?', (account,)).fetchone())
            tables = db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchone()[0]
        for client in (self.private, self.local):
            self.assertEqual(client.call('POST', '/api/auth/password-reset/complete', {
                'token': token, 'newpassword': PASSWORD+' replacement'})[0], 400)
        with connect(self.server.db_path) as db:
            self.assertEqual(tuple(db.execute('SELECT password,role FROM users WHERE id=?', (account,)).fetchone()), before)
            self.assertEqual(tables, 31)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name IN ('abuse_requests','abuse_mail_reservations')").fetchone()[0],2)

    def test_private_origin_must_be_explicitly_enabled(self):
        with tempfile.TemporaryDirectory() as folder:
            server = make_server(Path(folder), bootstrap_password=PASSWORD)
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                self.assertEqual(WireClient(server, PRIVATE).call('GET', '/api/session')[0], 403)
                local = WireClient(server, f'http://127.0.0.1:{server.server_port}')
                self.assertEqual(local.call('POST', '/api/auth/login', {'login': 'minhao', 'password': PASSWORD})[0], 200)
                self.assertFalse(local.cookies['elvia_session']['secure'])
            finally:
                server.shutdown();server.server_close();worker.join()


class PrivateOriginConfiguration(unittest.TestCase):
    def test_invalid_private_origin_is_rejected_before_creating_runtime_files(self):
        for value in ['http://elvia-atlas.org', PRIVATE+'/', PRIVATE+':443',
                      'https://other.example.org', 'https://user@elvia-atlas.org',
                      'https://elvia-private.minhaoliu.com', True]:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as folder:
                target = Path(folder)/'not-created'
                with self.assertRaises(ValueError):
                    make_server(target, bootstrap_password=PASSWORD, private_origin=value)
                self.assertFalse(target.exists())

    def test_oauth_private_metadata_requires_opt_in_and_does_not_enter_token_request(self):
        oauth = {'client_id': 'synthetic.apps.googleusercontent.com', 'client_secret': 'synthetic-secret',
                 'redirect_uris': ['http://127.0.0.1:8998'+CALLBACK, PRIVATE+CALLBACK]}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path/'google-oauth.json').write_text(json.dumps(oauth), 'utf-8')
            local_only = GoogleLogin(path, 8998)
            self.assertFalse(local_only.public(PRIVATE)['enabled'])
            google = GoogleLogin(path, 8998, private_origin=PRIVATE)
            self.assertTrue(google.public(PRIVATE)['enabled'])
            with patch('requests.Session') as transport, patch('google.oauth2.id_token.verify_oauth2_token') as verify:
                transport.return_value.post.return_value.status_code = 200
                transport.return_value.post.return_value.json.return_value = {'id_token': 'synthetic'}
                verify.return_value = {'nonce': 'expected', 'sub': 'synthetic-sub', 'email_verified': True,
                                       'email': 'owner@example.org'}
                google.exchange('synthetic-code', {'verifier': 'synthetic-verifier', 'nonce': 'expected', 'origin': PRIVATE})
                sent = transport.return_value.post.call_args.kwargs['data']
                self.assertEqual(sent['redirect_uri'], PRIVATE+CALLBACK)
                self.assertNotIn('redirect_uris', sent)
                self.assertNotIn('origin', sent)
                with self.assertRaises(GoogleLoginError):
                    google.exchange('synthetic-code', {'verifier': 'synthetic-verifier', 'nonce': 'expected', 'origin': 'https://evil.example.org'})


if __name__ == '__main__':
    unittest.main()
