"""Synthetic mail delivery and Google identities; no live credentials or emails."""
import sys,unittest,time,json,hashlib,threading
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'server'))
import test_local_service as baseline
from local_service import connect,stamp,uid,make_server
from email_access import eligible_email,MailError
from google_login import GoogleLoginError
from admission import AdmissionEngine,arxiv_identifier,norm,name_keys,CATALOG

class AccessV5(unittest.TestCase):
    setUp=baseline.ServiceContract.setUp
    tearDown=baseline.ServiceContract.tearDown
    reviewer=baseline.ServiceContract.reviewer
    create=baseline.ServiceContract.create
    save=baseline.ServiceContract.save
    upload=baseline.ServiceContract.upload

    def test_verified_registration_can_submit_without_reviewer_application(self):
        user=baseline.Client(self.base)
        code,result=user.call('POST','/api/auth/register',{'email':'DIRECT@EXAMPLE.EDU','name':'Test Submitter','password':'Synthetic-passphrase-48'})
        self.assertEqual(code,201,result)
        self.assertIsNone(user.call('GET','/api/me')[1]['application'])
        item=self.save(user,self.create(user,'new'),ai_used='no',ai_model='stale choice',ai_details='stale')
        self.assertEqual(item['data']['ai_model'],'')
        _,item=self.upload(user,item)
        self.assertEqual(user.call('POST',f"/api/contributions/{item['id']}/submit",{'version':item['version'],'attest':True})[0],200)
        self.assertEqual(user.call('POST','/api/contributions',{'kind':'review','task_id':'DEMO-001','conflict_clear':True})[0],403)

    def test_daily_claim_survives_release_new_browser_and_restart(self):
        user,_=self.reviewer();item=self.create(user)
        self.assertEqual(user.call('POST',f"/api/contributions/{item['id']}/release",{'version':item['version']})[0],200)
        other=baseline.Client(self.base);other.call('POST','/api/auth/login',{'login':'reviewer1@example.edu','password':'Reviewer-test-password-42'})
        self.assertEqual(other.call('POST','/api/contributions',{'kind':'review','task_id':'DEMO-002','conflict_clear':True})[0],429)
        self.assertEqual(other.call('GET','/api/me')[1]['quota']['used']['review_claim'],1)
        port=self.server.server_port
        self.server.shutdown();self.server.server_close();self.thread.join()
        self.server=make_server(Path(self.tmp.name),port)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.assertEqual(other.call('POST','/api/contributions',{'kind':'review','task_id':'DEMO-002','conflict_clear':True})[0],429)
        self.assertEqual(other.call('GET','/api/me')[1]['quota']['used']['review_claim'],1)
        with connect(self.server.db_path) as db:db.execute("UPDATE daily_usage SET day='2000-01-01'")
        self.assertEqual(other.call('POST','/api/contributions',{'kind':'review','task_id':'DEMO-002','conflict_clear':True})[0],201)

    def test_two_submissions_per_day_no_count_for_drafts_or_failed_validation(self):
        user,_=self.reviewer(approve=False)
        for index in range(3):
            item=self.save(user,self.create(user,'new'),source_url=f'https://example.org/paper-{index}')
            _,item=self.upload(user,item)
            response=user.call('POST',f"/api/contributions/{item['id']}/submit",{'version':item['version'],'attest':True})
            self.assertEqual(response[0],200 if index<2 else 429,response)
        self.assertEqual(user.call('GET','/api/me')[1]['quota']['used']['new_submit'],2)
        self.assertEqual(user.call('GET',f"/api/contributions/{item['id']}")[1]['status'],'draft')

    def test_verified_email_code_required_wrong_attempts_persist_and_replay_fails(self):
        user=baseline.Client(self.base);email='codes@example.edu'
        self.assertEqual(user.call('POST','/api/auth/email-code',{'email':email})[0],200)
        code=baseline.TEST_MAILBOX[email]
        data={'email':email,'name':'Test','password':'Synthetic-password-12','email_code':'000000' if code!='000000' else '111111'}
        for _ in range(5):self.assertEqual(user.call('POST','/api/auth/register',data)[0],400)
        self.assertEqual(user.call('POST','/api/auth/register',{**data,'email_code':code})[0],400)
        with connect(self.server.db_path) as db:self.assertEqual(db.execute('SELECT attempts FROM email_challenges WHERE email=?',(email,)).fetchone()[0],5)

    def test_email_domains_no_smtp_and_resend_limits(self):
        user=baseline.Client(self.base)
        for email in ['person@gmail.com','person@example.edu.evil.com','person@unknown.org']:
            self.assertEqual(user.call('POST','/api/auth/email-code',{'email':email})[0],400)
        self.assertEqual(user.call('POST','/api/auth/email-code',{'email':'person@example.edu'})[0],200)
        self.assertEqual(user.call('POST','/api/auth/email-code',{'email':'person@example.edu'})[0],429)
        self.server.mailer.config={}
        self.assertEqual(user.call('POST','/api/auth/email-code',{'email':'another@example.edu'})[0],503)

    def test_expired_code_and_email_switch_fail(self):
        user=baseline.Client(self.base);user.call('POST','/api/auth/email-code',{'email':'one@example.edu'})
        code=baseline.TEST_MAILBOX['one@example.edu']
        data={'email':'two@example.edu','name':'Test','password':'Synthetic-password-12','email_code':code}
        self.assertEqual(user.call('POST','/api/auth/register',data)[0],400)
        with connect(self.server.db_path) as db:db.execute('UPDATE email_challenges SET expires=0')
        self.assertEqual(user.call('POST','/api/auth/register',{**data,'email':'one@example.edu'})[0],400)

    def test_smtp_settings_are_admin_only_and_password_is_not_returned(self):
        user,_=self.reviewer()
        self.assertEqual(user.call('GET','/api/admin/email-settings')[0],403)
        data={'host':'smtp.example.org','port':465,'security':'ssl','sender':'noreply@example.org','username':'test','password':'Test-private-SMTP-secret','research_domains':['research.example.org']}
        status,result=self.admin.call('POST','/api/admin/email-settings',data)
        self.assertEqual(status,200,result);self.assertNotIn('password',result)
        self.assertNotIn(data['password'],json.dumps(self.admin.call('GET','/api/admin')[1]))
        self.assertEqual(self.admin.call('POST','/api/admin/email-settings',{**data,'research_domains':['gmail.com']})[0],400)

    def test_google_no_automatic_signup_or_role_promotion(self):
        google=self.server.google;identity={'subject':'synthetic-sub','email':'minhao@example.edu','name':'Synthetic identity'}
        with connect(self.server.db_path) as db:
            with self.assertRaises(GoogleLoginError):google.finish(db,identity,{'mode':'login'},uid,stamp)
        user,_=self.reviewer()
        self.assertEqual(user.call('POST','/api/auth/google/start',{'mode':'link','password':'Reviewer-test-password-42'})[0],403)

    def test_google_state_cookie_expiry_replay_and_pkce(self):
        google=self.server.google;google.config={'client_id':'synthetic.apps.googleusercontent.com','client_secret':'test-only','redirect_uri':self.base+'/api/auth/google/callback'}
        with connect(self.server.db_path) as db:
            url,cookie=google.start(db)
        q=parse_qs(urlsplit(url).query)
        self.assertEqual(q['code_challenge_method'],['S256']);self.assertEqual(q['scope'],['openid email profile'])
        with connect(self.server.db_path) as db:
            with self.assertRaises(GoogleLoginError):google.consume_state(db,q,'elvia_oauth=wrong')
            state=google.consume_state(db,q,cookie)
        self.assertTrue(state['verifier'])
        with connect(self.server.db_path) as db:
            with self.assertRaises(GoogleLoginError):google.consume_state(db,q,cookie)
            url,cookie=google.start(db);db.execute('UPDATE oauth_states SET expires=0')
            with self.assertRaises(GoogleLoginError):google.consume_state(db,parse_qs(urlsplit(url).query),cookie)

    def test_google_token_verification_nonce_and_audience(self):
        google=self.server.google;google.config={'client_id':'synthetic.apps.googleusercontent.com','client_secret':'test-only','redirect_uri':self.base+'/api/auth/google/callback'}
        claims={'sub':'test-sub','email':'test@example.edu','name':'Test','email_verified':True,'nonce':'expected'}
        with patch('requests.Session') as session,patch('google.oauth2.id_token.verify_oauth2_token',return_value=claims) as verify:
            session.return_value.post.return_value.status_code=200
            session.return_value.post.return_value.json.return_value={'id_token':'synthetic-signed-token'}
            identity=google.exchange('synthetic-code',{'verifier':'proof-key','nonce':'expected'})
            self.assertEqual(identity['subject'],'test-sub');self.assertEqual(verify.call_args.args[2],google.config['client_id'])
            self.assertEqual(session.return_value.post.call_args.kwargs['data']['code_verifier'],'proof-key')
            with self.assertRaises(GoogleLoginError):google.exchange('synthetic-code',{'verifier':'proof-key','nonce':'wrong'})
            verify.side_effect=ValueError('invalid signature')
            with self.assertRaises(GoogleLoginError):google.exchange('synthetic-code',{'verifier':'proof-key','nonce':'expected'})

    def test_google_link_and_callback_preserve_existing_maintainer_role(self):
        google=self.server.google;google.config={'client_id':'synthetic.apps.googleusercontent.com','client_secret':'test-only','redirect_uri':self.base+'/api/auth/google/callback'}
        google.exchange=lambda code,state:{'subject':'maintainer-sub','email':'maintainer@gmail.com','name':'Test Maintainer'}
        status,result=self.admin.call('POST','/api/auth/google/start',{'mode':'link','password':'Changed-test-password-42'})
        self.assertEqual(status,200,result)
        state=parse_qs(urlsplit(result['authorization_url']).query)['state'][0]
        self.admin.call('GET','/api/auth/google/callback?state='+state+'&code=synthetic')
        self.assertTrue(self.admin.call('GET','/api/me')[1]['google_linked'])
        other=baseline.Client(self.base)
        status,result=other.call('POST','/api/auth/google/start',{'accept_terms':True})
        self.assertEqual(status,200,result)
        state=parse_qs(urlsplit(result['authorization_url']).query)['state'][0]
        other.call('GET','/api/auth/google/callback?state='+state+'&code=synthetic')
        self.assertEqual(other.call('GET','/api/session')[1]['user']['role'],'maintainer')
        self.assertEqual(other.call('GET','/api/session')[1]['user']['login'],'minhao')

    def test_review_submission_quota_counts_distinct_papers_and_maintainer_is_exempt(self):
        user,_=self.reviewer();first=self.create(user)
        with connect(self.server.db_path) as db:db.execute("UPDATE daily_usage SET day='2000-01-01'")
        second=self.create(user,task='DEMO-002')
        for index,item in enumerate([first,second]):
            item=self.save(user,item);_,item=self.upload(user,item)
            status,result=user.call('POST',f"/api/contributions/{item['id']}/submit",{'version':item['version'],'attest':True})
            self.assertEqual(status,200 if index==0 else 429,result)
        self.assertTrue(self.admin.call('GET','/api/me')[1]['quota']['unlimited'])

