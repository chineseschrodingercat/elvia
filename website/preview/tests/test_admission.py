"""Admission policy tests: synthetic metadata, no journal pages or paper code executed."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
from admission import AdmissionEngine, unsafe_url, parse_metadata, parse_jif, parse_metric_table, fingerprint, safe_fetch, PinnedHTTPS, UnsafeDestination, FetchUnavailable


class AdmissionRules(unittest.TestCase):
    def test_crossref_title_uses_rendered_text_not_publisher_markup(self):
        engine=AdmissionEngine(fetch=lambda url,deadline:{'text':'{"message":{"title":["A C(sp<sup>3</sup>) &amp; H study"],"container-title":["Chemical Science"],"type":"journal-article"}}'})
        metadata=engine.metadata('https://doi.org/10.1234/synthetic',1000000000)
        self.assertEqual(metadata['title'],'A C(sp3) & H study')

    def setUp(self):
        self.engine = AdmissionEngine(online=False)
        self.paper = {'field':'mathematics', 'title':'A synthetic theorem about bounds',
                      'venue':'Annals of Mathematics', 'source_url':'https://doi.org/10.1234/synthetic', 'source_access':'public'}
        self.metadata = {'title':self.paper['title'], 'venue':'Annals of Mathematics', 'doi':'10.1234/synthetic',
                         'issns':['0003-486X'], 'type':'journal-article', 'identity_source':'https://api.crossref.org/works/10.1234%2Fsynthetic', 'bound_to_url':True}

    def check(self, paper=None, metadata=None, metric=None):
        return self.engine.evaluate(paper or self.paper, metadata if metadata is not None else self.metadata, metric)

    def test_identity_mismatch_never_passes_or_uses_title_search(self):
        self.assertEqual(self.check()['status'], 'pass')
        self.assertEqual(self.check(metadata={**self.metadata,'title':'An entirely different experimental paper'})['status'], 'blocked')
        self.assertNotEqual(self.check(metadata={**self.metadata,'bound_to_url':False})['status'], 'pass')
        self.assertEqual(self.check(metadata={**self.metadata,'venue':'Inventiones mathematicae','issns':[]})['status'], 'blocked')

    def test_jif_strict_threshold_latest_year_and_evidence(self):
        paper={**self.paper,'field':'chemistry','venue':'Synthetic Chemistry Journal'}
        meta={**self.metadata,'venue':paper['venue'],'issns':['1234-5678']}
        metric={'journal':paper['venue'],'issns':['1234-5678'],'year':2025,'value':10.1,'source':'https://pubs.acs.org/journal-metrics','verified_at':'2026-10-21'}
        self.assertEqual(self.check(paper,meta,metric)['status'],'pass')
        self.assertEqual(self.check(paper,meta,{**metric,'value':10.0})['status'],'blocked')
        self.assertEqual(self.check(paper,meta,{**metric,'year':2024})['status'],'pass')
        self.assertEqual(self.check(paper,meta,{**metric,'journal':'Other','issns':['2222-3333']})['status'],'blocked')
        self.assertEqual(self.check(paper,meta,None)['status'],'blocked')

    def test_ccf_current_list_main_paper_and_others(self):
        paper={**self.paper,'field':'computer_science','venue':'ICLR'}
        meta={**self.metadata,'venue':'International Conference on Learning Representations','type':'proceedings-article','paper_type':'full'}
        self.assertEqual(self.check(paper,meta)['status'],'pass')
        self.assertEqual(self.check(paper,{**meta,'paper_type':'workshop'})['status'],'blocked')
        self.assertEqual(self.check(paper,{**meta,'paper_type':'unknown'})['status'],'pending')
        self.assertEqual(self.check({**paper,'venue':'IJCAI'},{**meta,'venue':'IJCAI'})['status'],'blocked')
        self.assertEqual(self.check({**self.paper,'field':'others'})['status'],'blocked')

    def test_math_exact_catalog_and_metadata_missing(self):
        self.assertEqual(self.check({**self.paper,'venue':'Annals of Applied Mathematics'},{**self.metadata,'venue':'Annals of Applied Mathematics'})['status'],'blocked')
        self.assertEqual(self.engine.evaluate(self.paper,{},None)['status'],'pending')
        self.assertNotEqual(fingerprint(self.paper),fingerprint({**self.paper,'field':'chemistry'}))

    def test_metadata_and_metric_parsers_are_conservative(self):
        m=parse_metadata('<meta name="citation_title" content="A &amp; B"><meta name="citation_journal_title" content="Journal X"><meta name="citation_doi" content="10.1234/test">')
        self.assertEqual(m['title'],'A & B')
        self.assertEqual(m['doi'],'10.1234/test')
        self.assertEqual(parse_jif('Journal Impact Factor: 12.3 (2025)',2025),12.3)
        self.assertIsNone(parse_jif('5-year Journal Impact Factor: 19.4 (2025)',2025))
        self.assertIsNone(parse_jif('Impact Factor 2024: 99.9; CiteScore 2025: 22',2025))

    def test_unsafe_network_destinations_rejected(self):
        for url in ['http://127.0.0.1/','https://127.0.0.1/','https://[::1]/','https://localhost/','file:///etc/passwd','https://name:secret@nature.com/','https://nature.com:8443/paper','https://169.254.169.254/']:
            self.assertTrue(unsafe_url(url),url)
        self.assertFalse(unsafe_url('https://www.nature.com/articles/s41586-025-00000-0'))

    def test_metric_table_uses_the_correct_year_journal_and_column(self):
        table='<h2>2025 Journal Metrics</h2><table><tr><th>Journal</th><th>5-year Journal Impact Factor</th><th>Journal Impact Factor</th></tr><tr><td>Nature</td><td>99.2</td><td>56.1</td></tr><tr><td>Other</td><td>8.8</td><td>4.1</td></tr></table>'
        self.assertEqual(parse_metric_table(table,2025,'Nature'),56.1)
        self.assertIsNone(parse_metric_table(table,2024,'Nature'))
        self.assertIsNone(parse_metric_table(table,2025,'Unknown'))
        self.assertIsNone(parse_metric_table(table.replace('<th>Journal Impact Factor</th>','<th>CiteScore</th>'),2025,'Nature'))

    def test_dns_private_addresses_and_redirects_never_fetch_private_targets(self):
        with patch('admission.socket.getaddrinfo',return_value=[(2,1,6,'',('127.0.0.1',443))]),patch('admission.socket.create_connection') as connect:
            with self.assertRaises(UnsafeDestination):PinnedHTTPS('www.nature.com').connect()
            connect.assert_not_called()
        conn=MagicMock();response=conn.getresponse.return_value;response.status=302
        response.getheader.return_value='https://127.0.0.1/internal'
        with patch('admission.PinnedHTTPS',return_value=conn) as factory:
            with self.assertRaises(UnsafeDestination):safe_fetch('https://www.nature.com/articles/test')
            self.assertEqual(factory.call_count,1)
        with patch('admission.PinnedHTTPS') as factory:
            with self.assertRaises(FetchUnavailable):safe_fetch('https://unknown-publisher.org/article')
            factory.assert_not_called()

    def test_non_article_metadata_cannot_pass_a_journal_track(self):
        self.assertEqual(self.check(metadata={**self.metadata,'type':'posted-content'})['status'],'blocked')
        self.assertEqual(self.check(metadata={**self.metadata,'type':'dataset'})['status'],'pending')

    def test_journal_form_conference_metadata_is_held_not_falsely_rejected(self):
        paper={**self.paper,'field':'computer_science','venue':'SIGGRAPH'}
        metadata={**self.metadata,'venue':'ACM Transactions on Graphics','type':'journal-article','paper_type':'unknown'}
        self.assertEqual(self.check(paper,metadata)['status'],'pending')
        self.assertEqual(self.check({**paper,'title':'A completely unrelated biology study'},metadata)['status'],'blocked')


if __name__ == '__main__': unittest.main()
