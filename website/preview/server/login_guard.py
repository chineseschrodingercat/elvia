"""Persistent source-IP login failure locks; identities and addresses never stored."""
import hashlib
import hmac
import ipaddress
import json
import math

FAILURES=10
WINDOW=3600
MAX_SOURCES=1024


def initialize_login_guard(db):
    db.execute('CREATE TABLE IF NOT EXISTS login_guard(source_key TEXT PRIMARY KEY,failures TEXT NOT NULL,locked_until REAL NOT NULL,updated REAL NOT NULL)')
    db.execute('CREATE INDEX IF NOT EXISTS login_guard_expiry ON login_guard(updated,locked_until)')


class LoginGuard:
    def __init__(self,key):self.key=key

    def source_key(self,source):
        address=ipaddress.ip_address(source)
        if getattr(address,'scope_id',None):raise ValueError('Use a canonical source address.')
        if getattr(address,'ipv4_mapped',None):address=address.ipv4_mapped
        return hmac.new(self.key,('elvia-login-lock-v1\0'+str(address)).encode(),hashlib.sha256).hexdigest()

    def state(self,db,source,now):
        if not db.in_transaction:raise ValueError('An immediate transaction is required.')
        db.execute('DELETE FROM login_guard WHERE updated<=? AND locked_until<=?',(now-WINDOW,now))
        key=self.source_key(source)
        row=db.execute('SELECT failures,locked_until FROM login_guard WHERE source_key=?',(key,)).fetchone()
        failures=[]
        if row:
            failures=json.loads(row[0])
            if not isinstance(failures,list) or len(failures)>FAILURES or any(type(value) not in (int,float) or not math.isfinite(value) for value in failures):
                raise ValueError('Login guard storage needs attention.')
            failures=[value for value in failures if value>now-WINDOW]
            if row[1]>now:return {'locked':True,'remaining':0,'retry_after':max(1,math.ceil(row[1]-now)),'failures':failures}
        elif db.execute('SELECT COUNT(*) FROM login_guard').fetchone()[0]>=MAX_SOURCES:
            expiry=db.execute('SELECT MIN(MAX(updated+?,locked_until)) FROM login_guard',(WINDOW,)).fetchone()[0]
            return {'locked':True,'remaining':0,'retry_after':max(1,math.ceil(expiry-now)),'failures':[],'capacity':True}
        return {'locked':False,'remaining':max(0,FAILURES-len(failures)),'retry_after':0,'failures':failures}

    def failure(self,db,source,now):
        state=self.state(db,source,now)
        if state['locked']:return state
        failures=state['failures']+[now]
        locked_until=now+WINDOW if len(failures)>=FAILURES else 0
        db.execute('INSERT INTO login_guard VALUES(?,?,?,?) ON CONFLICT(source_key) DO UPDATE SET failures=excluded.failures,locked_until=excluded.locked_until,updated=excluded.updated',
                   (self.source_key(source),json.dumps(failures,separators=(',',':')),locked_until,now))
        return {'locked':bool(locked_until),'remaining':max(0,FAILURES-len(failures)),'retry_after':WINDOW if locked_until else 0,'failures':failures}

    def clear(self,db,source):
        if not db.in_transaction:raise ValueError('An immediate transaction is required.')
        db.execute('DELETE FROM login_guard WHERE source_key=?',(self.source_key(source),))