class ScopeV5(unittest.TestCase):
    def test_arxiv_official_urls_identifiers_and_versions(self):
        for url in ['https://arxiv.org/abs/2401.01234v2','https://arxiv.org/pdf/2401.01234v2.pdf','https://doi.org/10.48550/arXiv.2401.01234v2','https://arxiv.org/abs/math/0309136v1']:
            self.assertTrue(arxiv_identifier(url),url)
        self.assertFalse(arxiv_identifier('https://arxiv.org.evil.example/abs/2401.01234'))
        paper={'field':'others','title':'Synthetic title','venue':'aRxIv','source_url':'https://arxiv.org/abs/2401.01234v2'}
        meta={'title':'SYNTHETIC TITLE','venue':'arXiv','type':'preprint','bound_to_url':True,'arxiv_id':'2401.01234v2'}
        engine=AdmissionEngine(False)
        self.assertEqual(engine.evaluate(paper,meta)['status'],'pass')
        self.assertNotEqual(engine.evaluate(paper,{**meta,'arxiv_id':'2401.01234v1'})['status'],'pass')
        self.assertEqual(engine.evaluate(paper,{**meta,'title':'Unrelated study on cells'})['status'],'blocked')

    def test_latest_available_metric_and_newer_known_value_precedence(self):
        paper={'field':'chemistry','title':'Synthetic title','venue':'Chemical Science','source_url':'https://doi.org/10.1234/test'}
        meta={'title':paper['title'],'venue':paper['venue'],'type':'journal-article','bound_to_url':True}
        older={'journal':'Chemical Science','value':12,'year':2021,'source':'https://www.rsc.org/publishing/journals/chemical-science'}
        result=AdmissionEngine(False).evaluate(paper,meta,older)
        self.assertEqual(result['status'],'pass');self.assertEqual(result['metric']['year'],2025)
        self.assertEqual(result['eligibility_basis'],['top_list'])
        with patch.dict(CATALOG,{'top_journals':[]}):
            self.assertEqual(AdmissionEngine(False).evaluate(paper,meta,older)['status'],'blocked')
        paper['venue']=meta['venue']='Synthetic chemistry journal';older['journal']=paper['venue']
        self.assertEqual(AdmissionEngine(False).evaluate(paper,meta,older)['status'],'pass')
        self.assertEqual(AdmissionEngine(False).evaluate(paper,meta)['status'],'blocked')

    def test_case_accent_ampersand_and_academic_domain_normalization(self):
        self.assertTrue(name_keys(' Géometry & Topology ') & name_keys('geometry and topology'))
        for email in ['Person@College.EDU','one@school.edu.cn','a@lab.ac.uk','b@sub.institute.org']:
            self.assertTrue(eligible_email(email,['institute.org']))
        self.assertFalse(eligible_email('a@school.edu.evil.com',[]))
        self.assertGreater(len(CATALOG['math_journals']),100)

if __name__=='__main__':unittest.main()
