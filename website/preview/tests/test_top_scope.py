"""TOP eligibility uses synthetic catalog records, never claimed scientific reviews."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
from admission import AdmissionEngine, CATALOG


class TopScopeRules(unittest.TestCase):
    def setUp(self):
        self.engine = AdmissionEngine(online=False)
        self.paper = {'field':'chemistry', 'title':'Synthetic intake test',
                      'venue':'Synthetic Journal', 'source_url':'https://doi.org/10.1234/synthetic', 'source_access':'public'}
        self.meta = {'title':self.paper['title'], 'venue':self.paper['venue'],
                     'issns':[], 'type':'journal-article', 'bound_to_url':True}
        self.top = {'name':'Synthetic Journal', 'aliases':['Syn J'], 'year':2026,
                    'edition':'xr-2026', 'zone':1, 'top':True,
                    'source':'https://aarongig.github.io/xr-journal-query/'}
        self.policy = {'year':2026, 'edition':'xr-2026', 'refresh_due':'2027-06-01'}
        self.metric = {'journal':self.paper['venue'], 'year':2025, 'value':8.1,
                       'source':'https://pubs.acs.org/journal-metrics'}

    def result(self, top=None, metric=None, paper=None, meta=None):
        with patch.dict(CATALOG, {'top_policy':self.policy, 'top_journals':[top or self.top]}):
            return self.engine.evaluate(paper or self.paper, meta or self.meta, metric)

    def test_top_is_an_alternative_to_missing_or_low_jif_in_both_fields(self):
        for field in ('chemistry', 'biological_science'):
            for metric in (None, self.metric, {**self.metric,'value':10.0}):
                result = self.result(metric=metric, paper={**self.paper,'field':field})
                self.assertEqual(result['status'], 'pass', result)
                self.assertEqual(result['eligibility_basis'], ['top_list'])
                self.assertEqual(result['top_record']['year'], 2026)
                self.assertTrue(any('TOP' in e['label'] for e in result['evidence']))

    def test_zone_one_and_top_and_selected_edition_are_all_required(self):
        for changes in ({'top':False}, {'zone':2}, {'year':2025}, {'edition':'cas-2025'}, {'source':''}):
            self.assertEqual(self.result(top={**self.top,**changes})['status'], 'blocked', changes)
        self.assertEqual(self.result(top={**self.top,'top':False},metric={**self.metric,'value':10.1})['status'], 'pass')

    def test_metadata_identity_and_case_alias_matching_remain_required(self):
        self.assertEqual(self.result(paper={**self.paper,'venue':' sYn. j '})['status'], 'pass')
        self.assertEqual(self.result(meta={**self.meta,'title':'A different paper entirely'})['status'], 'blocked')
        self.assertEqual(self.result(meta={**self.meta,'venue':'Another Journal'})['status'], 'blocked')
        self.assertEqual(self.result(meta={**self.meta,'bound_to_url':False})['status'], 'pending')
        self.assertEqual(self.result(meta={**self.meta,'type':'preprint'})['status'], 'blocked')

    def test_top_does_not_open_closed_or_other_tracks_or_accept_client_flags(self):
        for field in ('others','computer_science','mathematics'):
            self.assertEqual(self.result(paper={**self.paper,'field':field})['status'], 'blocked')
        self.assertEqual(self.result(top={**self.top,'name':'Unrelated'},paper={**self.paper,'top':True,'zone':1})['status'], 'blocked')

    def test_both_routes_and_expired_list_are_distinguished(self):
        self.assertEqual(self.result(metric={**self.metric,'value':10.1})['eligibility_basis'], ['jif','top_list'])
        self.policy['refresh_due'] = '2026-01-01'
        self.assertEqual(self.result()['status'], 'pending')
        self.assertEqual(self.result(metric={**self.metric,'value':10.1})['status'], 'pass')


if __name__ == '__main__':
    unittest.main()
