"""Conservative, evidence-bearing intake checks. No LLM, private files or title search.

Network requests only retrieve public bibliographic/metric records. Unavailable
evidence produces a hold, never a fabricated match or a silent approval.
"""
from __future__ import annotations
import hashlib
import html
import http.client
import ipaddress
import json
import re
import socket
import ssl
import threading
import time
import unicodedata
import xml.etree.ElementTree as ET
from datetime import date, datetime, timezone
from difflib import SequenceMatcher
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urljoin, urlsplit

CATALOG = json.loads((Path(__file__).parent/'catalogs/admission-2026.json').read_text('utf-8'))
TRUSTED_HOSTS = {
 'doi.org','dx.doi.org','api.crossref.org','api.openreview.net','api2.openreview.net','openreview.net',
 'nature.com','www.nature.com','pubs.acs.org','pubs.rsc.org','www.rsc.org','blogs.rsc.org',
 'onlinelibrary.wiley.com','chemistry-europe.onlinelibrary.wiley.com','advanced.onlinelibrary.wiley.com',
 'cell.com','www.cell.com','science.org','www.science.org','sciencedirect.com','www.sciencedirect.com',
 'link.springer.com','academic.oup.com','www.pnas.org','pnas.org',
 'www.tandfonline.com','tandfonline.com','www.annualreviews.org','journals.plos.org','elifesciences.org',
 'www.mdpi.com','aacrjournals.org','www.embopress.org','rupress.org',
 'papers.nips.cc','papers.neurips.cc','proceedings.neurips.cc','proceedings.mlr.press','openaccess.thecvf.com',
 'aclanthology.org','ojs.aaai.org','dl.acm.org','ieeexplore.ieee.org','www.usenix.org','usenix.org',
 'drops.dagstuhl.de','www.vldb.org','vldb.org','www.ndss-symposium.org',
 'annals.math.princeton.edu','www.ams.org','ams.org','ems.press','msp.org','www.intlpress.com','intlpress.com',
 'projecteuclid.org','www.cambridge.org','cambridge.org','www.numdam.org','numdam.org',
 'epubs.siam.org','pubsonline.informs.org','iopscience.iop.org','www.degruyterbrill.com','www.degruyter.com',
 'imstat.org','www.jstor.org','jstor.org','www.jmlr.org','jmlr.org',
 'arxiv.org','www.arxiv.org','export.arxiv.org',
}
METRIC_HOSTS = TRUSTED_HOSTS | {'clarivate.com','www.clarivate.com','jcr.clarivate.com','api.clarivate.com','bsky.app'}

def now(): return datetime.now(timezone.utc).isoformat(timespec='seconds')
def norm(value):
    value = html.unescape(re.sub(r'</?[a-zA-Z][^>]*>', '', value))
    value = unicodedata.normalize('NFKD', value).casefold()
    return ''.join(c for c in value if c.isalnum())

def name_keys(value):
    variants=[value,re.sub(r'^\s*the\s+','',value,flags=re.I)]
    return {norm(v) for value in variants for v in (value,value.replace('&',' and ')) if norm(v)}

