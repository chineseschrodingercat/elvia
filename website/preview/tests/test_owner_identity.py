"""Exact owner consolidation: disposable accounts only, no actual mail/OAuth."""
from pathlib import Path
import sys
import tempfile
import time
import unittest
from urllib.parse import parse_qs,urlsplit

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'server'))
import test_local_service as base
from local_service import connect,initialize,password_hash,stamp,Handler
from google_login import GoogleLogin,GoogleLoginError
from owner_identity import (apply_fixed_owner,resolve_login,resolve_alias,IdentityError,
                            OWNER_EMAIL,OWNER_GOOGLE_EMAIL,RETIRED_PASSWORD,recovery_user_ids)
EMAIL=OWNER_EMAIL
PASSWORD='Synthetic unified password 42!'


class ExplicitOwnerAlias(unittest.TestCase):
    setUp=base.ServiceContract.setUp
    tearDown=base.ServiceContract.tearDown

    def pair(self):
        source=base.Client(self.base)
        status,created=source.call('POST','/api/auth/register',{'email':EMAIL,'name':'Synthetic owner','password':PASSWORD})
        self.assertEqual(status,201,created)
        canonical=self.admin.call('GET','/api/session')[1]['user']['id'];retired=created['user']['id']
        with connect(self.server.db_path) as db:
            db.execute('INSERT INTO google_identities VALUES(?,?,?,?)',('synthetic-owner-subject',canonical,OWNER_GOOGLE_EMAIL,stamp()))
            db.execute('INSERT INTO events(actor,target,action,note,created) VALUES(?,?,?,?,?)',(retired,retired,'password_reset_completed','synthetic fixture',stamp()))
            apply_fixed_owner(db,stamp())
        return source,canonical,retired

    def test_explicit_email_alias_signs_in_as_the_existing_canonical_maintainer(self):
        source,canonical,retired=self.pair()
        status,result=base.Client(self.base).call('POST','/api/auth/login',{'login':EMAIL,'password':PASSWORD})
        self.assertEqual(status,200,result)
        self.assertEqual((result['user']['id'],result['user']['login'],result['user']['role']),(canonical,'minhao','maintainer'))
        self.assertEqual(base.Client(self.base).call('POST','/api/auth/login',{'login':'minhao','password':PASSWORD})[1]['user']['id'],canonical)
        self.assertIsNone(source.call('GET','/api/session')[1]['user'])
        self.assertIsNone(self.admin.call('GET','/api/session')[1]['user'])
        with connect(self.server.db_path) as db:
            self.assertEqual(tuple(db.execute('SELECT login,role,password FROM users WHERE id=?',(retired,)).fetchone()),(EMAIL,'reviewer',RETIRED_PASSWORD))
            google=self.server.google.finish(db,{'subject':'synthetic-owner-subject','email':OWNER_GOOGLE_EMAIL},{'mode':'login'},None,stamp)
            self.assertEqual((google['id'],google['role']),(canonical,'maintainer'))

    def test_canonical_owner_cannot_claim_independent_review_of_retired_identity_work(self):
        _,_,retired=self.pair()
        self.admin.call('POST','/api/auth/login',{'login':'minhao','password':PASSWORD})
        with connect(self.server.db_path) as db:
            db.execute('INSERT INTO contributions VALUES(?,?,?,?,?,?,?,?,?,?,?)',('c_old_owner',retired,'new',None,'accepted','{}',1,1,'',stamp(),stamp()))
            db.execute('INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?)',('old-owner-task','Historical synthetic title','Test','Question','Context',1,'c_old_owner',stamp()))
        status,result=self.admin.call('POST','/api/contributions',{'kind':'review','task_id':'old-owner-task','conflict_clear':True})
        self.assertEqual(status,403,result)
        with connect(self.server.db_path) as db:self.assertEqual(db.execute('SELECT owner FROM contributions WHERE id=?',('c_old_owner',)).fetchone()[0],retired)

    def test_ttu_reset_changes_only_canonical_password_and_preserves_role_google(self):
        _,canonical,retired=self.pair();messages=[]
        # Registration and recovery share a real 60-second mail cooldown. Age
        # only the disposable fixture's reservation to model that elapsed time.
        with connect(self.server.db_path) as db:db.execute('UPDATE abuse_mail_reservations SET created=created-61')
        self.server.mailer.send_password_reset=lambda email,url:messages.append(url)
        guest=base.Client(self.base)
        self.assertEqual(guest.call('POST','/api/auth/password-reset/request',{'email':EMAIL})[0],202)
        deadline=time.monotonic()+3
        while time.monotonic()<deadline:
            with connect(self.server.db_path) as db:
                if db.execute('SELECT 1 FROM password_reset_tokens WHERE sent=1').fetchone():break
            time.sleep(.01)
        self.assertEqual(len(messages),1)
        token=parse_qs(urlsplit(messages[0]).fragment)['token'][0]
        self.assertEqual(guest.call('POST','/api/auth/password-reset/complete',{'token':token,'newpassword':'Another unified password 42!'})[0],200)
        result=guest.call('POST','/api/auth/login',{'login':EMAIL,'password':'Another unified password 42!'})[1]
        self.assertEqual((result['user']['id'],result['user']['role']),(canonical,'maintainer'))
        with connect(self.server.db_path) as db:
            self.assertEqual(db.execute('SELECT password FROM users WHERE id=?',(retired,)).fetchone()[0],RETIRED_PASSWORD)
            self.assertEqual(db.execute('SELECT user_id FROM google_identities').fetchone()[0],canonical)
            self.assertEqual(db.execute('SELECT user_id FROM password_reset_tokens').fetchone()[0],canonical)

    def test_recovery_daily_limit_counts_retired_account_history(self):
        _,_,retired=self.pair();messages=[]
        self.server.mailer.send_password_reset=lambda email,url:messages.append(url)
        with connect(self.server.db_path) as db:
            db.execute('UPDATE abuse_mail_reservations SET created=created-61')
            for n in range(5):db.execute('INSERT INTO password_reset_tokens VALUES(?,?,?,?,?,?,?,?)',('old_'+str(n),retired,EMAIL,'binding',time.time()-120,time.time()+900,1,1))
        self.assertEqual(base.Client(self.base).call('POST','/api/auth/password-reset/request',{'email':EMAIL})[0],202)
        self.assertEqual(messages,[])
        with connect(self.server.db_path) as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM password_reset_tokens').fetchone()[0],5)

    def test_retired_identity_cannot_be_reactivated_promoted_or_registered_again(self):
        _,_,retired=self.pair()
        self.admin.call('POST','/api/auth/login',{'login':'minhao','password':PASSWORD})
        self.assertEqual(self.admin.call('POST',f'/api/admin/accounts/{retired}/status',{'status':'active','note':'Synthetic attempted reactivation'})[0],403)
        self.assertEqual(self.admin.call('POST','/api/admin/roles',{'email':EMAIL,'role':'admin','password':PASSWORD})[0],403)
        self.assertEqual(base.Client(self.base).call('POST','/api/auth/email-code',{'email':EMAIL})[0],409)
        directory=self.admin.call('GET','/api/admin/accounts')[1]
        self.assertNotIn(retired,[row['id'] for row in directory['accounts']])
        with connect(self.server.db_path) as db:
            db.execute("UPDATE users SET role='admin' WHERE id=?",(retired,))
            db.execute('INSERT INTO google_identities VALUES(?,?,?,?)',('retired-google',retired,'retired@example.org',stamp()))
            with self.assertRaises(GoogleLoginError):self.server.google.finish(db,{'subject':'retired-google','email':'retired@example.org'},{'mode':'login'},None,stamp)


