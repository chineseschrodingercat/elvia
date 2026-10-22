"""Source-IP login locks use synthetic accounts and no real providers."""
from pathlib import Path
import json
import sys
import tempfile
import threading
import time
import unittest
from urllib.parse import parse_qs,urlsplit

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'server'))
import test_local_service as base
from local_service import connect
from login_guard import LoginGuard,initialize_login_guard
import test_private_origin as private_support


class DurableLoginGuard(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        self.path=Path(self.folder.name)/'elvia.sqlite3';self.guard=LoginGuard(b'synthetic-login-key-only')
        with connect(self.path) as db:initialize_login_guard(db)

    def call(self,method,source,now):
        with connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE');return getattr(self.guard,method)(db,source,now)

    def test_rolling_hour_ten_failures_lock_for_an_hour_and_survive_new_instance(self):
        for number in range(9):self.assertEqual(self.call('failure','192.0.2.1',100+number)['remaining'],9-number)
        state=self.call('failure','192.0.2.1',109)
        self.assertTrue(state['locked']);self.assertEqual(state['retry_after'],3600)
        self.guard=LoginGuard(b'synthetic-login-key-only')
        self.assertEqual(self.call('state','::ffff:192.0.2.1',110)['retry_after'],3599)
        self.assertFalse(self.call('state','192.0.2.1',3709)['locked'])
        self.assertEqual(self.call('state','192.0.2.1',3709)['remaining'],10)

    def test_rolling_window_retains_recent_failures_and_clear_is_source_only(self):
        self.call('failure','192.0.2.1',100)
        self.call('failure','192.0.2.1',3699)
        self.assertEqual(self.call('state','192.0.2.1',3701)['remaining'],9)
        self.call('failure','192.0.2.2',3701)
        with connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE');self.guard.clear(db,'192.0.2.1')
        self.assertEqual(self.call('state','192.0.2.1',3702)['remaining'],10)
        self.assertEqual(self.call('state','192.0.2.2',3702)['remaining'],9)

    def test_concurrent_failure_updates_lock_at_ten_without_oversubscription(self):
        results=[];barrier=threading.Barrier(12)
        def failure():barrier.wait();results.append(self.call('failure','192.0.2.1',100))
        workers=[threading.Thread(target=failure) for _ in range(12)]
        for worker in workers:worker.start()
        for worker in workers:worker.join()
        self.assertEqual(sum(not result['locked'] for result in results),9)
        with connect(self.path) as db:
            rows=db.execute('SELECT source_key,failures FROM login_guard').fetchall()
            self.assertEqual(len(rows),1);self.assertEqual(len(json.loads(rows[0][1])),10)
            self.assertNotIn('192.0.2.1',json.dumps([tuple(row) for row in rows]))

    def test_preexisting_five_failure_lock_remains_locked_without_rewriting_state(self):
        key=self.guard.source_key('192.0.2.1')
        original=(key,'[96,97,98,99,100]',3700,100)
        with connect(self.path) as db:db.execute('INSERT INTO login_guard VALUES(?,?,?,?)',original)
        self.guard=LoginGuard(b'synthetic-login-key-only')
        state=self.call('state','192.0.2.1',101)
        self.assertTrue(state['locked']);self.assertEqual(state['retry_after'],3599)
        with connect(self.path) as db:self.assertEqual(tuple(db.execute('SELECT * FROM login_guard').fetchone()),original)

    def test_existing_four_failures_continue_to_fifth_with_five_remaining(self):
        key=self.guard.source_key('192.0.2.1')
        with connect(self.path) as db:db.execute('INSERT INTO login_guard VALUES(?,?,?,?)',(key,'[96,97,98,99]',0,99))
        state=self.call('failure','192.0.2.1',100)
        self.assertFalse(state['locked']);self.assertEqual(state['remaining'],5)
        self.assertEqual(state['failures'],[96,97,98,99,100])

    def test_capacity_preserves_live_locks_and_refuses_new_source(self):
        with connect(self.path) as db:
            db.executemany('INSERT INTO login_guard VALUES(?,?,?,?)',[(str(number),'[100]',3700,100) for number in range(1024)])
        self.assertTrue(self.call('state','192.0.2.1',101)['capacity'])
        with connect(self.path) as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM login_guard').fetchone()[0],1024)


class LoginLockHTTP(unittest.TestCase):
    setUp=base.ServiceContract.setUp
    tearDown=base.ServiceContract.tearDown

    def test_tenth_wrong_login_locks_source_and_keeps_reads_and_recovery_open(self):
        guest=base.Client(self.base)
        for number in range(9):
            status,body=guest.call('POST','/api/auth/login',{'login':'minhao','password':'wrong'})
            self.assertEqual(status,401,body)
            self.assertEqual(body['login_attempts_remaining'],9-number)
            if number<4:self.assertEqual(body['error'],'The account or password is incorrect.')
            else:self.assertIn(str(9-number)+' attempts remain',body['error'])
        status,body=guest.call('POST','/api/auth/login',{'login':'minhao','password':'wrong'})
        self.assertEqual(status,429,body)
        self.assertTrue(body['login_locked'])
        self.assertEqual(body['login_attempts_remaining'],0)
        self.assertGreaterEqual(body['retry_after'],3599)
        self.assertEqual(guest.call('POST','/api/auth/login',{'login':'minhao','password':'Changed-test-password-42'})[0],429)
        self.assertEqual(guest.call('GET','/api/session')[0],200)
        self.assertEqual(guest.call('POST','/api/auth/password-reset/request',{'email':'missing@example.edu'})[0],202)
        self.assertEqual(self.admin.call('GET','/api/session')[1]['user']['role'],'maintainer')

    def test_unknown_accounts_share_the_same_source_limit_and_success_before_ten_clears_it(self):
        guest=base.Client(self.base)
        for number in range(9):
            status,result=guest.call('POST','/api/auth/login',{'login':'unknown'+str(number),'password':'wrong'})
            self.assertEqual(status,401);self.assertEqual(result['login_attempts_remaining'],9-number)
        self.assertEqual(guest.call('POST','/api/auth/login',{'login':'minhao','password':'Changed-test-password-42'})[0],200)
        self.assertEqual(guest.call('POST','/api/auth/login',{'login':'unknown','password':'wrong'})[1]['login_attempts_remaining'],9)

    def test_successful_reset_unlocks_only_current_source_and_bad_token_cannot_unlock(self):
        owner=self.admin.call('GET','/api/session')[1]['user']['id']
        with connect(self.server.db_path) as db:
            db.execute('INSERT INTO google_identities VALUES(?,?,?,?)',('synthetic-lock-owner',owner,'lock@example.org','2026-10-22'))
            db.execute('BEGIN IMMEDIATE') if not db.in_transaction else None
            for _ in range(10):self.server.login_guard.failure(db,'192.0.2.20',time.time())
        guest=base.Client(self.base)
        for _ in range(10):guest.call('POST','/api/auth/login',{'login':'minhao','password':'wrong'})
        delivered=[];self.server.mailer.send_password_reset=lambda email,url:delivered.append(url)
        self.assertEqual(guest.call('POST','/api/auth/password-reset/request',{'email':'lock@example.org'})[0],202)
        deadline=time.monotonic()+3
        while time.monotonic()<deadline:
            with connect(self.server.db_path) as db:
                if db.execute('SELECT COUNT(*) FROM password_reset_tokens WHERE sent=1').fetchone()[0]:break
            time.sleep(.01)
        self.assertEqual(len(delivered),1)
        self.assertEqual(guest.call('POST','/api/auth/password-reset/complete',{'token':'bad','newpassword':'Unlocked-password-42!'})[0],400)
        with connect(self.server.db_path) as db:
            db.execute('BEGIN IMMEDIATE');self.assertTrue(self.server.login_guard.state(db,'127.0.0.1',time.time())['locked'])
        token=parse_qs(urlsplit(delivered[0]).fragment)['token'][0]
        self.assertEqual(guest.call('POST','/api/auth/password-reset/complete',{'token':token,'newpassword':'Unlocked-password-42!'})[0],200)
        with connect(self.server.db_path) as db:
            db.execute('BEGIN IMMEDIATE')
            self.assertFalse(self.server.login_guard.state(db,'127.0.0.1',time.time())['locked'])
            self.assertTrue(self.server.login_guard.state(db,'192.0.2.20',time.time())['locked'])
            self.assertEqual(db.execute('SELECT role FROM users WHERE id=?',(owner,)).fetchone()[0],'maintainer')
            self.assertEqual(db.execute('SELECT COUNT(*) FROM google_identities').fetchone()[0],1)
        self.assertEqual(guest.call('POST','/api/auth/login',{'login':'minhao','password':'Unlocked-password-42!'})[0],200)

    def test_stopped_writer_backup_restore_preserves_a_live_lock_and_hmac_key(self):
        import importlib.util
        helper=Path(__file__).resolve().parents[2]/'ops/workspace_backup.py'
        spec=importlib.util.spec_from_file_location('login_lock_backup',helper)
        backup=importlib.util.module_from_spec(spec);spec.loader.exec_module(backup)
        guest=base.Client(self.base)
        for _ in range(10):guest.call('POST','/api/auth/login',{'login':'minhao','password':'wrong'})
        self.server.shutdown();self.server.server_close();self.thread.join()
        with tempfile.TemporaryDirectory() as destination:
            snapshot=Path(destination)/'snapshot';restored=Path(destination)/'restored'
            self.assertTrue(backup.snapshot(Path(self.tmp.name),snapshot,True)['verified'])
            self.assertTrue(backup.restore(snapshot,restored)['verified'])
            guard=LoginGuard((restored/'email-verification.key').read_bytes())
            with connect(restored/'elvia.sqlite3') as db:
                db.execute('BEGIN IMMEDIATE')
                self.assertTrue(guard.state(db,'127.0.0.1',time.time())['locked'])
                self.assertEqual(db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchone()[0],27)


class PrivateLoginSource(unittest.TestCase):
    setUp=private_support.PrivateOriginHTTP.setUp
    tearDown=private_support.PrivateOriginHTTP.tearDown

    def test_unsigned_and_forwarded_private_login_cannot_choose_source_or_create_lock(self):
        guest=private_support.WireClient(self.server,private_support.PRIVATE,sign_private=False)
        for headers in ({},{'CF-Connecting-IP':'192.0.2.1'},{'X-Forwarded-For':'192.0.2.1'}):
            self.assertEqual(guest.call('POST','/api/auth/login',{'login':'minhao','password':'wrong'},headers)[0],403)
        with connect(self.server.db_path) as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM login_guard').fetchone()[0],0)

    def test_private_signed_source_lock_does_not_lock_distinct_loopback_source(self):
        for _ in range(10):self.private.call('POST','/api/auth/login',{'login':'minhao','password':'wrong'})
        self.assertEqual(self.private.call('POST','/api/auth/login',{'login':'minhao','password':private_support.PASSWORD})[0],429)
        self.assertEqual(self.local.call('POST','/api/auth/login',{'login':'minhao','password':private_support.PASSWORD})[0],200)


if __name__=='__main__':unittest.main()
