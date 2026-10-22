"""Authenticated client-IP context between the verified gateway and local app.

No identity is inferred from an unsigned forwarded header. Keys are explicit,
read-only, private local files; this module never creates or prints credentials.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import ipaddress
import json
import math
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import time
from urllib.parse import urlsplit

SIGNED_PATHS = frozenset({'/api/auth/login', '/api/auth/password-reset/complete'})
HEADER_NAMES = frozenset({'x-elvia-login-context', 'x-elvia-login-signature'})
CONTEXT_HEADER = 'X-Elvia-Login-Context'
SIGNATURE_HEADER = 'X-Elvia-Login-Signature'
MAX_AGE = 30
FUTURE_SKEW = 5
ERROR = 'The trusted sign-in connection could not be verified.'


def protected_action(method, target):
    return method == 'POST' and isinstance(target, str) and urlsplit(target).path in SIGNED_PATHS


def canonical_client_ip(value):
    if (not isinstance(value, str) or not 1 <= len(value) <= 45
            or value != value.strip() or '%' in value):
        raise ValueError(ERROR)
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        raise ValueError(ERROR) from None
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
        address = address.ipv4_mapped
    return address.compressed.lower()


def _key(key):
    if type(key) is not bytes or len(key) != 32:
        raise ValueError(ERROR)
    return key


def _clock(now):
    value = time.time() if now is None else now
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError(ERROR)
    return value


def _message(method, target, context, body):
    if (not protected_action(method, target) or not isinstance(body, bytes)
            or len(target) > 16384 or not target.startswith('/') or target.startswith('//')
            or any(ord(c) < 33 or ord(c) > 126 for c in target)):
        raise ValueError(ERROR)
    return (b'ELVIA-login-context-v1\0' + method.encode('ascii') + b'\0'
            + target.encode('ascii') + b'\0' + context.encode('ascii') + b'\0'
            + hashlib.sha256(body).hexdigest().encode('ascii'))


def sign_context(key, method, target, ip, raw_body, *, now=None):
    key = _key(key)
    payload = {'v': 1, 'ts': int(_clock(now)), 'ip': canonical_client_ip(ip)}
    context = base64.urlsafe_b64encode(json.dumps(payload, separators=(',', ':'),
                                      sort_keys=True).encode('ascii')).rstrip(b'=').decode('ascii')
    signature = hmac.new(key, _message(method, target, context, raw_body), hashlib.sha256).hexdigest()
    return {CONTEXT_HEADER: context, SIGNATURE_HEADER: signature}


def verify_context(key, headers, method, target, raw_body, *, now=None):
    try:
        key = _key(key)
        found = {name: [] for name in HEADER_NAMES}
        for name, value in headers.items():
            lower = name.casefold()
            if lower.startswith('x-elvia-'):
                if lower not in found:
                    raise ValueError(ERROR)
                found[lower].append(value)
        if any(len(values) != 1 for values in found.values()):
            raise ValueError(ERROR)
        context, signature = found['x-elvia-login-context'][0], found['x-elvia-login-signature'][0]
        if (not isinstance(context, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,256}', context)
                or not isinstance(signature, str) or not re.fullmatch(r'[0-9a-f]{64}', signature)):
            raise ValueError(ERROR)
        expected = hmac.new(key, _message(method, target, context, raw_body), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError(ERROR)
        raw = base64.urlsafe_b64decode(context + '=' * (-len(context) % 4))
        if base64.urlsafe_b64encode(raw).rstrip(b'=').decode('ascii') != context:
            raise ValueError(ERROR)
        def unique(pairs):
            result = {}
            for name, value in pairs:
                if name in result:
                    raise ValueError(ERROR)
                result[name] = value
            return result
        payload = json.loads(raw.decode('ascii'), object_pairs_hook=unique)
        if (not isinstance(payload, dict) or set(payload) != {'v', 'ts', 'ip'}
                or type(payload['v']) is not int or payload['v'] != 1
                or type(payload['ts']) is not int or payload['ts'] < 0
                or payload['ip'] != canonical_client_ip(payload['ip'])):
            raise ValueError(ERROR)
        current = _clock(now)
        if current - payload['ts'] > MAX_AGE or payload['ts'] - current > FUTURE_SKEW:
            raise ValueError(ERROR)
        return payload['ip']
    except (ValueError, TypeError, KeyError, AttributeError, UnicodeError, OverflowError):
        raise ValueError(ERROR) from None


def _plain(path, *, file=False):
    info = path.lstat()
    if (stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400
            or (file and (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1))
            or (not file and not stat.S_ISDIR(info.st_mode))):
        raise ValueError(ERROR)
    return info


def verify_private_key_acl(path):
    """Metadata only: require protected exact owner/SYSTEM FullControl ACL."""
    if os.name != 'nt':
        info = path.stat()
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
            raise ValueError(ERROR)
        return
    shell = shutil.which('pwsh.exe') or str(Path(os.environ['SystemRoot']) /
                'System32/WindowsPowerShell/v1.0/powershell.exe')
    script = r'''
$ErrorActionPreference = 'Stop'
try {
    $acl = Get-Acl -LiteralPath $env:ELVIA_LOGIN_PROXY_KEY_METADATA
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
    Write-Output 'ELVIA_LOGIN_PROXY_KEY_PRIVATE'
} catch { exit 1 }
'''
    environment = os.environ.copy()
    environment['ELVIA_LOGIN_PROXY_KEY_METADATA'] = str(path)
    result = subprocess.run([shell, '-NoLogo', '-NoProfile', '-NonInteractive', '-Command', script],
                            env=environment, capture_output=True, text=True, timeout=20)
    if result.returncode != 0 or result.stdout.strip() != 'ELVIA_LOGIN_PROXY_KEY_PRIVATE':
        raise ValueError(ERROR)


def load_proxy_key(path, *, expected_root=None):
    """Open only an explicitly selected plain, private, raw 32-byte key file."""
    try:
        path = Path(path)
        if (not path.is_absolute() or path.drive.startswith('\\\\') or '..' in path.parts
                or path.name != 'login-proxy.key' or path.parent.name != 'private-connection'):
            raise ValueError(ERROR)
        if expected_root is not None and path != Path(os.path.abspath(expected_root)) / 'private-connection/login-proxy.key':
            raise ValueError(ERROR)
        for parent in path.parents:
            _plain(parent)
        before = _plain(path, file=True)
        if before.st_size != 32:
            raise ValueError(ERROR)
        verify_private_key_acl(path)
        def identity(info):
            created = getattr(info, 'st_birthtime_ns', info.st_ctime_ns) if os.name == 'nt' else info.st_ctime_ns
            return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, created, info.st_nlink)
        with path.open('rb') as stream:
            if identity(os.fstat(stream.fileno())) != identity(before):
                raise ValueError(ERROR)
            key = stream.read(33)
            if identity(os.fstat(stream.fileno())) != identity(before):
                raise ValueError(ERROR)
        if identity(_plain(path, file=True)) != identity(before):
            raise ValueError(ERROR)
        return _key(key)
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError):
        raise ValueError(ERROR) from None
