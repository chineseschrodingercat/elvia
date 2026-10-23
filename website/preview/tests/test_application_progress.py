"""Applicant transitions use isolated state and captured mail only."""
import unittest
import threading
from unittest.mock import patch

import test_local_service as base
from local_service import connect


class ApplicationProgress(unittest.TestCase):
    setUp = base.ServiceContract.setUp
    tearDown = base.ServiceContract.tearDown
    reviewer = base.ServiceContract.reviewer

    def register(self):
        client = base.Client(self.base)
        status, result = client.call('POST', '/api/auth/register', {
            'name': 'Synthetic Applicant', 'email': 'progress@example.edu',
            'password': 'Synthetic-password-42',
        })
        self.assertEqual(status, 201, result)
        return client, result['user']['id']

    def test_expertise_is_optional_and_five_selections_include_other(self):
        client, _ = self.register()
        profile = {'position': 'Graduate student', 'institution': 'Fictional University'}
        status, result = client.call('POST', '/api/application', profile)
        self.assertEqual(status, 200, result)
        app = client.call('GET', '/api/me')[1]['application']
        self.assertEqual(app['profile']['expertise_fields'], [])

    def test_more_than_five_fields_and_invalid_profile_type_are_rejected(self):
        client, _ = self.register()
        profile = {'position': 'Graduate student', 'institution': 'Fictional University',
                   'expertise': 'legacy text',
                   'expertise_fields': ['Algebra', 'Topology', 'Statistics', 'Genetics', 'Optics', 'Other'],
                   'expertise_other': 'Synthetic specialty'}
        self.assertEqual(client.call('POST', '/api/application', profile)[0], 400)
        profile.update(expertise_fields=[], profile_type='Invalid choice')
        self.assertEqual(client.call('POST', '/api/application', profile)[0], 400)
        self.assertIsNone(client.call('GET', '/api/me')[1]['application'])

    def test_opening_one_application_changes_only_that_application_and_queues_once(self):
        client, uid = self.reviewer(approve=False)
        self.admin.call('GET', '/api/admin')
        self.assertEqual(client.call('GET', '/api/me')[1]['application']['status'], 'pending')
        route = '/api/admin/applications/' + uid + '/open'
        self.assertEqual(client.call('POST', route, {})[0], 403)
        for _ in range(2):
            status, result = self.admin.call('POST', route, {})
            self.assertEqual(status, 200, result)
        app = client.call('GET', '/api/me')[1]['application']
        self.assertEqual(app['status'], 'under_review')
        self.assertEqual([x['status'] for x in app['timeline']], ['pending', 'under_review'])
        for _ in range(2):
            self.assertEqual(self.admin.call('POST', '/api/admin/applications/' + uid,
                                           {'decision': 'approved', 'note': 'Synthetic decision'})[0], 200)
        with connect(self.server.db_path) as db:
            notices = list(db.execute('SELECT status FROM application_notifications ORDER BY event_id'))
        self.assertEqual([r['status'] for r in notices], ['pending', 'under_review', 'approved'])

    def test_pending_submission_cannot_be_reset_or_spam_notifications(self):
        client, _ = self.reviewer(approve=False)
        before = client.call('GET', '/api/me')[1]['application']
        status, result = client.call('POST', '/api/application', before['profile'])
        self.assertEqual(status, 409, result)
        self.assertEqual(client.call('GET', '/api/me')[1]['application'], before)

    def test_failed_delivery_survives_restart_and_keeps_transition_order(self):
        from application_workflow import deliver_one
        client, uid = self.reviewer(approve=False)
        self.admin.call('POST', '/api/admin/applications/' + uid + '/open', {})
        calls = []
        def fail(*args):
            raise OSError('synthetic transport failure')
        self.server.mailer.send_application_update = fail
        self.assertTrue(deliver_one(self.server.db_path, self.server.mailer, now=100000000000))
        with connect(self.server.db_path) as db:
            rows = list(db.execute('SELECT sent_at, attempts FROM application_notifications ORDER BY event_id'))
        self.assertEqual([(r['sent_at'], r['attempts']) for r in rows], [(None, 1), (None, 0)])
        self.server.mailer.send_application_update = lambda *args: calls.append(args)
        self.assertTrue(deliver_one(self.server.db_path, self.server.mailer, now=100000001000))
        self.assertTrue(deliver_one(self.server.db_path, self.server.mailer, now=100000001000))
        self.assertFalse(deliver_one(self.server.db_path, self.server.mailer, now=100000001000))
        self.assertEqual([args[1] for args in calls], ['pending', 'under_review'])
        self.assertTrue(all(args[0].endswith('@example.edu') for args in calls))

    def test_old_application_rows_are_preserved_by_additive_migration(self):
        from application_workflow import migrate
        client, _ = self.reviewer(approve=False)
        with connect(self.server.db_path) as db:
            before = [tuple(r) for r in db.execute('SELECT * FROM applications')]
            migrate(db)
            migrate(db)
            self.assertEqual(before, [tuple(r) for r in db.execute('SELECT * FROM applications')])
        self.assertEqual(client.call('GET', '/api/me')[0], 200)

    def test_five_selections_round_trip_and_information_request_allows_resubmission(self):
        client, uid = self.register()
        data = {'position':'Graduate student','institution':'Fictional University',
                'expertise_fields':['Algebra','Topology','Statistics','Genetics','Other'],
                'expertise_other':'Synthetic specialty','profile_type':'ORCID',
                'profile_url':'https://orcid.org/0000-0000-0000-0000'}
        self.assertEqual(client.call('POST','/api/application',data)[0],200)
        app=client.call('GET','/api/me')[1]['application']
        self.assertEqual(app['profile']['expertise_fields'],data['expertise_fields'])
        self.admin.call('POST','/api/admin/applications/'+uid,{'decision':'needs_information','note':'Synthetic clarification requested'})
        data.update(expertise_fields=[],expertise_other='')
        self.assertEqual(client.call('POST','/api/application',data)[0],200)
        self.assertEqual([x['status'] for x in client.call('GET','/api/me')[1]['application']['timeline']],['pending'])
        with connect(self.server.db_path) as db:
            self.assertEqual([r[0] for r in db.execute('SELECT status FROM application_notifications ORDER BY event_id')],['pending','needs_information','pending'])

    def test_mail_content_is_stage_specific_and_escapes_decision_notes(self):
        mail=self.server.mailer
        with patch.object(mail,'_send') as send:
            for stage in ['pending','under_review','approved','needs_information','declined']:
                mail.send_application_update('synthetic@example.edu',stage,'<script>synthetic</script>',123)
                message=send.call_args.args[0]
                text=message.get_body(preferencelist=('plain',)).get_content()
                html=message.get_body(preferencelist=('html',)).get_content()
                self.assertIn('https://elvia-atlas.org/contribute.html?view=my-work',text)
                self.assertNotIn('<script>',html)
                self.assertEqual(str(message['Message-ID']),'<application-123@example.org>')
                if stage=='pending':self.assertIn('1–3 days',text)
                if stage=='under_review':self.assertIn('awaiting a decision',text)

    def test_concurrent_delivery_cannot_send_the_same_transition_twice(self):
        from application_workflow import deliver_one
        self.reviewer(approve=False)
        started,release=threading.Event(),threading.Event()
        calls=[]
        def blocked(*args):
            calls.append(args);started.set();release.wait(10)
        self.server.mailer.send_application_update=blocked
        worker=threading.Thread(target=deliver_one,args=(self.server.db_path,self.server.mailer))
        worker.start()
        try:
            self.assertTrue(started.wait(10))
            self.assertFalse(deliver_one(self.server.db_path,self.server.mailer))
        finally:
            release.set();worker.join(10)
        self.assertEqual(len(calls),1)

    def test_stale_staff_decision_rejected_without_changing_current_status(self):
        client,uid=self.reviewer(approve=False)
        version=client.call('GET','/api/me')[1]['application']['version']
        self.admin.call('POST','/api/admin/applications/'+uid+'/open',{})
        result=self.admin.call('POST','/api/admin/applications/'+uid,{'decision':'approved','note':'Synthetic','version':version})
        self.assertEqual(result[0],409)
        self.assertEqual(client.call('GET','/api/me')[1]['application']['status'],'under_review')