class OwnerMaintenance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=initialize(Path(self.tmp.name),bootstrap_password='Synthetic original password 42!')
        with connect(self.path) as db:
            GoogleLogin(Path(self.tmp.name),0).initialize(db)
            self.canonical=db.execute("SELECT id FROM users WHERE login='minhao'").fetchone()[0]
            db.execute('UPDATE users SET force_change=0')
            db.execute('INSERT INTO users VALUES(?,?,?,?,?,?,?)',('u_source',EMAIL,'Synthetic owner','reviewer',password_hash(PASSWORD),0,stamp()))
            db.execute('INSERT INTO verified_emails VALUES(?,?,?)',('u_source',EMAIL,'2026-10-21'))
            db.execute('INSERT INTO google_identities VALUES(?,?,?,?)',('owner-google',self.canonical,OWNER_GOOGLE_EMAIL,stamp()))
            db.execute('INSERT INTO events(actor,target,action,note,created) VALUES(?,?,?,?,?)',('u_source','u_source','password_reset_completed','synthetic fixture',stamp()))

    def apply(self):
        with connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE');return apply_fixed_owner(db,stamp())

    def test_idempotence_preserves_history_google_and_a_later_canonical_password(self):
        with connect(self.path) as db:
            source=dict(db.execute("SELECT * FROM users WHERE id='u_source'").fetchone())
            google=tuple(db.execute('SELECT * FROM google_identities').fetchone())
        self.assertTrue(self.apply()['changed'])
        with connect(self.path) as db:
            current=dict(db.execute("SELECT * FROM users WHERE id='u_source'").fetchone())
            for field in ('id','login','name','role','created'):self.assertEqual(current[field],source[field])
            self.assertEqual(db.execute('SELECT password FROM users WHERE id=?',(self.canonical,)).fetchone()[0],source['password'])
            self.assertEqual(tuple(db.execute('SELECT * FROM google_identities').fetchone()),google)
            replacement=password_hash('Later canonical password 42!');db.execute('UPDATE users SET password=? WHERE id=?',(replacement,self.canonical))
        with connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE');before=db.total_changes
            self.assertFalse(apply_fixed_owner(db,stamp())['changed']);self.assertEqual(db.total_changes,before)
            self.assertEqual(db.execute('SELECT password FROM users WHERE id=?',(self.canonical,)).fetchone()[0],replacement)

    def test_source_business_and_identity_conflicts_refuse_before_any_mutation(self):
        changes=["INSERT INTO applications VALUES('u_source','{}','pending','','now')",
                 "INSERT INTO daily_usage VALUES('u_source','2026-10-22','new_submit','synthetic',0)",
                 "INSERT INTO contributions VALUES('c_source','u_source','new',NULL,'draft','{}',1,1,'','now','now')",
                 "INSERT INTO google_identities VALUES('source-google','u_source','source@example.org','now')",
                 "UPDATE users SET role='admin' WHERE id='u_source'",
                 "UPDATE users SET force_change=1 WHERE id='u_source'",
                 "INSERT INTO users VALUES('u_third','MINHLIU@TTU.EDU','Third','reviewer','unusable',0,'now')"]
        for sql in changes:
            with self.subTest(change=sql.split()[0:3]),connect(self.path) as db:
                db.execute('BEGIN IMMEDIATE');db.execute(sql);before=db.total_changes
                with self.assertRaises(IdentityError):apply_fixed_owner(db,stamp())
                self.assertEqual(db.total_changes,before)
                self.assertEqual(db.execute('SELECT COUNT(*) FROM account_merges').fetchone()[0],0);db.rollback()

    def test_broken_alias_denies_legacy_fallback_and_recovery_counts_include_old_source(self):
        with connect(self.path) as db:
            for n in range(5):db.execute('INSERT INTO password_reset_tokens VALUES(?,?,?,?,?,?,?,?)',(str(n),'u_source',EMAIL,'binding',time.time(),time.time()+900,1,1))
        self.apply()
        with connect(self.path) as db:
            self.assertEqual(Handler.password_recovery_account(db,EMAIL)['id'],self.canonical)
            ids=recovery_user_ids(db,self.canonical)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM password_reset_tokens WHERE user_id IN (?,?)',ids).fetchone()[0],5)
            db.execute('DELETE FROM verified_emails WHERE user_id=?',(self.canonical,))
            self.assertIsNone(resolve_login(db,EMAIL));self.assertIsNone(Handler.password_recovery_account(db,EMAIL))

    def test_only_exact_pair_sessions_and_tokens_are_revoked_and_names_never_autolink(self):
        with connect(self.path) as db:
            db.execute('INSERT INTO users VALUES(?,?,?,?,?,?,?)',('u_other','other@example.edu','Synthetic owner','reviewer',password_hash(PASSWORD),0,stamp()))
            db.execute('INSERT INTO verified_emails VALUES(?,?,?)',('u_other','other@example.edu',stamp()))
            for uid in (self.canonical,'u_source','u_other'):
                db.execute('INSERT INTO sessions VALUES(?,?,?,?)',('s_'+uid,uid,'csrf',time.time()+900))
                db.execute('INSERT INTO password_reset_tokens VALUES(?,?,?,?,?,?,?,?)',('t_'+uid,uid,EMAIL,'binding',time.time(),time.time()+900,0,1))
                db.execute('INSERT INTO oauth_states VALUES(?,?,?,?,?,?,?,?)',('o_'+uid,'binding','proof','nonce',time.time()+900,uid,'s_'+uid,'link'))
        self.apply()
        with connect(self.path) as db:
            self.assertEqual([r[0] for r in db.execute('SELECT user_id FROM sessions')],['u_other'])
            self.assertEqual([r[0] for r in db.execute('SELECT actor FROM oauth_states')],['u_other'])
            self.assertEqual([r[0] for r in db.execute('SELECT user_id FROM password_reset_tokens WHERE used=0')],['u_other'])
            self.assertEqual(resolve_login(db,'other@example.edu')['id'],'u_other')
            self.assertIsNone(resolve_alias(db,'other@example.edu'))

    def test_post_merge_google_or_login_ambiguity_fails_closed(self):
        self.apply()
        for extra in ('source_google','third_google','case_variant'):
            with self.subTest(extra=extra),connect(self.path) as db:
                db.execute('BEGIN IMMEDIATE')
                if extra=='source_google':db.execute('INSERT INTO google_identities VALUES(?,?,?,?)',('source-google','u_source','source@example.org','now'))
                else:
                    login='MINHLIU@TTU.EDU' if extra=='case_variant' else 'third@example.edu'
                    db.execute('INSERT INTO users VALUES(?,?,?,?,?,?,?)',('u_third',login,'Third','reviewer','unusable',0,'now'))
                    if extra=='third_google':db.execute('INSERT INTO google_identities VALUES(?,?,?,?)',('third-google','u_third',OWNER_GOOGLE_EMAIL,'now'))
                self.assertIsNone(resolve_login(db,EMAIL));self.assertIsNone(Handler.password_recovery_account(db,EMAIL))
                with self.assertRaises(IdentityError):apply_fixed_owner(db,stamp())
                db.rollback()


if __name__=='__main__':unittest.main()
