"""Optional Google OIDC, authorization code + PKCE; identities never grant roles.

Client secret lives only in private local-data/google-oauth.json. ID tokens use
Google's maintained verifier, never unverified JWT decoding. Tokens are not saved.
"""
import base64
import hashlib
import hmac
import json
import re
import secrets
import time
from http.cookies import SimpleCookie
from urllib.parse import urlencode,parse_qs,urlsplit
from origin_policy import OriginPolicy
from owner_identity import is_retired

POLICY_VERSION='2026-10-22-public-v1'
AUTH_URL='https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_URL='https://oauth2.googleapis.com/token'

class GoogleLoginError(Exception):pass

class GoogleLogin:
    def __init__(self,data_dir,port,private_origin=None):
        self.origins=OriginPolicy(port,private_origin)
        self.config=None;self.reason='Google sign-in has not been configured for this local workspace.'
        path=data_dir/'google-oauth.json'
        if path.exists():
            try:
                config=self.validate_config(json.loads(path.read_text('utf-8')),port,private_origin=private_origin)
                from google.oauth2 import id_token  # noqa: F401
                self.config=config
                self.reason='Google sign-in settings are configured. Live sign-in must be verified separately in a regular browser.'
            except (ValueError,OSError,ImportError,GoogleLoginError):self.reason='Google sign-in configuration needs attention. Email sign-in is still available.'

    @staticmethod
    def validate_config(raw,port,private_origin=None):
        origins=OriginPolicy(port,private_origin)
        message='Use a valid Google web client configuration with the exact ELVIA callback URI.'
        if not isinstance(raw,dict):raise GoogleLoginError(message)
        raw=raw.get('web',raw)
        if not isinstance(raw,dict):raise GoogleLoginError(message)
        client_id=raw.get('client_id');secret=raw.get('client_secret')
        expected=f'http://127.0.0.1:{port}/api/auth/google/callback'
        redirects=raw.get('redirect_uris',[raw.get('redirect_uri')])
        if not isinstance(client_id,str) or not re.fullmatch(r'[A-Za-z0-9._-]+\.apps\.googleusercontent\.com',client_id):raise GoogleLoginError(message)
        if not isinstance(secret,str) or not secret or len(secret)>1000 or any(c in secret for c in '\r\n\x00'):raise GoogleLoginError(message)
        if not isinstance(redirects,list) or any(not isinstance(uri,str) for uri in redirects) or expected not in redirects:raise GoogleLoginError(message)
        config={'client_id':client_id,'client_secret':secret,'redirect_uri':expected}
        if origins.private_origin and origins.private_origin+'/api/auth/google/callback' in redirects:
            config['redirect_uris']=[expected,origins.private_origin+'/api/auth/google/callback']
        return config

    def callback_uri(self,origin=None):
        try:origin=self.origins.canonical(origin)
        except ValueError:raise GoogleLoginError('Use the configured ELVIA origin for Google sign-in.') from None
        if not self.config:raise GoogleLoginError(self.reason)
        expected=origin+'/api/auth/google/callback'
        configured=self.config.get('redirect_uris',[self.config['redirect_uri']])
        if expected not in configured:raise GoogleLoginError('Google sign-in is not configured for this ELVIA address. Use email sign-in.')
        return expected

    def public(self,origin=None):
        try:self.callback_uri(origin)
        except GoogleLoginError as exc:return {'enabled':False,'message':str(exc)}
        return {'enabled':True,'message':self.reason}

    def initialize(self,db):
        db.executescript('''
        CREATE TABLE IF NOT EXISTS google_identities(subject TEXT PRIMARY KEY,user_id TEXT UNIQUE NOT NULL REFERENCES users(id),email TEXT NOT NULL,created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS oauth_states(state_hash TEXT PRIMARY KEY,binding_hash TEXT NOT NULL,verifier TEXT NOT NULL,nonce TEXT NOT NULL,expires REAL NOT NULL,actor TEXT,session_token TEXT,mode TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS policy_acceptances(user_id TEXT NOT NULL REFERENCES users(id),version TEXT NOT NULL,accepted TEXT NOT NULL,method TEXT NOT NULL,PRIMARY KEY(user_id,version));
        ''')

    def start(self,db,actor=None,session=None,mode='login',origin=None):
        redirect_uri=self.callback_uri(origin)
        origin=self.origins.canonical(origin)
        raw,binding,verifier,nonce=[secrets.token_urlsafe(32) for _ in range(4)]
        db.execute('DELETE FROM oauth_states WHERE expires<?',(time.time(),))
        db.execute('INSERT INTO oauth_states VALUES(?,?,?,?,?,?,?,?)',(hashlib.sha256((origin+'\0'+raw).encode()).hexdigest(),hashlib.sha256((origin+'\0'+binding).encode()).hexdigest(),verifier,nonce,time.time()+600,actor['id'] if actor else None,session['token'] if session else None,mode))
        challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
        query={'client_id':self.config['client_id'],'redirect_uri':redirect_uri,'response_type':'code','scope':'openid email profile','state':raw,'nonce':nonce,'code_challenge':challenge,'code_challenge_method':'S256','prompt':'select_account'}
        cookie='elvia_oauth='+binding+'; Path=/api/auth/google; HttpOnly; SameSite=Lax; Max-Age=600'
        return AUTH_URL+'?'+urlencode(query),cookie

    def consume_state(self,db,query,cookie_header,origin=None):
        self.callback_uri(origin)
        origin=self.origins.canonical(origin)
        values=query.get('state',[])
        if len(values)!=1 or not isinstance(values[0],str) or not re.fullmatch(r'[A-Za-z0-9_-]{43}',values[0]):raise GoogleLoginError('This Google sign-in expired or belongs to another browser. Start again.')
        raw=values[0];digest=hashlib.sha256((origin+'\0'+raw).encode()).hexdigest()
        row=db.execute('SELECT * FROM oauth_states WHERE state_hash=?',(digest,)).fetchone()
        cookies=SimpleCookie()
        try:cookies.load(cookie_header)
        except Exception:raise GoogleLoginError('The Google sign-in could not be matched to this browser. Start again.') from None
        binding=cookies.get('elvia_oauth')
        if not row or row['expires']<time.time() or not binding or not hmac.compare_digest(row['binding_hash'],hashlib.sha256((origin+'\0'+binding.value).encode()).hexdigest()):raise GoogleLoginError('This Google sign-in expired or belongs to another browser. Start again.')
        db.execute('DELETE FROM oauth_states WHERE state_hash=?',(digest,))
        if row['mode']=='link' and not db.execute('SELECT 1 FROM sessions WHERE token=? AND user_id=? AND expires>?',(row['session_token'],row['actor'],time.time())).fetchone():raise GoogleLoginError('Sign in again before linking your Google account.')
        return dict(row)|{'origin':origin}

    def exchange(self,code,state):
        redirect_uri=self.callback_uri(state.get('origin'))
        import requests
        from google.auth.transport.requests import Request
        from google.oauth2 import id_token
        try:
            transport=requests.Session();transport.trust_env=False
            response=transport.post(TOKEN_URL,data={'client_id':self.config['client_id'],'client_secret':self.config['client_secret'],'redirect_uri':redirect_uri,'grant_type':'authorization_code','code':code,'code_verifier':state['verifier']},timeout=10,allow_redirects=False)
            if response.status_code!=200:raise GoogleLoginError('Google could not complete this sign-in. Start again.')
            token=response.json().get('id_token','')
            class BoundedRequest(Request):
                def __call__(self,*args,**kwargs):
                    kwargs['timeout']=10
                    return super().__call__(*args,**kwargs)
            claims=id_token.verify_oauth2_token(token,BoundedRequest(session=transport),self.config['client_id'],clock_skew_in_seconds=30)
            if not hmac.compare_digest(str(claims.get('nonce','')),state['nonce']):raise GoogleLoginError('The Google sign-in response did not match this request.')
            if claims.get('azp') and claims['azp']!=self.config['client_id']:raise GoogleLoginError('The Google sign-in was issued for another application.')
            if claims.get('email_verified') is not True or not claims.get('sub') or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',claims.get('email','')):raise GoogleLoginError('A verified Google email is required.')
            return {'subject':claims['sub'],'email':claims['email'].casefold(),'name':str(claims.get('name') or claims['email'])[:150]}
        except GoogleLoginError:raise
        except Exception:raise GoogleLoginError('Google sign-in could not be verified. Retry or use email sign-in.') from None
        finally:
            if 'transport' in locals():transport.close()

    def finish(self,db,identity,state,uid,stamp):
        linked=db.execute('SELECT * FROM google_identities WHERE subject=?',(identity['subject'],)).fetchone()
        if state['mode']=='link':
            if linked and linked['user_id']!=state['actor']:raise GoogleLoginError('This Google account is already linked to another account.')
            other=db.execute('SELECT subject FROM google_identities WHERE user_id=?',(state['actor'],)).fetchone()
            if other and other['subject']!=identity['subject']:raise GoogleLoginError('A different Google account is already linked. Contact the maintainer before changing it.')
            # Recheck the originating session after the network request, before role-bearing linkage.
            if not db.execute('SELECT 1 FROM sessions WHERE token=? AND user_id=? AND expires>?',(state['session_token'],state['actor'],time.time())).fetchone():raise GoogleLoginError('Your local sign-in changed. Sign in again before linking Google.')
            user_id=state['actor']
        elif linked:user_id=linked['user_id']
        else:raise GoogleLoginError('Google sign-in is reserved for linked admin and maintainer accounts. Contributors must verify an institutional email.')
        user=db.execute('SELECT * FROM users WHERE id=?',(user_id,)).fetchone()
        if not user or is_retired(db,user_id) or user['role'] not in ('admin','maintainer'):raise GoogleLoginError('Google sign-in is available only to admins and maintainers.')
        if user['force_change']:raise GoogleLoginError('Choose a new local password before continuing with Google.')
        control=db.execute('SELECT suspended FROM account_controls WHERE user_id=?',(user_id,)).fetchone()
        if control and control['suspended']:raise GoogleLoginError('This account is suspended. Contact a site manager.')
        db.execute('INSERT INTO google_identities VALUES(?,?,?,?) ON CONFLICT(subject) DO UPDATE SET email=excluded.email',(identity['subject'],user_id,identity['email'],stamp()))
        db.execute('INSERT OR IGNORE INTO policy_acceptances VALUES(?,?,?,?)',(user_id,POLICY_VERSION,stamp(),'google'))
        return db.execute('SELECT * FROM users WHERE id=?',(user_id,)).fetchone()
