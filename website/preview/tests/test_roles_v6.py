"""Role boundaries use synthetic accounts and isolated databases only."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'server'))
import test_local_service as base
from admission import norm, find_venue, venue_matches


class NameMatching(unittest.TestCase):
    def test_unicode_letters_numbers_and_punctuation(self):
        self.assertEqual(norm("Élie-Cartan's Δβ_²: Notes!"), norm('elie cartans ΔΒ2 notes'))
        self.assertEqual(norm('Straße & Søren (α)'), norm('STRASSE Søren α'))
        self.assertNotEqual(norm('α Journal'),norm('β Journal'))
        self.assertNotEqual(norm('ø Journal'),norm('o Journal'))
        self.assertEqual(norm('Theoretical Biology'),'theoreticalbiology')
        self.assertEqual(norm('中文_期刊 ²'), '中文期刊2')

    def test_venue_aliases_and_collisions(self):
        entries=[{'name':'Geometry & Topology'},{'name':'Annals of Probability'}]
        self.assertEqual(find_venue('geometry and topology',entries),entries[0])
        self.assertEqual(find_venue('THE ANNALS OF PROBABILITY',entries),entries[1])
        self.assertIsNone(find_venue('A.B. Journal',[{'name':'A B Journal'},{'name':'AB Journal'}]))
        self.assertTrue(venue_matches('Søren–α_2 Review',{'venue':'søren α2 review'}))


class RolesV6(unittest.TestCase):
    setUp=base.ServiceContract.setUp
    tearDown=base.ServiceContract.tearDown
    reviewer=base.ServiceContract.reviewer
    create=base.ServiceContract.create
    save=base.ServiceContract.save
    upload=base.ServiceContract.upload

    def reserve(self,email,role='admin',client=None,password='Changed-test-password-42'):
        return (client or self.admin).call('POST','/api/admin/roles',{'email':email,'role':role,'password':password})

    def staff(self,number=20,role='admin'):
        email=f'staff{number}@example.edu'
        status,result=self.reserve(email,role);self.assertEqual(status,200,result)
        client=base.Client(self.base)
        status,result=client.call('POST','/api/auth/register',{'email':email,'name':f'Fictional {role} {number}','password':'Staff-test-password-42','accept_terms':True})
        self.assertEqual(status,201,result);self.assertEqual(result['user']['role'],role)
        return client,result['user']['id'],email

    def test_reserved_role_requires_verified_email_and_client_role_is_ignored(self):
        status,result=self.reserve('STAFF20@EXAMPLE.EDU');self.assertEqual(status,200,result)
        client=base.Client(self.base)
        status,result=client.call('POST','/api/auth/register',{'email':'staff20@example.edu','name':'Synthetic admin','password':'Staff-test-password-42','accept_terms':True,'email_code':'111111'})
        self.assertEqual(status,400,result)
        status,result=client.call('POST','/api/auth/register',{'email':'staff20@example.edu','name':'Synthetic admin','password':'Staff-test-password-42','accept_terms':True})
        self.assertEqual(status,201,result);self.assertEqual(result['user']['role'],'admin')
        other=base.Client(self.base)
        status,result=other.call('POST','/api/auth/register',{'email':'ordinary@example.edu','name':'Synthetic ordinary','password':'Staff-test-password-42','role':'maintainer','accept_terms':True})
        self.assertEqual(result['user']['role'],'reviewer')

    def test_admin_unlimited_contributions_and_management_but_no_final_or_settings(self):
        admin,_,_=self.staff()
        self.assertTrue(admin.call('GET','/api/me')[1]['quota']['unlimited'])
        for index in range(3):
            item=self.save(admin,self.create(admin,'new'),source_url=f'https://example.org/paper-{index}')
            _,item=self.upload(admin,item)
            status,result=admin.call('POST',f"/api/contributions/{item['id']}/submit",{'version':item['version'],'attest':True})
            self.assertEqual(status,200,result)
        reviewer,_=self.reviewer(approve=False)
        item=self.save(reviewer,self.create(reviewer,'new'))
        self.assertEqual(admin.call('GET',f"/api/contributions/{item['id']}")[0],200)
        data={**item['data'],'summary':'Synthetic ordinary revision of the local interface fixture only.'}
        status,result=admin.call('POST',f"/api/admin/contributions/{item['id']}/revisions",{'version':item['version'],'mode':'ordinary','data':data})
        self.assertEqual(status,200,result)
        status,result=admin.call('POST',f"/api/admin/contributions/{item['id']}/revisions",{'version':result['version'],'mode':'final','data':data})
        self.assertEqual(status,403,result)
        self.assertEqual(admin.call('GET','/api/admin/email-settings')[0],403)
        self.assertEqual(self.reserve('escalation@example.edu','maintainer',admin,'Staff-test-password-42')[0],403)
        self.assertEqual(admin.call('POST','/api/auth/google/start',{'mode':'link','password':'wrong-password'})[0],403)
        self.assertEqual(admin.call('POST','/api/auth/google/start',{'mode':'link','password':'Staff-test-password-42'})[0],503)

    def test_admin_suspension_revokes_sessions_and_blocks_login_without_deleting_work(self):
        admin,_,_=self.staff();reviewer,user_id=self.reviewer()
        item=self.save(reviewer,self.create(reviewer,'new'))
        status,result=admin.call('POST',f'/api/admin/accounts/{user_id}/status',{'status':'suspended','note':'Repeated synthetic misuse fixture.'})
        self.assertEqual(status,200,result)
        self.assertEqual(reviewer.call('GET','/api/me')[0],401)
        self.assertEqual(reviewer.call('POST','/api/auth/login',{'login':'reviewer1@example.edu','password':'Reviewer-test-password-42'})[0],403)
        self.assertEqual(admin.call('GET',f"/api/contributions/{item['id']}")[0],200)
        self.assertEqual(admin.call('POST',f'/api/admin/accounts/{user_id}/status',{'status':'active','note':'Synthetic issue resolved.'})[0],200)
        self.assertEqual(reviewer.call('GET','/api/me')[0],401)
        self.assertEqual(reviewer.call('POST','/api/auth/login',{'login':'reviewer1@example.edu','password':'Reviewer-test-password-42'})[0],200)

    def test_hierarchy_peer_isolation_and_maintainer_control_of_admin(self):
        admin,admin_id,admin_email=self.staff()
        peer,peer_id,_=self.staff(21)
        maintainer,maintainer_id,maintainer_email=self.staff(22,'maintainer')
        for target in (admin_id,peer_id,maintainer_id):
            self.assertEqual(admin.call('POST',f'/api/admin/accounts/{target}/status',{'status':'suspended','note':'Synthetic permission probe.'})[0],403)
        self.assertEqual(self.admin.call('POST',f'/api/admin/accounts/{maintainer_id}/status',{'status':'suspended','note':'Synthetic permission probe.'})[0],403)
        self.assertEqual(self.reserve(maintainer_email,'reviewer')[0],403)
        item=self.save(maintainer,self.create(maintainer,'new'))
        _,item=self.upload(maintainer,item)
        for actor in (self.admin,admin):
            self.assertEqual(actor.call('GET',f"/api/contributions/{item['id']}")[0],403)
            self.assertEqual(actor.call('GET',f"/api/packages/{item['package']['id']}")[0],403)
            self.assertNotIn(item['id'],[x['id'] for x in actor.call('GET','/api/admin')[1]['contributions']])
        self.assertEqual(self.admin.call('POST',f'/api/admin/accounts/{admin_id}/status',{'status':'suspended','note':'Synthetic admin suspension.'})[0],200)
        self.assertEqual(self.admin.call('POST',f'/api/admin/accounts/{admin_id}/status',{'status':'active','note':'Synthetic admin reactivation.'})[0],200)
        self.assertEqual(self.reserve(admin_email,'reviewer')[0],200)
        status,result=admin.call('POST','/api/auth/login',{'login':admin_email,'password':'Staff-test-password-42'})
        self.assertEqual(result['user']['role'],'reviewer')

    def test_account_directory_has_no_secrets_and_role_changes_require_password(self):
        admin,_,email=self.staff();reviewer,user_id=self.reviewer()
        status,result=self.admin.call('GET','/api/admin/accounts')
        self.assertEqual(status,200,result)
        account=next(x for x in result['accounts'] if x['id']==user_id)
        self.assertTrue(account['email_verified'])
        self.assertFalse({'password','csrf','token','google_subject'} & set(account))
        self.assertEqual(self.reserve(email,'reviewer',password='wrong')[0],403)
        self.assertEqual(reviewer.call('GET','/api/admin/accounts')[0],403)

    def test_admin_reviews_others_but_does_not_accept_own_work(self):
        admin,_,_=self.staff()
        reviewer,user_id=self.reviewer(approve=False)
        self.assertEqual(admin.call('POST',f'/api/admin/applications/{user_id}',{'decision':'approved','note':'Synthetic background checked.'})[0],200)
        for author,expected in ((admin,403),(reviewer,200)):
            item=self.save(author,self.create(author,'new'),source_url=f'https://example.org/role-decision-{expected}')
            _,item=self.upload(author,item)
            status,item=author.call('POST',f"/api/contributions/{item['id']}/submit",{'version':item['version'],'attest':True})
            self.assertEqual(status,200,item)
            status,result=admin.call('POST',f"/api/admin/contributions/{item['id']}/decision",{'version':item['version'],'decision':'accepted','note':'Synthetic interface fixture accepted.'})
            self.assertEqual(status,expected,result)
            if expected==200:
                credit=reviewer.call('GET',f"/api/credit/{item['id']}")[1]
                self.assertEqual(credit['issuer'],'ELVIA')


if __name__=='__main__':unittest.main()
