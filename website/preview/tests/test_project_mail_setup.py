"""Project sender imports and failures use private synthetic directories and mock SMTP."""
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('project_mail_setup', ROOT/'scripts/configure_project_mail.py')
setup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(setup)


class ProjectMailSetup(unittest.TestCase):
    def setUp(self):
        sandbox = ROOT/'private-test-data'
        sandbox.mkdir(exist_ok=True)
        self.folder = Path(tempfile.mkdtemp(prefix='project-mail-', dir=sandbox))
        self.data = self.folder/'state'
        self.data.mkdir()
        self.source = self.folder/'provider.json'
        self.secret = 'synthetic-project-token-never-print'
        self.source.write_text(json.dumps({'api_token': self.secret}), 'utf-8')
        self.key = self.data/'email-verification.key'
        self.key.write_bytes(b'unchanged-synthetic-key')
        self.google = self.data/'google-oauth.json'
        self.google.write_bytes(b'unchanged-synthetic-google-config')

    def tearDown(self):
        shutil.rmtree(self.folder)

    def test_fixed_cloudflare_profile_preserves_domains_key_google_and_is_idempotent(self):
        old = setup.EmailAccess.validate_config({'host': 'smtp.gmail.com', 'port': 465,
                  'security': 'ssl', 'sender': 'owner@gmail.com', 'username': 'owner@gmail.com',
                  'password': 'old-synthetic', 'research_domains': ['institute.org']})
        path = self.data/'email-settings.json'
        path.write_text(json.dumps(old), 'utf-8')
        before = {member.name: member.read_bytes() for member in (self.key, self.google)}
        with patch.object(setup, 'authenticate_smtp') as smtp:
            self.assertTrue(setup.configure(self.data, 'cloudflare', source=self.source, replace=True))
            smtp.assert_not_called()
        saved = json.loads(path.read_text('utf-8'))
        self.assertEqual((saved['host'], saved['port'], saved['security']),
                         ('smtp.mx.cloudflare.net', 465, 'ssl'))
        self.assertEqual(saved['username'], 'api_token')
        self.assertEqual(saved['password'], self.secret)
        self.assertEqual(saved['sender'], 'accounts@elvia-atlas.org')
        self.assertEqual(saved['reply_to'], 'contact@elvia-atlas.org')
        self.assertEqual(saved['sender_name'], 'ELVIA Accounts')
        self.assertEqual(saved['research_domains'], ['institute.org'])
        self.assertFalse(setup.configure(self.data, 'cloudflare', source=self.source))
        self.assertEqual({member.name: member.read_bytes() for member in (self.key, self.google)}, before)

    def test_new_profile_refuses_unapproved_overwrite_and_check_authenticates_without_delivery(self):
        setup.configure(self.data, 'cloudflare', source=self.source)
        path = self.data/'email-settings.json'
        first = path.read_bytes()
        self.source.write_text(json.dumps({'api_token': 'different-synthetic-token'}), 'utf-8')
        with self.assertRaises(ValueError):
            setup.configure(self.data, 'cloudflare', source=self.source)
        self.assertEqual(path.read_bytes(), first)
        with patch.object(setup, 'authenticate_smtp') as smtp:
            self.assertTrue(setup.configure(self.data, 'cloudflare', source=self.source,
                                            replace=True, check_smtp=True))
            smtp.assert_called_once()

    def test_brevo_profile_uses_supplied_smtp_user_and_ssl_key_without_space_normalizing(self):
        self.source.write_text(json.dumps({'username': 'synthetic-user@smtp-brevo.com',
                                          'password': ' keep synthetic spaces '}), 'utf-8')
        setup.configure(self.data, 'brevo', source=self.source)
        saved = json.loads((self.data/'email-settings.json').read_text('utf-8'))
        self.assertEqual((saved['host'], saved['port'], saved['security']),
                         ('smtp-relay.brevo.com', 465, 'ssl'))
        self.assertEqual(saved['password'], ' keep synthetic spaces ')
        self.assertEqual(saved['username'], 'synthetic-user@smtp-brevo.com')

    def test_malformed_tokens_wrong_paths_symlinks_and_profiles_fail_before_publication(self):
        for value in (None, {}, {'api_token': []}, {'api_token': 'secret\r\nheader'},
                      {'password': 'wrong-field'}, {'api_token': self.secret, 'unknown': True}):
            self.source.write_text(json.dumps(value), 'utf-8')
            with self.subTest(value=type(value).__name__), self.assertRaises((ValueError, setup.MailError)):
                setup.configure(self.data, 'cloudflare', source=self.source)
            self.assertFalse((self.data/'email-settings.json').exists())
        with self.assertRaises(ValueError):
            setup.configure(self.data, 'unknown', password=self.secret)
        with self.assertRaises(ValueError):
            setup.configure(ROOT, 'cloudflare', password=self.secret)
        with self.assertRaises(ValueError):
            setup.read_credentials(ROOT/'README.md', 'cloudflare')
        original = Path.is_symlink
        with patch.object(Path, 'is_symlink', lambda value: value == self.source or original(value)), \
             self.assertRaises(ValueError):
            setup.read_credentials(self.source, 'cloudflare')

    def test_cli_redacts_provider_errors_and_refuses_getpass_echo_fallback(self):
        for error in (OSError(self.secret), setup.getpass.GetPassWarning()):
            output, errors = io.StringIO(), io.StringIO()
            with patch.object(setup.getpass, 'getpass', side_effect=error), \
                 redirect_stdout(output), redirect_stderr(errors):
                self.assertEqual(setup.main(['--data-dir', str(self.data)]), 1)
            self.assertNotIn(self.secret, output.getvalue()+errors.getvalue())
            self.assertFalse((self.data/'email-settings.json').exists())
        errors = io.StringIO()
        with redirect_stderr(errors), self.assertRaises(SystemExit):
            setup.main(['--data-dir', str(self.data), '--password', self.secret])
        self.assertNotIn(self.secret, errors.getvalue())

    def test_cli_success_reports_no_identity_or_credential_and_transport_failure_leaves_settings(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(setup.main(['--data-dir', str(self.data), '--source', str(self.source)]), 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report, {'smtp_configured': True, 'profile': 'cloudflare',
                                 'changed': True, 'authenticated': False, 'email_sent': False})
        self.assertNotIn(self.secret, output.getvalue())
        path = self.data/'email-settings.json'
        before = path.read_bytes()
        self.source.write_text(json.dumps({'api_token': 'different-synthetic-token'}), 'utf-8')
        with patch.object(setup, 'authenticate_smtp', side_effect=OSError(self.secret)), \
             self.assertRaises(OSError):
            setup.configure(self.data, 'cloudflare', source=self.source, replace=True, check_smtp=True)
        self.assertEqual(path.read_bytes(), before)

    def test_source_acl_guard_runs_before_any_credential_json_read(self):
        with patch.object(setup, 'private_acl') as protect, \
             patch.object(setup, 'verify_private_source', create=True,
                          side_effect=ValueError('unsafe synthetic source ACL')) as verify, \
             patch.object(setup, 'read_json') as read:
            with self.assertRaises(ValueError):
                setup.read_credentials(self.source, 'cloudflare')
            protect.assert_called_once_with(self.source)
            verify.assert_called_once_with(self.source)
            read.assert_not_called()

    @unittest.skipUnless(os.name == 'nt', 'Windows explicit ACL contract')
    def test_existing_explicit_users_grant_is_rejected_before_read(self):
        subprocess.run(['icacls', str(self.source), '/grant', '*S-1-5-32-545:R'],
                       check=True, capture_output=True)
        with patch.object(setup, 'read_json') as read, self.assertRaises(ValueError):
            setup.read_credentials(self.source, 'cloudflare')
        read.assert_not_called()

    def test_hardlinked_credential_source_is_rejected_before_acl_mutation_or_read(self):
        linked = self.folder/'hardlinked-provider.json'
        os.link(self.source, linked)
        with patch.object(setup, 'private_acl') as protect, \
             patch.object(setup, 'read_json') as read, self.assertRaises(ValueError):
            setup.read_credentials(linked, 'cloudflare')
        protect.assert_not_called()
        read.assert_not_called()


if __name__ == '__main__':
    unittest.main()
