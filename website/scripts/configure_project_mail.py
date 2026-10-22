"""Privately import the approved ELVIA project SMTP sender; never send a test email.

Secrets enter only through a hidden prompt or an explicitly selected local JSON
under Downloads, this release's private-connection, or its synthetic test scope.
Cloudflare JSON: {"api_token": "..."}. Brevo JSON: {"username": "...", "password": "..."}.
Provider enablement, domain verification, any billing and live authentication are
separate operator decisions. --check-smtp authenticates only when explicitly used.
"""
from __future__ import annotations

import getpass
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import warnings

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'preview/server'), str(ROOT/'scripts')]
from configure_private_auth import (PrivateParser, authenticate_smtp, checked_data_dir,
                                    plain_path, private_acl, publish, read_json)
from email_access import EmailAccess, MailError

PROFILES = {'cloudflare': ('smtp.mx.cloudflare.net', 'api_token'),
            'brevo': ('smtp-relay.brevo.com', None)}


def verify_private_source(path):
    """Refuse residual explicit grants before opening any credential content."""
    if os.name != 'nt':
        info = path.stat()
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
            raise ValueError('The selected credential file is not private to this user.')
        return
    shell = shutil.which('pwsh.exe') or str(Path(os.environ['SystemRoot'])/
                'System32/WindowsPowerShell/v1.0/powershell.exe')
    script = r'''
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
try {
    $acl = Get-Acl -LiteralPath $env:ELVIA_PROJECT_MAIL_CREDENTIAL_SOURCE
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    $allowed = @($sid, 'S-1-5-18')
    $owner = $acl.GetOwner([Security.Principal.SecurityIdentifier]).Value
    if ($owner -notin $allowed -or -not $acl.AreAccessRulesProtected) { exit 1 }
    $rules = @($acl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier]))
    if ($rules.Count -ne 2) { exit 1 }
    $seen = @()
    foreach ($rule in $rules) {
        $principal = $rule.IdentityReference.Value
        if ($principal -notin $allowed -or $principal -in $seen -or $rule.IsInherited -or
            $rule.AccessControlType -ne [Security.AccessControl.AccessControlType]::Allow -or
            $rule.FileSystemRights -ne [Security.AccessControl.FileSystemRights]::FullControl) { exit 1 }
        $seen += $principal
    }
    Write-Output 'ELVIA_PRIVATE_SOURCE_OK'
} catch { exit 1 }
'''
    environment = os.environ.copy()
    environment['ELVIA_PROJECT_MAIL_CREDENTIAL_SOURCE'] = str(path)
    result = subprocess.run([shell, '-NoLogo', '-NoProfile', '-NonInteractive',
                             '-Command', script], env=environment, capture_output=True,
                            text=True, timeout=20)
    if result.returncode != 0 or result.stdout.strip() != 'ELVIA_PRIVATE_SOURCE_OK':
        raise ValueError('The selected credential file ACL must allow only this user and SYSTEM.')


def read_credentials(source, profile):
    if profile not in PROFILES:
        raise ValueError('Use an approved project SMTP profile.')
    source = plain_path(source)
    scopes = (plain_path(Path.home()/'Downloads'), plain_path(ROOT/'private-connection'),
              plain_path(ROOT/'private-test-data'))
    if not any(scope in source.parents for scope in scopes):
        raise ValueError('Use the selected downloaded or release-private credential file.')
    info = source.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > 65536:
        raise ValueError('Use a small regular local credential JSON file without hard links.')
    private_acl(source)
    verify_private_source(source)
    value = read_json(source)
    expected = {'api_token'} if profile == 'cloudflare' else {'username', 'password'}
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError('Use the documented provider credential object.')
    if profile == 'cloudflare':
        return 'api_token', value['api_token']
    return value['username'], value['password']


def configure(data_dir, profile, *, source=None, password=None, username=None,
              replace=False, check_smtp=False):
    if profile not in PROFILES:
        raise ValueError('Use an approved project SMTP profile.')
    data = checked_data_dir(data_dir)
    if source is not None:
        if password is not None or username is not None:
            raise ValueError('Select exactly one private credential input.')
        username, password = read_credentials(source, profile)
    elif profile == 'cloudflare':
        username = 'api_token'
    existing = plain_path(data/'email-settings.json')
    current = EmailAccess.validate_config(read_json(existing)) if existing.exists() else None
    config = EmailAccess.validate_config({'host': PROFILES[profile][0], 'port': 465,
               'security': 'ssl', 'sender': 'accounts@elvia-atlas.org',
               'sender_name': 'ELVIA Accounts', 'reply_to': 'contact@elvia-atlas.org',
               'username': username, 'password': password,
               'research_domains': current['research_domains'] if current else []})
    if current is not None and current != config and not replace:
        raise ValueError('Different settings exist; review and explicitly replace them.')
    if check_smtp:
        authenticate_smtp(config)
    return publish(data, 'email-settings.json', config, EmailAccess.validate_config,
                   replace, smtp=True)


def main(argv=None):
    parser = PrivateParser(description=__doc__)
    parser.add_argument('--data-dir', required=True)
    parser.add_argument('--profile', choices=tuple(PROFILES), default='cloudflare')
    parser.add_argument('--source', help='Selected local JSON; never include credentials as arguments')
    parser.add_argument('--replace', action='store_true')
    parser.add_argument('--check-smtp', action='store_true',
                        help='Explicitly authenticate over verified TLS and quit without sending email')
    args = parser.parse_args(argv)
    try:
        checked_data_dir(args.data_dir)
        inputs = {'source': args.source} if args.source else {}
        if not args.source:
            if args.profile == 'brevo':
                inputs['username'] = input('Approved Brevo SMTP username: ')
            with warnings.catch_warnings():
                warnings.simplefilter('error', getpass.GetPassWarning)
                inputs['password'] = getpass.getpass('Project SMTP credential (hidden; never paste into chat): ')
        changed = configure(args.data_dir, args.profile, **inputs,
                            replace=args.replace, check_smtp=args.check_smtp)
        print(json.dumps({'smtp_configured': True, 'profile': args.profile, 'changed': changed,
                          'authenticated': args.check_smtp, 'email_sent': False}))
        return 0
    except (Exception, KeyboardInterrupt):
        print('Project mail setup failed. Review the approved private input, provider readiness and permissions; no credential values are shown.',
              file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
