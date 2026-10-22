"""New-password rules and legacy confirmation use synthetic isolated state only."""
import hashlib
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs,urlsplit

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'server'))
import test_local_service as base
from local_service import Problem,connect,make_server,password_hash,password_matches
from email_access import EmailAccess


VALID='Aaaaaaa!/'
LEGACY='legacyonly12'


def legacy_hash(value):
    salt=b'synthetic-salt42'
    return salt.hex()+':'+hashlib.scrypt(value.encode(),salt=salt,n=16384,r=8,p=1).hex()


class PasswordRules(unittest.TestCase):
    def test_nine_codepoints_ascii_uppercase_and_each_ascii_punctuation_are_accepted(self):
        import string
        for value in ('Aaaaaaaa!','Aaaaaaaa/','É'*7+'A!', 'A'+'😀'*6+'!a', 'A!'+'😀'*254):
            with self.subTest(length=len(value)):
                self.assertTrue(password_matches(value,password_hash(value)))
        for punctuation in string.punctuation:
            with self.subTest(punctuation=punctuation):
                self.assertTrue(password_matches('Aaaaaaaa'+punctuation,password_hash('Aaaaaaaa'+punctuation)))

    def test_short_missing_ascii_uppercase_missing_ascii_punctuation_and_overlong_are_rejected(self):
        for value in ('Aaaaaaa!','aaaaaaaa!','Aaaaaaaaa','Éaaaaaaa!','Aaaaaaaa？','A!'+'a'*255,None,[]):
            with self.subTest(shape=type(value).__name__),self.assertRaises(Problem):password_hash(value)

    def test_legacy_hash_verification_and_external_smtp_secret_do_not_use_new_policy(self):
        self.assertTrue(password_matches(LEGACY,legacy_hash(LEGACY)))
        self.assertFalse(password_matches('wrong',legacy_hash(LEGACY)))
        config=EmailAccess.validate_config({'host':'smtp.example.org','port':465,'security':'ssl',
            'sender':'accounts@example.org','username':'api_token','password':'lowercaseonly'})
        self.assertEqual(config['password'],'lowercaseonly')

    def test_generated_bootstrap_and_dummy_passwords_always_satisfy_the_policy(self):
        with tempfile.TemporaryDirectory() as folder,patch('local_service.secrets.token_urlsafe',return_value='a'*32):
            server=make_server(Path(folder))
            try:
                content=(Path(folder)/'MAINTAINER-LOGIN.txt').read_text('utf-8')
                generated=content.split('Temporary password: ',1)[1].split('\n',1)[0]
                self.assertRegex(generated,r'[A-Z]')
                self.assertTrue(any(c in __import__('string').punctuation for c in generated))
                self.assertTrue(password_matches(generated,server.dummy_hash))
            finally:server.server_close()


class PasswordPolicyHTTP(unittest.TestCase):
    setUp=base.ServiceContract.setUp
    tearDown=base.ServiceContract.tearDown

    def test_registration_and_manual_change_share_new_rules_while_login_keeps_legacy(self):
        guest=base.Client(self.base);email='nine@example.edu'
        self.assertEqual(guest.call('POST','/api/auth/email-code',{'email':email})[0],200)
        for bad in ('Aaaaaaa!','aaaaaaaa!','Aaaaaaaaa','Éaaaaaaa!'):
            status,_=guest.call('POST','/api/auth/register',{'email':email,'email_code':base.TEST_MAILBOX[email],
                'name':'Synthetic policy member','password':bad})
            self.assertEqual(status,400)
        status,result=guest.call('POST','/api/auth/register',{'email':email,'email_code':base.TEST_MAILBOX[email],
            'name':'Synthetic policy member','password':VALID})
        self.assertEqual(status,201,result)
        for bad in ('Aaaaaaa!','aaaaaaaa!','Aaaaaaaaa'):
            self.assertEqual(guest.call('POST','/api/auth/password',{'current':VALID,'password':bad})[0],400)
        self.assertEqual(guest.call('POST','/api/auth/password',{'current':VALID,'password':'Bbbbbbbb/'})[0],200)
        with connect(self.server.db_path) as db:
            db.execute('UPDATE users SET password=? WHERE login=?',(legacy_hash(LEGACY),email))
        legacy=base.Client(self.base)
        self.assertEqual(legacy.call('POST','/api/auth/login',{'login':email,'password':LEGACY})[0],200)
        self.assertEqual(legacy.call('POST','/api/auth/password',{'current':LEGACY,'password':VALID})[0],200)

    def test_google_current_password_confirmation_accepts_a_legacy_password(self):
        with connect(self.server.db_path) as db:
            db.execute("UPDATE users SET password=? WHERE login='minhao'",(legacy_hash(LEGACY),))
        with patch.object(self.server.google,'start',return_value=('https://accounts.google.com/o/oauth2/v2/auth?synthetic=1','elvia_oauth=synthetic; Path=/; HttpOnly')) as start:
            status,response=self.admin.call('POST','/api/auth/google/start',{'mode':'link','password':LEGACY})
            self.assertEqual(status,200,response)
            self.assertEqual(start.call_count,1)

    def test_reset_rejects_invalid_new_password_without_consuming_link_then_accepts_nine(self):
        owner=self.admin.call('GET','/api/session')[1]['user']['id']
        with connect(self.server.db_path) as db:
            db.execute('INSERT INTO google_identities VALUES(?,?,?,?)',('synthetic-policy-owner',owner,'policy@example.org','2026-10-22'))
        delivered=[]
        self.server.mailer.send_password_reset=lambda email,url:delivered.append(url)
        guest=base.Client(self.base)
        self.assertEqual(guest.call('POST','/api/auth/password-reset/request',{'email':'policy@example.org'})[0],202)
        deadline=time.monotonic()+3
        while time.monotonic()<deadline:
            with connect(self.server.db_path) as db:
                if db.execute('SELECT COUNT(*) FROM password_reset_tokens WHERE sent=1').fetchone()[0]:break
            time.sleep(.01)
        self.assertEqual(len(delivered),1)
        token=parse_qs(urlsplit(delivered[0]).fragment)['token'][0]
        for bad in ('Aaaaaaa!','aaaaaaaa!','Aaaaaaaaa'):
            self.assertEqual(guest.call('POST','/api/auth/password-reset/complete',{'token':token,'newpassword':bad})[0],400)
            with connect(self.server.db_path) as db:
                self.assertEqual(db.execute('SELECT used FROM password_reset_tokens').fetchone()[0],0)
        self.assertEqual(guest.call('POST','/api/auth/password-reset/complete',{'token':token,'newpassword':VALID})[0],200)
        self.assertEqual(guest.call('POST','/api/auth/login',{'login':'minhao','password':VALID})[0],200)
        with connect(self.server.db_path) as db:
            self.assertEqual(db.execute('SELECT role FROM users WHERE id=?',(owner,)).fetchone()[0],'maintainer')
            self.assertEqual(db.execute('SELECT COUNT(*) FROM google_identities').fetchone()[0],1)


if __name__=='__main__':unittest.main()