def fingerprint(record):
    fields={k:record.get(k,'') for k in ('title','venue','field','source_url','source_access')}
    fields['policy']=CATALOG['version']
    return hashlib.sha256(json.dumps(fields,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def arxiv_identifier(url):
    """Recognize official modern/legacy arXiv URLs and arXiv DOI aliases only."""
    try:
        p=urlsplit(url.strip()); host=(p.hostname or '').lower()
        if p.scheme.lower()!='https' or p.username or p.password or p.port not in (None,443):return ''
        path=unquote(p.path)
        if host in ('arxiv.org','www.arxiv.org','export.arxiv.org'):
            match=re.fullmatch(r'/(?:abs|pdf|html)/(.+?)(?:\.pdf)?/?',path,re.I)
        elif host in ('doi.org','dx.doi.org'):
            match=re.fullmatch(r'/10\.48550/arxiv\.(.+)',path,re.I)
        else:return ''
        value=match[1] if match else ''
        return value if re.fullmatch(r'(?:\d{4}\.\d{4,5}|[a-z][a-z.\-]+/\d{7})(?:v[1-9]\d*)?',value,re.I) else ''
    except (ValueError,TypeError):return ''

def unsafe_url(value):
    try:
        p=urlsplit(value); host=(p.hostname or '').lower()
        if p.scheme!='https' or not host or p.username or p.password or p.port not in (None,443):return True
        if any(ord(c)<33 for c in value) or '\\' in value or host.endswith('.') or host=='localhost' or '.' not in host:return True
        try: ipaddress.ip_address(host); return True
        except ValueError: pass
        return host.endswith(('.localhost','.local','.internal','.test'))
    except (ValueError,TypeError):return True

class FetchUnavailable(Exception): pass
class UnsafeDestination(FetchUnavailable): pass

class PinnedHTTPS(http.client.HTTPSConnection):
    def connect(self):
        try: addresses=socket.getaddrinfo(self.host,443,type=socket.SOCK_STREAM)
        except OSError as exc:raise FetchUnavailable('The source could not be reached.') from exc
        if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
            raise UnsafeDestination('The source resolves to a non-public address.')
        # Connect to the checked address, while authenticating TLS against the original host.
        address=addresses[0][4][0]
        raw=socket.create_connection((address,443),self.timeout)
        self.sock=self._context.wrap_socket(raw,server_hostname=self.host)

def safe_fetch(url, deadline=None):
    deadline=deadline or time.monotonic()+10
    for _ in range(5):
        if unsafe_url(url):raise UnsafeDestination('Use a public HTTPS publisher or DOI link.')
        p=urlsplit(url)
        if p.hostname.lower() not in TRUSTED_HOSTS:raise FetchUnavailable('This publisher needs manual source verification.')
        remaining=deadline-time.monotonic()
        if remaining<=0:raise FetchUnavailable('The source check timed out.')
        connection=PinnedHTTPS(p.hostname,timeout=min(3.5,remaining),context=ssl.create_default_context())
        try:
            connection.request('GET',p.path+('?' + p.query if p.query else ''),headers={'User-Agent':'ELVIA-Local-Intake/1.0 (public bibliographic metadata)','Accept':'application/json,text/html;q=0.9','Accept-Encoding':'identity'})
            response=connection.getresponse()
            if response.status in (301,302,303,307,308):
                target=response.getheader('Location')
                if not target:raise FetchUnavailable('The source redirect is incomplete.')
                url=urljoin(url,target);continue
            if response.status!=200:raise FetchUnavailable(f'The source returned HTTP {response.status}; manual verification is needed.')
            if response.getheader('Content-Encoding','identity') not in ('identity',''):raise FetchUnavailable('Unsupported source encoding.')
            raw=response.read(2_000_001)
            if len(raw)>2_000_000:raise FetchUnavailable('The source page exceeds the metadata size limit.')
            kind=response.getheader('Content-Type','')
            if not any(x in kind for x in ('html','json','text/plain','xml')):raise FetchUnavailable('Use the article landing page, not a PDF download.')
            return {'text':raw.decode('utf-8','replace'),'url':url,'content_type':kind}
        except (OSError,http.client.HTTPException) as exc:raise FetchUnavailable('The public source could not be read.') from exc
        finally:connection.close()
    raise FetchUnavailable('The source has too many redirects.')

class MetadataParser(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.values={}
    def handle_starttag(self,tag,attrs):
        if tag!='meta':return
        a=dict(attrs);key=(a.get('name') or a.get('property') or '').lower()
        if key.startswith(('citation_','dc.','prism.')):self.values.setdefault(key,[]).append(a.get('content',''))

def parse_metadata(text):
    p=MetadataParser();p.feed(text)
    def first(*keys):return next((p.values[k][0] for k in keys if p.values.get(k)), '')
    doi=first('citation_doi','dc.identifier','prism.doi').removeprefix('doi:').strip()
    if doi.startswith('https://doi.org/'):doi=doi[16:]
    return {'title':first('citation_title','dc.title'),'venue':first('citation_journal_title','citation_conference_title','prism.publicationname'),
            'doi':doi if re.fullmatch(r'10\.\d{4,9}/\S+',doi) else '', 'issns':p.values.get('citation_issn',[]),
            'type':'proceedings-article' if first('citation_conference_title') else 'journal-article','paper_type':'unknown'}

def parse_jif(text,year):
    text=html.unescape(re.sub('<[^>]+>',' ',text))
    text=re.sub(r'\s+',' ',text)
    # Do not confuse five-year JIF, CiteScore, an earlier year or an unlabelled number.
    pattern=rf'(?<![\w-])(?:Two-Year\s+)?Journal Impact Factor(?:™)?\s*:?\s*(\d+(?:\.\d+)?)\s*\({year}\)'
    for match in re.finditer(pattern,text,re.I):
        if re.search(r'(?:5|five)[ -]year\s*$',text[max(0,match.start()-16):match.start()],re.I):continue
        return float(match[1])
    return None

class MetricTableParser(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.rows=[];self.row=[];self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag=='tr':self.row=[]
        elif tag in ('td','th'):self.cell=[]
    def handle_data(self,text):
        if self.cell is not None:self.cell.append(text)
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.cell is not None:self.row.append(' '.join(''.join(self.cell).split()));self.cell=None
        elif tag=='tr' and self.row:self.rows.append(self.row)

def parse_metric_table(text,year,journal):
    plain=' '.join(html.unescape(re.sub('<[^>]+>',' ',text)).split())
    if not re.search(rf'\b{year}\s+Journal Metrics\b',plain,re.I):return None
    parser=MetricTableParser();parser.feed(text);jif_column=None
    for row in parser.rows:
        if any('Impact Factor' in c for c in row):
            jif_column=next((i for i,c in enumerate(row) if norm(c)=='journalimpactfactor'),None)
            continue
        if jif_column is not None and len(row)>jif_column and norm(row[0])==norm(journal):
            try:return float(row[jif_column])
            except ValueError:return None
    return None

def find_venue(name,entries):
    keys=name_keys(name)
    matches=[v for v in entries if any(keys & name_keys(s) for s in [v['name'],v.get('full_name',''),*v.get('aliases',[])])]
    return matches[0] if len(matches)==1 else None

def venue_matches(submitted, metadata, entry=None):
    actual=norm(metadata.get('venue',''))
    names=[submitted]+([entry['name'],entry.get('full_name',''),*entry.get('aliases',[])] if entry else [])
    if any(name_keys(metadata.get('venue','')) & name_keys(x) for x in names if x):return True
    if entry and set(entry.get('issns',[])) & set(metadata.get('issns',[])):return True
    if entry and entry.get('rank')=='A':
        # A long full conference name inside a deposited proceedings title is useful.
        return any(len(norm(x))>22 and norm(x) in actual for x in names if x)
    return False

def metric_matches(record,metadata):
    return bool(name_keys(record.get('journal','')) & name_keys(metadata.get('venue',''))) or bool(set(record.get('issns',[]))&set(metadata.get('issns',[])))

def top_journal(name):
    policy=CATALOG.get('top_policy',{})
    entry=find_venue(name,CATALOG.get('top_journals',[]))
    if entry and entry.get('zone')==1 and entry.get('top') is True and entry.get('year')==policy.get('year') and entry.get('edition')==policy.get('edition') and not unsafe_url(entry.get('source','')):
        return entry
    return None

class AdmissionEngine:
    def __init__(self,online=True,fetch=None):
        self.online=online;self.fetch=fetch or safe_fetch;self.slots=threading.BoundedSemaphore(2)
        self.cache={};self.cache_lock=threading.Lock()

    def public_policy(self):
        return {k:v for k,v in CATALOG.items() if k!='metric_records'} | {'metric_records':[{k:v for k,v in x.items() if k!='method'} for x in CATALOG['metric_records']], 'jif_threshold':10,'conference_papers':'Full or regular main-conference papers only','math_policy':'Expanded ELVIA journal selection, not a universal ranking'}

    def _get(self,url,deadline):
        with self.cache_lock:
            cached=self.cache.get(url)
            if cached and cached[0]>time.time():return cached[1]
        result=self.fetch(url,deadline)
        with self.cache_lock:
            if len(self.cache)>500:self.cache.clear()
            self.cache[url]=(time.time()+86400,result)
        return result

    def metadata(self,url,deadline):
        p=urlsplit(url);host=p.hostname.lower();doi='';page={};link_bound=False
        arxiv_id=arxiv_identifier(url)
        if arxiv_id:
            canonical='https://arxiv.org/abs/'+arxiv_id
            # The abstract page is small and avoids downloading the paper itself.
            try:
                page=self._get(canonical,deadline);meta=parse_metadata(page['text'])
                parser=MetadataParser();parser.feed(page['text'])
                actual=(parser.values.get('citation_arxiv_id') or [''])[0]
                same=actual and re.sub(r'v\d+$','',actual).casefold()==re.sub(r'v\d+$','',arxiv_id).casefold()
                if re.search(r'v\d+$',arxiv_id):same=same and actual.casefold()==arxiv_id.casefold()
                if meta['title'] and same:
                    return {**meta,'venue':'arXiv','type':'preprint','arxiv_id':actual,'bound_to_url':True,'identity_source':canonical,'canonical_url':canonical}
            except FetchUnavailable:pass
            source='https://export.arxiv.org/api/query?id_list='+quote(arxiv_id,safe='')
            tree=ET.fromstring(self._get(source,deadline)['text']);ns={'a':'http://www.w3.org/2005/Atom'}
            entry=tree.find('a:entry',ns)
            if entry is None:raise FetchUnavailable('The arXiv record was not found.')
            actual=(entry.findtext('a:id','',ns)).split('/abs/')[-1]
            same=re.sub(r'v\d+$','',actual).casefold()==re.sub(r'v\d+$','',arxiv_id).casefold()
            if re.search(r'v\d+$',arxiv_id):same=same and actual.casefold()==arxiv_id.casefold()
            return {'title':' '.join(entry.findtext('a:title','',ns).split()),'venue':'arXiv','type':'preprint','arxiv_id':actual,'bound_to_url':same,'identity_source':source,'canonical_url':canonical,'issns':[]}
        if host in ('doi.org','dx.doi.org'):doi=unquote(p.path.lstrip('/'));link_bound=True
        elif host in ('nature.com','www.nature.com') and re.fullmatch(r'/articles/[^/]+',p.path):doi='10.1038/'+p.path.rsplit('/',1)[1]
        else:
            match=re.search(r'/doi/(?:abs/|full/|pdf/|epdf/)?(10\.\d{4,9}/[^?#]+)',url)
            if match:doi=unquote(match[1])
        if host=='openreview.net':
            paper_id=parse_qs(p.query).get('id',[''])[0]
            if not re.fullmatch(r'[\w-]{5,100}',paper_id):raise FetchUnavailable('Use the specific published OpenReview paper page.')
            source='https://api2.openreview.net/notes?id='+quote(paper_id)
            notes=json.loads(self._get(source,deadline)['text']).get('notes',[])
            if not notes:raise FetchUnavailable('No published OpenReview record was found.')
            item=notes[0];content=item.get('content',{})
            def value(key):
                x=content.get(key,'');return x.get('value','') if isinstance(x,dict) else x
            venue_id=str(value('venueid'));venue=str(value('venue'))
            name=next((v['name'] for v in CATALOG['ccf_conferences'] if v['name'].lower() in venue_id.lower().split('.')[0]),venue)
            main=bool(re.fullmatch(r'(ICLR|NeurIPS|ICML)\.cc/\d{4}/Conference',venue_id,re.I)) and not re.search('submitted|withdrawn|rejected',venue,re.I)
            return {'title':value('title'),'venue':name,'issns':[],'type':'proceedings-article','paper_type':'full' if main else 'workshop' if 'workshop' in venue_id.lower() else 'unknown','identity_source':source,'canonical_url':url,'bound_to_url':item.get('id')==paper_id or item.get('forum')==paper_id,'venue_detail':venue}
        if not doi:
            page=self._get(url,deadline);meta=parse_metadata(page['text']);doi=meta['doi'];link_bound=True
        if doi:
            if not re.fullmatch(r'10\.\d{4,9}/\S{1,500}',doi):raise FetchUnavailable('The DOI could not be read.')
            source='https://api.crossref.org/works/'+quote(doi,safe='')
            data=json.loads(self._get(source,deadline)['text']).get('message',{})
            canonical=data.get('resource',{}).get('primary',{}).get('URL','')
            def clean_url(u):
                q=urlsplit(u);return ((q.hostname or '').removeprefix('www.'),unquote(q.path).rstrip('/'))
            if not link_bound and canonical:link_bound=clean_url(url)==clean_url(canonical)
            if not link_bound:
                page=self._get(url,deadline);link_bound=parse_metadata(page['text'])['doi'].lower()==doi.lower()
            title=html.unescape(re.sub(r'<[^>]+>','',(data.get('title') or [''])[0]))
            return {'title':' '.join(title.split()),'venue':(data.get('container-title') or [''])[0], 'issns':data.get('ISSN',[]),
                    'doi':doi,'type':data.get('type',''),'paper_type':'unknown','identity_source':source,'canonical_url':canonical,'bound_to_url':link_bound}
        meta.update(identity_source=page.get('url',url),canonical_url=page.get('url',url),bound_to_url=True)
        if re.search(r'workshop|findings|short.paper|demo.paper',meta['venue']+' '+p.path,re.I):meta['paper_type']='workshop'
        elif host in ('papers.nips.cc','papers.neurips.cc','proceedings.neurips.cc') and re.search(r'/(?:paper_files/)?paper/\d{4}/',p.path):
            meta.update(venue='NeurIPS',type='proceedings-article',paper_type='full')
        elif host=='proceedings.mlr.press' and re.search('International Conference on Machine Learning',meta['venue'],re.I):meta.update(type='proceedings-article',paper_type='full')
        elif host=='openaccess.thecvf.com' and re.search(r'/content/(CVPR|ICCV)\d{4}/html/',p.path):meta.update(venue=re.search(r'/content/(CVPR|ICCV)',p.path)[1],type='proceedings-article',paper_type='full')
        elif host=='aclanthology.org' and re.search(r'\d{4}\.acl-long\.\d+',p.path):meta.update(venue='ACL',type='proceedings-article',paper_type='full')
        return meta

    def evaluate(self,record,metadata,metric=None):
        field=record.get('field','');venue=record.get('venue','')
        if metric:
            newer=max((m for m in CATALOG['metric_records'] if metric_matches(m,metadata) and m['year']>metric.get('year',0)),key=lambda m:m['year'],default=None)
            if newer:metric=newer
        evidence=[];reasons=[];states=[];basis=[];top=None
        def add(state,code,message):states.append(state);reasons.append({'status':state,'code':code,'message':message})
        entry=find_venue(venue,CATALOG['math_journals'] if field=='mathematics' else CATALOG['ccf_conferences'] if field=='computer_science' else [])
        if field in ('chemistry','biological_science'):entry=top_journal(venue)
        arxiv_id=arxiv_identifier(record.get('source_url',''))
        is_arxiv=bool(arxiv_id) and norm(venue)=='arxiv'
        if field=='others' and not is_arxiv:add('blocked','field_closed','Sorry, this field is not open for journal or conference submissions yet. Verified arXiv preprints are accepted in all fields.')
        elif field not in ('chemistry','biological_science','computer_science','mathematics','others'):add('blocked','field_required','Choose a field for eligibility checking.')
        if unsafe_url(record.get('source_url','')):add('blocked','unsafe_url','Use a public HTTPS article landing page or DOI URL; local addresses and credentials are not accepted.')
        if not metadata.get('title') or not metadata.get('venue') or not metadata.get('bound_to_url'):
            add('pending','metadata_unavailable','The exact title and venue could not be verified for this URL. The maintainer must verify the official record.')
        else:
            if norm(record.get('title',''))==norm(metadata['title']):add('pass','title_match','The title matches the published metadata.')
            elif SequenceMatcher(None,norm(record.get('title','')),norm(metadata['title'])).ratio()>=.85:add('pending','title_close','The title is similar but not an exact match. Check punctuation, formulas and subtitle against the detected title.')
            else:add('blocked','title_mismatch','This URL identifies a different title. Correct the title or the article URL.')
            if venue_matches(venue,metadata,entry):add('pass','venue_match','The supplied venue matches the published metadata.')
            elif field=='computer_science' and entry and metadata.get('type')=='journal-article':add('pending','conference_container_unverified','The source names a journal rather than the selected conference. Its connection to the full/regular main-conference proceedings needs verification.')
            else:add('blocked','venue_mismatch','The detected journal or conference differs from the supplied venue.')
            if metadata.get('type') in ('posted-content','preprint') and not is_arxiv:add('blocked','not_published','Only verified arXiv preprints are included in the preprint route.')
            elif is_arxiv:
                actual=metadata.get('arxiv_id','')
                same=bool(actual) and re.sub(r'v\d+$','',actual).casefold()==re.sub(r'v\d+$','',arxiv_id).casefold()
                if re.search(r'v\d+$',arxiv_id):same=same and actual.casefold()==arxiv_id.casefold()
                add('pass' if same else 'pending','arxiv_identity','Official arXiv identity verified. Preprints have no venue or JIF restriction in this collection.' if same else 'The exact arXiv identifier and version still need verification.')
            elif field in ('chemistry','biological_science','mathematics') and metadata.get('type')!='journal-article':add('pending','article_type_unverified','The official record must identify a published journal article. Book chapters, datasets and other records need intake clarification.')
            if metadata.get('identity_source'):evidence.append({'label':'Published metadata','url':metadata['identity_source']})
        if is_arxiv:pass
        elif field in ('chemistry','biological_science'):
            top=top_journal(metadata.get('venue',''))
            if not top and entry and venue_matches(venue,metadata,entry):top=entry
            top_current=bool(top) and date.today().isoformat()<CATALOG['top_policy']['refresh_due']
            jif_valid=False;jif_pass=False
            if metric and metric_matches(metric,metadata) and isinstance(metric.get('year'),int) and 1975<=metric['year']<date.today().year and not unsafe_url(metric.get('source','')) and (urlsplit(metric['source']).hostname in METRIC_HOSTS):
                value=metric.get('value')
                if isinstance(value,(int,float)) and 0<=value<2000:
                    jif_valid=True;jif_pass=value>10
                    evidence.append({'label':f"{metric['year']} JIF source",'url':metric['source']})
            if jif_pass:
                basis.append('jif')
                add('pass','jif_threshold',f"Most recent verified JIF: {metric['value']:g} ({metric['year']}); greater than 10.")
            if top_current:
                basis.append('top_list')
                add('pass','top_scope',f"Included in the {top['year']} TOP journal list: major-category Zone 1 and Top. No JIF threshold is required for this route.")
                evidence.append({'label':f"{top['year']} TOP list — public snapshot",'url':top['source']})
                if top.get('publisher_confirmation'):evidence.append({'label':'Publisher confirmation of TOP status','url':top['publisher_confirmation']})
            if not basis:
                if top:add('pending','top_refresh','The TOP list needs its annual refresh. A qualifying JIF can still establish eligibility.')
                elif not metadata.get('venue'):add('pending','metadata_needed','The paper identity check must finish before journal eligibility can be checked. Please retry the source check.')
                elif jif_valid:add('blocked','journal_scope',f"Most recent verified JIF: {metric['value']:g} ({metric['year']}); not greater than 10. No matching entry in the current TOP journal list. Neither route qualifies.")
                else:add('blocked','journal_scope','No qualifying dated JIF or matching entry in the current TOP journal list was found in the available sources. Qualifying evidence is required to proceed.')
        elif field=='computer_science':
            if not entry:add('blocked','conference_scope','This venue is not in the CCF 2026 A-conference list. Computer science journals and B/C conferences are outside this initial track.')
            else:
                evidence.append({'label':'CCF seventh-edition scope','url':CATALOG['ccf_source']})
                if metadata.get('paper_type')=='full':add('pass','conference_full','Listed CCF A conference; the official record identifies a main-conference paper.')
                elif metadata.get('paper_type') in ('workshop','short','demo','findings'):add('blocked','conference_type','Workshops, short papers, demos and Findings are not included. Use a full or regular main-conference paper.')
                else:add('pending','paper_type_unverified','The venue is listed, but the full/regular main-conference paper type still needs confirmation.')
        elif field=='mathematics':
            add('pass' if entry else 'blocked','math_scope','Included in the expanded ELVIA mathematics list.' if entry else 'This journal is outside the current mathematics list. Please choose a listed journal or a verified arXiv preprint.')
            if entry:evidence.append({'label':entry.get('source_label','Journal identity record'),'url':entry['source']})
        if not is_arxiv and field in ('computer_science','mathematics') and date.today().isoformat()>=CATALOG['refresh_due']:add('pending','policy_refresh','The annual scope refresh is due. The venue list needs updating.')
        status='blocked' if 'blocked' in states else 'pending' if 'pending' in states else 'pass'
        return {'status':status,'checked_at':now(),'policy_version':CATALOG['version'],'fingerprint':fingerprint(record),'metadata':metadata,'metric':metric,'top_record':top,'eligibility_basis':basis,'reasons':reasons,'evidence':evidence,'field_is_classification':False}

    def check(self,record):
        if (record.get('field')=='others' and not arxiv_identifier(record.get('source_url',''))) or unsafe_url(record.get('source_url','')):return self.evaluate(record,{},None)
        if not self.online:return self.evaluate(record,{},None)
        if not self.slots.acquire(blocking=False):
            result=self.evaluate(record,{},None);result['network_note']='Two source checks are already running. This submission is held for verification.';return result
        try:
            deadline=time.monotonic()+11
            metadata=self.metadata(record['source_url'],deadline)
            metric=max((m for m in CATALOG['metric_records'] if metric_matches(m,metadata)),key=lambda x:x['year'],default=None)
            # Only known metric pages are parsed; numbers in article bodies are never JIF evidence.
            if metric and urlsplit(metric['source']).hostname in TRUSTED_HOSTS and time.monotonic()<deadline:
                try:
                    text=self._get(metric['source'],deadline)['text']
                    for year in range(date.today().year-1,metric['year']-1,-1):
                        current=parse_metric_table(text,year,metric['journal']) if 'journal-metrics' in metric['source'] else parse_jif(text,year)
                        if current is not None:
                            metric={**metric,'value':current,'year':year,'verified_at':now(),'method':'Live official publisher metric page'};break
                except FetchUnavailable:pass
            return self.evaluate(record,metadata,metric)
        except UnsafeDestination as exc:
            result=self.evaluate(record,{},None);result['status']='blocked';result['reasons'].insert(0,{'status':'blocked','code':'unsafe_destination','message':str(exc)});return result
        except (FetchUnavailable,ValueError,KeyError,TypeError,ET.ParseError) as exc:
            result=self.evaluate(record,{},None);result['network_note']=str(exc) if isinstance(exc,FetchUnavailable) else 'The metadata response could not be interpreted; manual verification is needed.';return result
        finally:self.slots.release()
