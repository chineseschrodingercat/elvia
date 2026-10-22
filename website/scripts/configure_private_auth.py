"""Configure ELVIA's private local providers without printing credentials.

Run in the repository's locked Python environment. Passwords are accepted only by
the hidden terminal prompt; downloaded OAuth JSON is read from an explicit path.
"""
from __future__ import annotations

import argparse
import csv
import getpass
import json
import os
from pathlib import Path
import smtplib
import ssl
import stat
import subprocess
import sys
import tempfile
import warnings

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_DATA = ROOT.parent.parent / 'ELVIA-runtime' / 'production' / 'data'
TEST_DATA = ROOT / 'private-test-data'
sys.path.insert(0, str(ROOT / 'preview' / 'server'))
from email_access import EmailAccess, normalize_email  # noqa: E402
from google_login import GoogleLogin, GoogleLoginError  # noqa: E402


def plain_path(value):
    path = Path(os.path.abspath(value))
    if path.drive.startswith('\\\\'):
        raise ValueError('Use a local filesystem path.')
    for item in (path, *path.parents):
        if item.is_symlink() or (hasattr(item, 'is_junction') and item.is_junction()):
            raise ValueError('Linked paths are unsupported.')
        try:
            info = item.lstat()
        except FileNotFoundError:
            continue
        if getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError('Reparse paths are unsupported.')
    return path.resolve()


def checked_data_dir(value):
    path = plain_path(value)
    if path != ORIGINAL_DATA and TEST_DATA not in path.parents:
        raise ValueError('Data directory is outside this local release scope.')
    if not path.is_dir():
        raise ValueError('Initialize the approved data directory first.')
    return path


def read_json(path):
    path = plain_path(path)
    if not path.is_file() or path.stat().st_size > 65536:
        raise ValueError('Use a small local provider JSON file.')
    return json.loads(path.read_text(encoding='utf-8-sig'))


def private_acl(path, *, directory=False):
    if os.name == 'nt':
        result = subprocess.run(['whoami', '/user', '/fo', 'csv', '/nh'],
                                check=True, capture_output=True, text=True)
        sid = next(csv.reader([result.stdout.strip()]))[1]
        inherit = '(OI)(CI)' if directory else ''
        subprocess.run(['icacls', str(path), '/inheritance:r', '/grant:r',
                        f'*{sid}:{inherit}F', f'*S-1-5-18:{inherit}F'],
                       check=True, capture_output=True)
    else:
        path.chmod(0o700 if directory else 0o600)


def status(data_dir, port):
    data = checked_data_dir(data_dir)
    result = {}
    for provider, filename, validate in (
            ('smtp', 'email-settings.json', EmailAccess.validate_config),
            ('google', 'google-oauth.json', lambda value: GoogleLogin.validate_config(value, port))):
        path = plain_path(data / filename)
        present, enabled = path.is_file(), False
        if present:
            try:
                enabled = bool(validate(read_json(path)))
            except Exception:
                pass
        result[provider] = {'present': present, 'enabled': enabled}
    return result


def publish(data, filename, config, validate, replace, *, smtp=False):
    destination = plain_path(data / filename)
    if destination.exists():
        try:
            if validate(read_json(destination)) == config:
                return False
        except Exception:
            pass
        if not replace:
            raise ValueError('Different configuration already exists; review it locally before --replace.')
    staging = Path(tempfile.mkdtemp(prefix='.auth-setup-', dir=data))
    try:
        private_acl(staging, directory=True)
        temporary = staging / filename
        if smtp:
            EmailAccess(staging).save(config)
        else:
            temporary.write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')
        private_acl(temporary)
        plain_path(destination)
        if replace:
            os.replace(temporary, destination)
        else:
            os.link(temporary, destination)  # Atomic exclusive publication; a racing writer wins safely.
        return True
    finally:
        for member in staging.iterdir():
            member.unlink()
        staging.rmdir()


def import_google(source, data_dir, port, *, replace=False):
    data = checked_data_dir(data_dir)
    raw = read_json(source)
    if not isinstance(raw, dict) or not isinstance(raw.get('web'), dict):
        raise ValueError('Import the downloaded Web application OAuth JSON.')
    config = GoogleLogin.validate_config(raw, port)
    return publish(data, 'google-oauth.json', config,
                   lambda value: GoogleLogin.validate_config(value, port), replace)


def authenticate_smtp(config):
    connection = smtplib.SMTP_SSL(config['host'], config['port'], timeout=10,
                                 context=ssl.create_default_context())
    try:
        connection.login(config['username'], config['password'])
    finally:
        connection.quit()


def smtp_gmail(data_dir, sender, password, *, replace=False, check_smtp=False):
    data = checked_data_dir(data_dir)
    sender = normalize_email(sender)
    if not sender or sender.rsplit('@', 1)[1] not in ('gmail.com', 'googlemail.com'):
        raise ValueError('Use the owner Gmail sending account.')
    if not isinstance(password, str):
        raise ValueError('Enter the Gmail app password in the private prompt.')
    password = password.replace(' ', '')  # Google displays app passwords in space-separated groups.
    existing = plain_path(data / 'email-settings.json')
    domains = read_json(existing).get('research_domains', []) if existing.exists() else []
    config = EmailAccess.validate_config({'host': 'smtp.gmail.com', 'port': 465,
        'security': 'ssl', 'sender': sender, 'username': sender, 'password': password,
        'research_domains': domains})
    if check_smtp:
        authenticate_smtp(config)
    return publish(data, 'email-settings.json', config, EmailAccess.validate_config, replace, smtp=True)


class PrivateParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, 'Invalid options. Use --help; credentials belong only in the private prompt or local file.\n')


def main(argv=None):
    parser = PrivateParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True, parser_class=PrivateParser)
    for name in ('status', 'import-google', 'smtp-gmail'):
        command = commands.add_parser(name)
        command.add_argument('--data-dir', required=True)
        command.add_argument('--port', type=int, default=8797)
        if name != 'status':
            command.add_argument('--replace', action='store_true', help='Intentionally replace different saved settings')
        if name == 'import-google':
            command.add_argument('--source', required=True)
        if name == 'smtp-gmail':
            command.add_argument('--sender', required=True)
            command.add_argument('--password-via', choices=('getpass',), default='getpass',
                                 help='Read the app password only through a hidden terminal prompt')
            command.add_argument('--check-smtp', action='store_true',
                                 help='Authenticate over TLS and quit; send no email')
    args = parser.parse_args(argv)
    try:
        checked_data_dir(args.data_dir)
        if args.command == 'status':
            result = status(args.data_dir, args.port)
        elif args.command == 'import-google':
            changed = import_google(args.source, args.data_dir, args.port, replace=args.replace)
            result = {'google': {'present': True, 'enabled': True}, 'changed': changed}
        else:
            with warnings.catch_warnings():
                warnings.simplefilter('error', getpass.GetPassWarning)
                password = getpass.getpass('Gmail app password (hidden; never paste into chat): ')
            changed = smtp_gmail(args.data_dir, args.sender, password,
                                 replace=args.replace, check_smtp=args.check_smtp)
            result = {'smtp': {'present': True, 'enabled': True}, 'changed': changed}
        print(json.dumps(result))
        return 0
    except (Exception, KeyboardInterrupt):
        print('Setup failed. Review the approved local paths, provider settings and permissions; no credentials are printed.',
              file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
