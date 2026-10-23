"""ROR fixtures exercise failure fallback without external requests."""
import json
import unittest
from unittest.mock import patch
import requests
from institution_search import InstitutionSearch


class InstitutionSuggestions(unittest.TestCase):
    def test_fixed_ror_query_and_cache_exclude_account_data(self):
        payload={'items':[{'names':[{'value':'Fictional University','types':['ror_display']}],
                            'locations':[{'geonames_details':{'name':'Example City','country_name':'Example Country'}}]}]}
        search=InstitutionSearch()
        with patch('institution_search.requests.Session') as session:
            response=session.return_value.__enter__.return_value.get.return_value.__enter__.return_value
            response.status_code=200
            response.raw.read.return_value=json.dumps(payload).encode()
            result=search.search(' Fictional   University ')
            self.assertEqual(result['items'],[{'name':'Fictional University','location':'Example City, Example Country'}])
            get=session.return_value.__enter__.return_value.get
            self.assertEqual(get.call_args.args,('https://api.ror.org/v2/organizations',))
            self.assertEqual(get.call_args.kwargs['params'],{'query':'Fictional University'})
            self.assertFalse(get.call_args.kwargs['allow_redirects'])
            self.assertEqual(search.search('fictional university'),result)
            self.assertEqual(get.call_count,1)

    def test_failure_and_oversize_response_leave_manual_entry_available(self):
        with patch('institution_search.requests.Session') as session:
            client=session.return_value.__enter__.return_value
            client.get.side_effect=requests.Timeout('synthetic')
            self.assertEqual(InstitutionSearch().search('Fictional'),{'items':[],'available':False})
            client.get.side_effect=None
            response=client.get.return_value.__enter__.return_value
            response.status_code=200
            response.raw.read.return_value=b' ' * 1048577
            self.assertFalse(InstitutionSearch().search('Fictional')['available'])

    def test_short_queries_and_saturation_never_start_external_requests(self):
        search=InstitutionSearch()
        with patch('institution_search.requests.Session') as session:
            self.assertEqual(search.search('a')['items'],[])
            search.slots.acquire();search.slots.acquire()
            self.assertFalse(search.search('Fictional')['available'])
            session.assert_not_called()
