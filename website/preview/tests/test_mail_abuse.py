"""Mail-abuse checks use only synthetic SMTP, isolated state and test ports."""
import contextlib
import json
import importlib.util
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import shutil
import sys
import threading
import time
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs,urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'server'))
import test_local_service as base
from local_service import connect
from local_service import Handler, Problem
from mail_abuse import AbuseBudget, initialize_abuse
from email_access import MailError


class DurableMailBudget(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path=Path(self.folder.name)/'synthetic.sqlite3'
        self.guard=AbuseBudget(b'synthetic-budget-key-only')
        self.now=datetime(2026,10,25,12,tzinfo=timezone.utc).timestamp()
        with connect(self.path) as db:initialize_abuse(db)

    def reserve(self,recipient,now=None,request=False):
        with connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            method=self.guard.reserve_request if request else self.guard.reserve_mail
            return method(db,recipient,self.now if now is None else now)

    def test_recipient_cooldown_hour_day_are_normalized_shared_and_persistent(self):
        self.assertTrue(self.reserve(' PERSON@example.edu '))
        self.guard=AbuseBudget(b'synthetic-budget-key-only')
        self.assertFalse(self.reserve('person@EXAMPLE.edu',self.now+59))
        for number in range(1,5):self.assertTrue(self.reserve('person@example.edu',self.now+61*number))
        self.assertFalse(self.reserve('person@example.edu',self.now+61*5))
        for number in range(5):self.assertTrue(self.reserve('person@example.edu',self.now+3601+61*number))
        self.assertFalse(self.reserve('person@example.edu',self.now+7202))
        self.assertTrue(self.reserve('person@example.edu',self.now+86401))
        with connect(self.path) as db:
            content=json.dumps([tuple(row) for row in db.execute('SELECT * FROM abuse_mail_reservations')])
            self.assertNotIn('person',content.lower())

    def test_global_hour_day_month_and_retention_fail_closed(self):
        for number in range(20):self.assertTrue(self.reserve(f'person{number}@example.edu'))
        self.assertFalse(self.reserve('over@example.edu'))
        with connect(self.path) as db:
            db.execute('DELETE FROM abuse_mail_reservations')
            db.executemany('INSERT INTO abuse_mail_reservations VALUES(?,?)',[(str(i),self.now-7200) for i in range(80)])
        self.assertFalse(self.reserve('day@example.edu'))
        with connect(self.path) as db:
            db.execute('DELETE FROM abuse_mail_reservations')
            db.executemany('INSERT INTO abuse_mail_reservations VALUES(?,?)',[(str(i),self.now-172800) for i in range(1000)])
        self.assertFalse(self.reserve('month@example.edu'))
        november=datetime(2026,11,2,12,tzinfo=timezone.utc).timestamp()
        self.assertTrue(self.reserve('next@example.edu',november))
        with connect(self.path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM abuse_mail_reservations').fetchone()[0],1)

    def test_atomic_concurrent_distinct_and_identical_reservations_never_oversubscribe(self):
        results=[]
        barrier=threading.Barrier(25)
        def reserve(number):
            barrier.wait();results.append(self.reserve(f'person{number}@example.edu'))
        workers=[threading.Thread(target=reserve,args=(number,)) for number in range(25)]
        for worker in workers:worker.start()
        for worker in workers:worker.join()
        self.assertEqual(sum(results),20)
        with connect(self.path) as db:db.execute('DELETE FROM abuse_mail_reservations')
        results.clear();barrier=threading.Barrier(25)
        workers=[threading.Thread(target=reserve,args=(0,)) for _ in range(25)]
        for worker in workers:worker.start()
        for worker in workers:worker.join()
        self.assertEqual(sum(results),1)

    def test_unknown_request_identity_and_global_limits_bound_rows_and_survive_new_guard(self):
        for _ in range(12):self.assertTrue(self.reserve('Unknown@Example.edu',request=True))
        self.assertFalse(self.reserve('unknown@example.edu',request=True))
        self.guard=AbuseBudget(b'synthetic-budget-key-only')
        self.assertFalse(self.reserve('unknown@example.edu',request=True))
        for number in range(108):self.assertTrue(self.reserve(f'rotating{number}@example.edu',request=True))
        self.assertFalse(self.reserve('extra@example.edu',request=True))
        with connect(self.path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM abuse_requests').fetchone()[0],120)
            db.execute('DELETE FROM abuse_requests')
            db.executemany('INSERT INTO abuse_requests VALUES(?,?)',[(str(i),self.now-1800) for i in range(500)])
        self.assertFalse(self.reserve('daily@example.edu',request=True))
        self.assertTrue(self.reserve('tomorrow@example.edu',self.now+86401,request=True))
        with connect(self.path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM abuse_requests').fetchone()[0],1)

    def test_request_identity_daily_ceiling_applies_across_short_windows(self):
        for number in range(40):
            self.assertTrue(self.reserve('same@example.edu',self.now+(number//12)*901,request=True))
        self.assertFalse(self.reserve('same@example.edu',self.now+4000,request=True))

    def test_maintenance_snapshot_restore_retains_both_budgets_and_their_key(self):
        helper=Path(__file__).resolve().parents[2]/'ops/workspace_backup.py'
        spec=importlib.util.spec_from_file_location('mail_budget_backup_fixture',helper)
        backup=importlib.util.module_from_spec(spec);spec.loader.exec_module(backup)
        self.assertTrue(self.reserve('person@example.edu'))
        self.assertTrue(self.reserve('unknown@example.edu',request=True))
        source=Path(self.folder.name)/'state';source.mkdir()
        shutil.copyfile(self.path,source/'elvia.sqlite3')
        (source/'email-verification.key').write_bytes(self.guard.key)
        snapshot=Path(self.folder.name)/'snapshot';restored=Path(self.folder.name)/'restored'
        self.assertTrue(backup.snapshot(source,snapshot,True)['verified'])
        self.assertTrue(backup.restore(snapshot,restored)['verified'])
        restored_guard=AbuseBudget((restored/'email-verification.key').read_bytes())
        with connect(source/'elvia.sqlite3') as before,connect(restored/'elvia.sqlite3') as after:
            for table in ('abuse_mail_reservations','abuse_requests'):
                self.assertEqual([tuple(row) for row in before.execute('SELECT rowid,* FROM '+table)],
                                 [tuple(row) for row in after.execute('SELECT rowid,* FROM '+table)])
            after.execute('BEGIN IMMEDIATE')
            self.assertFalse(restored_guard.reserve_mail(after,'person@example.edu',self.now+59))


class MailAbuseHTTP(unittest.TestCase):
    setUp = base.ServiceContract.setUp
    tearDown = base.ServiceContract.tearDown

    def test_distinct_registration_addresses_share_one_global_send_budget(self):
        client = base.Client(self.base)
        for number in range(20):
            status, body = client.call('POST', '/api/auth/email-code', {'email':f'person{number}@example.edu'})
            self.assertEqual(status, 200, body)
        self.assertEqual(client.call('POST', '/api/auth/email-code', {'email':'over@example.edu'})[0], 429)
        self.assertEqual(len(base.TEST_MAILBOX), 20)

    def test_unknown_recovery_requests_are_durable_bounded_and_never_lock_an_account(self):
        client = base.Client(self.base)
        expected = client.call('POST', '/api/auth/password-reset/request', {'email':'missing@example.edu'})
        for _ in range(30):
            self.assertEqual(client.call('POST', '/api/auth/password-reset/request', {'email':'MISSING@EXAMPLE.EDU'}), expected)
        with connect(self.server.db_path) as db:
            rows = db.execute('SELECT identity_key,created FROM abuse_requests').fetchall()
            self.assertLessEqual(len(rows), 14)  # Two fixture staff requests plus twelve accepted identity attempts.
            self.assertNotIn('missing@example.edu', json.dumps([tuple(row) for row in rows]))
            self.assertEqual(db.execute('SELECT COUNT(*) FROM password_reset_tokens').fetchone()[0], 0)
        self.assertEqual(self.admin.call('GET', '/api/session')[1]['user']['role'], 'maintainer')

    def test_failed_smtp_attempts_consume_shared_budget_without_refunds(self):
        def fail(email,code):raise MailError('Synthetic transport failure')
        self.server.mailer.send_code=fail
        client=base.Client(self.base)
        for number in range(20):
            self.assertEqual(client.call('POST','/api/auth/email-code',{'email':f'failed{number}@example.edu'})[0],503)
        self.assertEqual(client.call('POST','/api/auth/email-code',{'email':'over@example.edu'})[0],429)
        with connect(self.server.db_path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM abuse_mail_reservations').fetchone()[0],20)

    def test_throttled_registration_keeps_the_existing_unexpired_code(self):
        client=base.Client(self.base);email='keep@example.edu'
        self.assertEqual(client.call('POST','/api/auth/email-code',{'email':email})[0],200)
        with connect(self.server.db_path) as db:
            db.execute('UPDATE email_challenges SET created=created-61')
            db.execute('UPDATE abuse_mail_reservations SET created=created-61')
            db.executemany('INSERT INTO abuse_mail_reservations VALUES(?,?)',[(str(i),time.time()) for i in range(19)])
            before=tuple(db.execute('SELECT * FROM email_challenges').fetchone())
        self.assertEqual(client.call('POST','/api/auth/email-code',{'email':email})[0],429)
        with connect(self.server.db_path) as db:
            self.assertEqual(tuple(db.execute('SELECT * FROM email_challenges').fetchone()),before)

    def test_global_throttle_keeps_existing_reset_link_redeemable(self):
        owner=self.admin.call('GET','/api/session')[1]['user']['id']
        with connect(self.server.db_path) as db:
            db.execute('INSERT INTO google_identities VALUES(?,?,?,?)',('synthetic-budget-owner',owner,'keeper@example.org','2026-10-22'))
        messages=[]
        self.server.mailer.send_password_reset=lambda email,url:messages.append(url)
        client=base.Client(self.base)
        expected=client.call('POST','/api/auth/password-reset/request',{'email':'keeper@example.org'})
        deadline=time.monotonic()+3
        while time.monotonic()<deadline:
            with connect(self.server.db_path) as db:
                if db.execute('SELECT COUNT(*) FROM password_reset_tokens WHERE sent=1').fetchone()[0]:break
            time.sleep(.01)
        self.assertEqual(len(messages),1)
        token=parse_qs(urlsplit(messages[0]).fragment)['token'][0]
        with connect(self.server.db_path) as db:
            db.execute('UPDATE password_reset_tokens SET created=created-61')
            db.execute('UPDATE abuse_mail_reservations SET created=created-61')
            db.executemany('INSERT INTO abuse_mail_reservations VALUES(?,?)',[(str(i),time.time()) for i in range(19)])
            before=tuple(db.execute('SELECT * FROM password_reset_tokens').fetchone())
        self.assertEqual(client.call('POST','/api/auth/password-reset/request',{'email':'keeper@example.org'}),expected)
        self.assertEqual(len(messages),1)
        with connect(self.server.db_path) as db:
            self.assertEqual(tuple(db.execute('SELECT * FROM password_reset_tokens').fetchone()),before)
        self.assertEqual(client.call('POST','/api/auth/password-reset/complete',{'token':token,'newpassword':'Synthetic budget replacement 42!'})[0],200)

    def test_forgot_password_spam_does_not_spend_the_accounts_login_allowance(self):
        base.ServiceContract.reviewer(self,approve=False)
        self.server.mailer.send_password_reset=lambda *args:None
        guest=base.Client(self.base)
        for _ in range(25):
            self.assertEqual(guest.call('POST','/api/auth/password-reset/request',{'email':'reviewer1@example.edu'})[0],202)
        self.assertEqual(guest.call('POST','/api/auth/login',{'login':'reviewer1@example.edu','password':'Reviewer-test-password-42'})[0],200)

    def test_memory_keys_are_hmac_bounded_without_live_key_eviction(self):
        handler=object.__new__(Handler);handler.server=self.server
        self.server.attempts.clear()
        for number in range(2048):handler.rate_limit(f'login:synthetic{number}@example.edu')
        with self.assertRaises(Problem):handler.rate_limit('login:one-more@example.edu')
        self.assertEqual(len(self.server.attempts),2048)
        self.assertNotIn('example.edu',json.dumps(self.server.attempts))
        for _ in range(11):handler.rate_limit('login:synthetic0@example.edu')
        with self.assertRaises(Problem):handler.rate_limit('login:synthetic0@example.edu')

    def test_auth_and_mail_slots_fail_closed_without_consuming_mail_budget(self):
        # Receiving the setup response can precede the handler's final release.
        # Acquire all slots before checking saturation, and unwind partial setup.
        with contextlib.ExitStack() as held:
            for _ in range(4):
                self.assertTrue(self.server.auth_slots.acquire(timeout=10))
                held.callback(self.server.auth_slots.release)
            self.assertEqual(base.Client(self.base).call('POST','/api/auth/login',{'login':'minhao','password':'Changed-test-password-42'})[0],429)
            self.assertEqual(base.Client(self.base).call('POST','/api/auth/password-reset/request',{'email':'missing@example.edu'})[0],202)
        with contextlib.ExitStack() as held:
            for _ in range(2):
                self.assertTrue(self.server.reset_mail_slots.acquire(timeout=10))
                held.callback(self.server.reset_mail_slots.release)
            self.assertEqual(base.Client(self.base).call('POST','/api/auth/email-code',{'email':'busy@example.edu'})[0],429)
        with connect(self.server.db_path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM abuse_mail_reservations').fetchone()[0],0)


if __name__ == '__main__':
    unittest.main()
