"""Project-mail headers, safe content and configuration use synthetic SMTP only."""
from email.utils import parsedate_to_datetime
import json
from pathlib import Path
import ssl
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
from email_access import EmailAccess, MailError


SMTP = {'host': 'smtp.example.org', 'port': 465, 'security': 'ssl',
        'sender': 'accounts@elvia-atlas.org', 'sender_name': 'ELVIA Accounts',
        'reply_to': 'contact@elvia-atlas.org', 'username': 'synthetic',
        'password': 'synthetic-project-secret', 'research_domains': ['institute.org']}


class ProjectMail(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.mail = EmailAccess(Path(self.folder.name))
        self.mail.config = EmailAccess.validate_config(SMTP)

    def test_both_messages_have_project_headers_tls_exact_envelope_and_unique_ids(self):
        reset = 'https://elvia-atlas.org/?view=reset-password#token=synthetic-only'
        with patch('email_access.smtplib.SMTP_SSL') as transport:
            self.mail.send_code('recipient@example.edu', '123456')
            self.mail.send_password_reset('recipient@example.edu', reset)
        connection = transport.return_value
        context = transport.call_args.kwargs['context']
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(context.check_hostname)
        messages = [call.args[0] for call in connection.send_message.call_args_list]
        self.assertEqual(len(messages), 2)
        self.assertNotEqual(messages[0]['Message-ID'], messages[1]['Message-ID'])
        for call, message in zip(connection.send_message.call_args_list, messages):
            self.assertEqual(call.kwargs, {'from_addr': 'accounts@elvia-atlas.org',
                                          'to_addrs': ['recipient@example.edu']})
            self.assertEqual(message['From'].addresses[0].display_name, 'ELVIA Accounts')
            self.assertEqual(message['From'].addresses[0].addr_spec, 'accounts@elvia-atlas.org')
            self.assertEqual(str(message['Reply-To']), 'contact@elvia-atlas.org')
            self.assertRegex(str(message['Message-ID']), r'^<[^<>\s]+@elvia-atlas\.org>$')
            self.assertIsNotNone(parsedate_to_datetime(str(message['Date'])).tzinfo)
            self.assertEqual(message.get_content_type(), 'multipart/alternative')
            self.assertEqual([part.get_content_type() for part in message.iter_parts()],
                             ['text/plain', 'text/html'])
            self.assertNotIn('synthetic-project-secret', message.as_string())
            self.assertNotIn('synthetic-only', json.dumps(list(message.items())))
        self.assertIn('123456', messages[0].get_body(preferencelist=('plain',)).get_content())
        self.assertIn(reset, messages[1].get_body(preferencelist=('plain',)).get_content())

    def test_html_escapes_body_values_without_tracking_or_external_assets(self):
        reset = 'https://elvia-atlas.org/?view=reset-password&test="<tag>"#token=synthetic'
        with patch('email_access.smtplib.SMTP_SSL') as transport:
            self.mail.send_password_reset('recipient@example.edu', reset)
        message = transport.return_value.send_message.call_args.args[0]
        html = message.get_body(preferencelist=('html',)).get_content()
        self.assertIn('&amp;test=&quot;&lt;tag&gt;&quot;', html)
        for forbidden in ('<img', '<script', '<iframe', 'src=', '<style', '<tag>'):
            self.assertNotIn(forbidden, html.casefold())
        self.assertIn('https://elvia-atlas.org/', html)

    def test_header_injection_invalid_metadata_and_recipients_fail_before_smtp(self):
        for field, value in [('sender_name', 'ELVIA\r\nBcc: other@example.org'),
                             ('sender_name', 'ELVIA\x00'), ('sender_name', ['ELVIA']),
                             ('sender_name', 'X'*121),
                             ('reply_to', 'contact@example.org\r\nBcc: other@example.org'),
                             ('reply_to', 'one@example.org,two@example.org'),
                             ('reply_to', ['contact@example.org'])]:
            with self.subTest(field=field), self.assertRaises(MailError):
                EmailAccess.validate_config({**SMTP, field: value})
        with patch('email_access.smtplib.SMTP_SSL') as transport:
            for recipient in ('recipient@example.edu\r\nBcc: other@example.org',
                              'one@example.edu,two@example.edu'):
                with self.assertRaises(MailError):
                    self.mail.send_code(recipient, '123456')
            transport.assert_not_called()

    def test_old_settings_defaults_optional_fields_survive_old_form_and_remain_redacted(self):
        legacy = {k: v for k, v in SMTP.items() if k not in ('sender_name', 'reply_to')}
        normalized = EmailAccess.validate_config(legacy)
        self.assertEqual(normalized['sender_name'], 'ELVIA Accounts')
        self.assertEqual(normalized['reply_to'], '')
        self.mail.save(SMTP)
        self.mail.save({**legacy, 'password': ''})
        self.assertEqual(self.mail.config['reply_to'], 'contact@elvia-atlas.org')
        self.assertEqual(self.mail.config['password'], SMTP['password'])
        self.assertNotIn(SMTP['password'], json.dumps(self.mail.settings()))
        self.assertEqual(EmailAccess(Path(self.folder.name)).config, self.mail.config)


if __name__ == '__main__':
    unittest.main()
