"""Synthetic trust-context and private-key boundary regressions; no real data."""
from email.message import Message
import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).absolute().parents[1] / "server"))
import trusted_login_proxy as proxy
from origin_policy import OriginPolicy

KEY=bytes(range(32))
PATH="/api/auth/login"
BODY=b'{"login":"synthetic","password":"not-real"}'

def headers(values):
    result=Message()
    for name,value in values.items():result[name]=value
    return result


def make_synthetic_proxy_key(root):
    """Create a disposable key only below the OS temporary directory."""
    root=Path(root).absolute()
    if not root.is_relative_to(Path(tempfile.gettempdir()).absolute()):
        raise ValueError('Synthetic key fixtures require a disposable temporary root.')
    key=root/'private-connection/login-proxy.key';key.parent.mkdir(parents=True,exist_ok=True)
    with key.open('xb') as stream:stream.write(KEY)
    acl=_SyntheticACL();acl.key=key;acl.acl()
    return key,KEY


class ContextTests(unittest.TestCase):
    def signed(self, **kw):
        return proxy.sign_context(KEY,'POST',PATH,'2001:0DB8::1',BODY,now=1000,**kw)

    def test_exact_action_and_canonical_single_ip(self):
        self.assertTrue(proxy.protected_action('POST',PATH+'?synthetic=1'))
        for method,target in [('GET',PATH),('POST','/api/auth/register'),('POST','/API/auth/login')]:
            self.assertFalse(proxy.protected_action(method,target))
        self.assertEqual(proxy.canonical_client_ip('2001:0DB8:0::1'),'2001:db8::1')
        self.assertEqual(proxy.canonical_client_ip('::ffff:192.0.2.1'),'192.0.2.1')
        for value in ('',' 192.0.2.1','192.0.2.1 ','192.0.2.1, 192.0.2.2','[::1]','fe80::1%1','010.0.0.1',None):
            with self.subTest(value=value),self.assertRaises(ValueError):proxy.canonical_client_ip(value)

    def test_signed_context_roundtrip_and_exact_body_target_method_binding(self):
        signed=headers(self.signed())
        self.assertEqual(proxy.verify_context(KEY,signed,'POST',PATH,BODY,now=1000),'2001:db8::1')
        self.assertEqual(proxy.verify_context(KEY,signed,'POST',PATH,BODY,now=1030),'2001:db8::1')
        for key,method,target,body in [(b'x'*32,'POST',PATH,BODY),(KEY,'PUT',PATH,BODY),(KEY,'POST',PATH+'?a=1',BODY),(KEY,'POST',PATH,BODY+b' ')]:
            with self.subTest(target=target,method=method),self.assertRaises(ValueError):proxy.verify_context(key,signed,method,target,body,now=1000)
        for when in (994,1031):
            with self.subTest(when=when),self.assertRaises(ValueError):proxy.verify_context(KEY,signed,'POST',PATH,BODY,now=when)

    def test_missing_duplicate_extra_malformed_and_tampered_contexts_refused(self):
        signed=self.signed()
        for name in proxy.HEADER_NAMES:
            missing={k:v for k,v in signed.items() if k.casefold()!=name}
            with self.assertRaises(ValueError):proxy.verify_context(KEY,headers(missing),'POST',PATH,BODY,now=1000)
            duplicate=headers(signed);duplicate[name]=duplicate.get(name)
            with self.assertRaises(ValueError):proxy.verify_context(KEY,duplicate,'POST',PATH,BODY,now=1000)
        for name,value in [('X-Elvia-Login-Context','!'),('X-Elvia-Login-Signature','0'*64),('X-Elvia-Login-Signature','A'*64)]:
            broken=dict(signed);broken[name]=value
            with self.assertRaises(ValueError):proxy.verify_context(KEY,headers(broken),'POST',PATH,BODY,now=1000)
        extra=headers(signed);extra['X-Elvia-Other']='synthetic'
        with self.assertRaises(ValueError):proxy.verify_context(KEY,extra,'POST',PATH,BODY,now=1000)
        for key in (None,b'short',bytearray(32)):
            with self.assertRaises(ValueError):proxy.verify_context(key,headers(signed),'POST',PATH,BODY,now=1000)

    def test_context_payload_canonicality_and_duplicate_json_refused_even_with_valid_mac(self):
        for raw in (b'{"v":1,"ts":1000,"ip":"192.0.2.1","ip":"192.0.2.2"}',b'{"v":true,"ts":1000,"ip":"192.0.2.1"}',b'{"v":1,"ts":1000,"ip":"::ffff:192.0.2.1"}',b'{"v":1,"ts":1000,"ip":"192.0.2.1","extra":1}'):
            ctx=base64.urlsafe_b64encode(raw).rstrip(b'=').decode()
            msg=b'ELVIA-login-context-v1\0POST\0'+PATH.encode()+b'\0'+ctx.encode()+b'\0'+hashlib.sha256(BODY).hexdigest().encode()
            supplied=headers({'X-Elvia-Login-Context':ctx,'X-Elvia-Login-Signature':hmac.new(KEY,msg,hashlib.sha256).hexdigest()})
            with self.assertRaises(ValueError):proxy.verify_context(KEY,supplied,'POST',PATH,BODY,now=1000)


