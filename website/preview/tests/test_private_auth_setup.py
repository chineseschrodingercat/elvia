"""Private setup exercises use only synthetic state and mock SMTP."""
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
SPEC = importlib.util.spec_from_file_location('private_auth_setup', ROOT / 'scripts/configure_private_auth.py')
setup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(setup)


class PrivateAuthSetupTests(unittest.TestCase):
    def setUp(self):
        sandbox = ROOT / 'private-test-data'
        sandbox.mkdir(exist_ok=True)
        self.folder = Path(tempfile.mkdtemp(prefix='setup-fixture-', dir=sandbox))
        self.data = self.folder / 'state'
        self.data.mkdir()
        self.source = self.folder / 'client.json'
        self.secret = 'synthetic-only-secret-never-print'
        self.raw = {'web': {'client_id': '123.synthetic.apps.googleusercontent.com',
                            'client_secret': self.secret,
                            'redirect_uris': ['http://127.0.0.1:8797/api/auth/google/callback']}}
        self.source.write_text(json.dumps(self.raw), encoding='utf-8')

    def tearDown(self):
        for path in self.folder.rglob('*'):
            if not path.is_symlink():
                try:
                    path.chmod(0o700 if path.is_dir() else 0o600)
                except OSError:
                    pass
        shutil.rmtree(self.folder)

    def test_status_is_readonly_and_never_creates_key(self):
        before = list(self.data.iterdir())
        self.assertEqual(setup.status(self.data, 8797), {
            'smtp': {'present': False, 'enabled': False},
            'google': {'present': False, 'enabled': False}})
        self.assertEqual(list(self.data.iterdir()), before)

    def test_google_standard_web_import_idempotence_and_no_overwrite(self):
        self.assertTrue(setup.import_google(self.source, self.data, 8797))
        destination = self.data / 'google-oauth.json'
        first = destination.read_bytes()
        self.assertFalse(setup.import_google(self.source, self.data, 8797))
        self.assertEqual(destination.read_bytes(), first)
        self.raw['web']['client_secret'] = 'other-synthetic-secret'
        self.source.write_text(json.dumps(self.raw), encoding='utf-8')
        with self.assertRaises(ValueError):
            setup.import_google(self.source, self.data, 8797)
        self.assertEqual(destination.read_bytes(), first)
        self.assertTrue(setup.import_google(self.source, self.data, 8797, replace=True))

    def test_import_rejects_installed_and_wrong_callback_before_any_write(self):
        for raw in ({'installed': self.raw['web']}, self.raw['web'],
                    {'web': {**self.raw['web'], 'redirect_uris': ['https://example.org/callback']}}):
            with self.subTest(raw=raw):
                self.source.write_text(json.dumps(raw), encoding='utf-8')
                with self.assertRaises((ValueError, setup.GoogleLoginError)):
                    setup.import_google(self.source, self.data, 8797)
                self.assertEqual(list(self.data.iterdir()), [])

    def test_only_approved_existing_data_directories(self):
        self.assertEqual(setup.checked_data_dir(self.data), self.data)
        for path in (ROOT, ROOT / 'formal-copy', ROOT / 'private-test-data',
                     ROOT / 'private-test-data' / '..' / 'other-state',
                     Path('D:/ELVIA'), self.folder / 'missing'):
            with self.subTest(path=path), self.assertRaises((ValueError, OSError)):
                setup.checked_data_dir(path)

    def test_symlink_sources_or_targets_and_parent_links_are_rejected(self):
        linked = self.folder / 'linked-state'
        if os.name == 'nt':
            subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(linked), str(self.data)],
                           check=True, capture_output=True)
        else:
            linked.symlink_to(self.data, target_is_directory=True)
        with self.assertRaises(ValueError):
            setup.checked_data_dir(linked)
        with self.assertRaises(ValueError):
            setup.checked_data_dir(linked / 'nested')
        if os.name == 'nt':
            linked.rmdir()
        else:
            linked.unlink()
        config = self.data / 'google-oauth.json'
        original = Path.is_symlink
        with patch.object(Path, 'is_symlink', lambda path: path == config or original(path)), \
             self.assertRaises(ValueError):
            setup.import_google(self.source, self.data, 8797, replace=True)
        source_link = self.folder / 'linked-client.json'
        with patch.object(Path, 'is_symlink', lambda path: path == source_link or original(path)), \
             self.assertRaises(ValueError):
            setup.import_google(source_link, self.data, 8797)

    def test_gmail_uses_existing_validator_and_save_without_sending(self):
        with self.assertRaises(ValueError):
            setup.smtp_gmail(self.data, 'owner@example.com', self.secret)
        with patch.object(setup.smtplib, 'SMTP_SSL') as smtp:
            self.assertTrue(setup.smtp_gmail(self.data, 'owner@gmail.com', self.secret))
            smtp.assert_not_called()
        config = json.loads((self.data / 'email-settings.json').read_text('utf-8'))
        self.assertEqual(config['host'], 'smtp.gmail.com')
        self.assertEqual((config['port'], config['security']), (465, 'ssl'))
        self.assertEqual(config['password'], self.secret)
        self.assertFalse((self.data / 'email-verification.key').exists())

    def test_smtp_explicit_check_authenticates_and_quits_without_send(self):
        with patch.object(setup.smtplib, 'SMTP_SSL') as smtp:
            connection = smtp.return_value
            self.assertTrue(setup.smtp_gmail(self.data, 'owner@gmail.com', self.secret, check_smtp=True))
        connection.login.assert_called_once_with('owner@gmail.com', self.secret)
        connection.quit.assert_called_once_with()
        connection.send_message.assert_not_called()
        connection.sendmail.assert_not_called()

    def test_only_gmail_display_spaces_are_removed(self):
        with patch.object(setup.smtplib, 'SMTP_SSL') as smtp:
            setup.smtp_gmail(self.data, 'owner@gmail.com', 'abcd efgh ijkl mnop', check_smtp=True)
        smtp.return_value.login.assert_called_once_with('owner@gmail.com', 'abcdefghijklmnop')
        config = json.loads((self.data / 'email-settings.json').read_text('utf-8'))
        self.assertEqual(config['password'], 'abcdefghijklmnop')
        normal = setup.EmailAccess.validate_config({**config, 'password': ' keep these spaces '})
        self.assertEqual(normal['password'], ' keep these spaces ')

    def test_smtp_failure_does_not_publish_or_print_provider_error(self):
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(setup.getpass, 'getpass', return_value=self.secret), \
             patch.object(setup.smtplib, 'SMTP_SSL', side_effect=OSError(self.secret)), \
             redirect_stdout(output), redirect_stderr(errors):
            result = setup.main(['smtp-gmail', '--data-dir', str(self.data),
                                 '--sender', 'owner@gmail.com', '--check-smtp'])
        self.assertEqual(result, 1)
        self.assertNotIn(self.secret, output.getvalue() + errors.getvalue())
        self.assertNotIn('owner@gmail.com', output.getvalue() + errors.getvalue())
        self.assertEqual(list(self.data.iterdir()), [])

    def test_status_output_contains_only_presence_and_enabled(self):
        setup.import_google(self.source, self.data, 8797)
        setup.smtp_gmail(self.data, 'owner@gmail.com', self.secret)
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(setup.main(['status', '--data-dir', str(self.data)]), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result, {'smtp': {'present': True, 'enabled': True},
                                  'google': {'present': True, 'enabled': True}})
        self.assertNotIn(self.secret, output.getvalue())
        self.assertNotIn('owner@gmail.com', output.getvalue())

    def test_cli_never_echoes_unknown_credential_arguments(self):
        errors = io.StringIO()
        with redirect_stderr(errors), self.assertRaises(SystemExit):
            setup.main(['smtp-gmail', '--data-dir', str(self.data), '--sender', 'owner@gmail.com',
                        '--password', self.secret])
        self.assertNotIn(self.secret, errors.getvalue())
        self.assertNotIn('owner@gmail.com', errors.getvalue())

    def test_smtp_idempotence_refusal_and_preserved_research_domains(self):
        setup.smtp_gmail(self.data, 'owner@gmail.com', self.secret)
        config_path = self.data / 'email-settings.json'
        config = json.loads(config_path.read_text('utf-8'))
        config['research_domains'] = ['research.example.org']
        config_path.write_text(json.dumps(config), encoding='utf-8')
        first = config_path.read_bytes()
        self.assertFalse(setup.smtp_gmail(self.data, 'owner@gmail.com', self.secret))
        with self.assertRaises(ValueError):
            setup.smtp_gmail(self.data, 'owner@gmail.com', 'different synthetic password')
        self.assertEqual(config_path.read_bytes(), first)
        self.assertTrue(setup.smtp_gmail(self.data, 'owner@gmail.com', 'different synthetic password', replace=True))
        self.assertEqual(json.loads(config_path.read_text('utf-8'))['research_domains'], ['research.example.org'])

    def test_exclusive_publication_does_not_overwrite_a_racing_writer(self):
        destination = self.data / 'google-oauth.json'
        def racing_writer(source, target):
            destination.write_text('synthetic concurrent state', encoding='utf-8')
            raise FileExistsError()
        with patch.object(setup.os, 'link', side_effect=racing_writer), self.assertRaises(FileExistsError):
            setup.import_google(self.source, self.data, 8797)
        self.assertEqual(destination.read_text('utf-8'), 'synthetic concurrent state')
        self.assertEqual([path.name for path in self.data.iterdir()], ['google-oauth.json'])

    def test_getpass_echo_fallback_is_rejected(self):
        errors = io.StringIO()
        with patch.object(setup.getpass, 'getpass', side_effect=setup.getpass.GetPassWarning()), \
             redirect_stderr(errors):
            self.assertEqual(setup.main(['smtp-gmail', '--data-dir', str(self.data),
                                         '--sender', 'owner@gmail.com']), 1)
        self.assertEqual(list(self.data.iterdir()), [])
        self.assertNotIn('owner@gmail.com', errors.getvalue())


if __name__ == '__main__':
    unittest.main()