class OriginContextTests(unittest.TestCase):
    def test_origin_exception_is_exact_opt_in_and_duplicates_still_fail_closed(self):
        policy=OriginPolicy(8797,'https://elvia-atlas.org')
        supplied=headers({'Host':'elvia-atlas.org','Origin':'https://elvia-atlas.org',**proxy.sign_context(KEY,'POST',PATH,'192.0.2.1',BODY,now=1000)})
        with self.assertRaises(ValueError):policy.request_origin(supplied,'POST')
        self.assertEqual(policy.request_origin(supplied,'POST',allow_login_context=True),'https://elvia-atlas.org')
        for name in ('X-Elvia-Other','CF-Connecting-IP','CF-Access-Jwt-Assertion','Forwarded','X-Forwarded-For'):
            altered=headers(dict(supplied.items()));altered[name]='spoof'
            with self.subTest(name=name),self.assertRaises(ValueError):policy.request_origin(altered,'POST',allow_login_context=True)
        supplied['x-elvia-login-context']='duplicate'
        with self.assertRaises(ValueError):policy.request_origin(supplied,'POST',allow_login_context=True)


class _SyntheticACL:
    def acl(self, extra=False):
        if os.name!='nt':self.key.chmod(0o600 if not extra else 0o644);return
        script=r"""$ErrorActionPreference='Stop';$p=$env:ELVIA_SYNTHETIC_KEY;$sid=[Security.Principal.WindowsIdentity]::GetCurrent().User;$acl=[Security.AccessControl.FileSecurity]::new();$acl.SetOwner($sid);$acl.SetAccessRuleProtection($true,$false);foreach($s in @($sid,[Security.Principal.SecurityIdentifier]::new('S-1-5-18'))){$acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($s,'FullControl','Allow'))};if($env:ELVIA_SYNTHETIC_EXTRA -eq '1'){$acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new([Security.Principal.SecurityIdentifier]::new('S-1-5-32-545'),'Read','Allow'))};Set-Acl -LiteralPath $p -AclObject $acl"""
        env=os.environ.copy();env['ELVIA_SYNTHETIC_KEY']=str(self.key);env['ELVIA_SYNTHETIC_EXTRA']='1' if extra else '0'
        shell=shutil.which('pwsh.exe') or 'powershell.exe'
        result=subprocess.run([shell,'-NoProfile','-NonInteractive','-Command',script],env=env,capture_output=True,timeout=20)
        if result.returncode!=0:raise RuntimeError('Synthetic ACL setup failed')


class KeyTests(_SyntheticACL,unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='elvia-proxy-key-synthetic-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.key=self.root/'private-connection'/'login-proxy.key';self.key.parent.mkdir();self.key.write_bytes(KEY)

    def test_private_key_exact_bytes_and_root_binding(self):
        self.acl();self.assertEqual(proxy.load_proxy_key(self.key,expected_root=self.root),KEY)
        with self.assertRaises(ValueError):proxy.load_proxy_key(self.key,expected_root=self.root/'other')
        for raw in (KEY[:-1],KEY+b'x'):
            self.key.write_bytes(raw)
            with self.assertRaises(ValueError):proxy.load_proxy_key(self.key)

    def test_key_acl_extra_grant_is_refused_without_modification(self):
        self.acl(extra=True);before=self.key.read_bytes()
        with self.assertRaises(ValueError):proxy.load_proxy_key(self.key)
        self.assertEqual(self.key.read_bytes(),before)

    def test_hardlink_and_wrong_scope_rejected_before_acl_or_content_read(self):
        outside=self.root/'outside';outside.write_bytes(KEY);self.key.unlink();os.link(outside,self.key)
        with patch.object(proxy,'verify_private_key_acl',side_effect=AssertionError('ACL must not run')):
            with self.assertRaises(ValueError):proxy.load_proxy_key(self.key)
            with self.assertRaises(ValueError):proxy.load_proxy_key('private-connection/login-proxy.key')
            with self.assertRaises(ValueError):proxy.load_proxy_key(outside)

if __name__=='__main__':unittest.main()
