"""Explicit, single-owner authentication aliases; never infer shared identity."""
import re

OWNER_LOGIN='minhao'
OWNER_EMAIL='minhliu@ttu.edu'
OWNER_GOOGLE_EMAIL='liuminhao44b@gmail.com'
RETIRED_PASSWORD='!retired-owner-identity-v1!'
PROVENANCE='owner-directed-exact-pair-v1'


class IdentityError(ValueError):pass


def initialize_owner_identity(db):
    db.execute('CREATE TABLE IF NOT EXISTS auth_aliases(alias TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id),verified_at TEXT NOT NULL,created TEXT NOT NULL,provenance TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS account_merges(retired_user_id TEXT PRIMARY KEY REFERENCES users(id),canonical_user_id TEXT NOT NULL REFERENCES users(id),exact_email TEXT UNIQUE NOT NULL,created TEXT NOT NULL,provenance TEXT NOT NULL,CHECK(retired_user_id<>canonical_user_id))')


def _table(db,name):
    return bool(db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(name,)).fetchone())


def is_retired(db,user_id):
    return bool(_table(db,'account_merges') and db.execute('SELECT 1 FROM account_merges WHERE retired_user_id=?',(user_id,)).fetchone())


def alias_claimed(db,login):
    return bool((_table(db,'auth_aliases') and db.execute('SELECT 1 FROM auth_aliases WHERE alias=?',(login,)).fetchone()) or
                (_table(db,'account_merges') and db.execute('SELECT 1 FROM account_merges WHERE exact_email=?',(login,)).fetchone()))


def _suspended(db,user_id):
    row=db.execute('SELECT suspended FROM account_controls WHERE user_id=?',(user_id,)).fetchone()
    return bool(row and row[0])


def resolve_alias(db,login):
    if not alias_claimed(db,login):return None
    if login!=OWNER_EMAIL:return None
    alias=db.execute('SELECT * FROM auth_aliases WHERE alias=?',(login,)).fetchone()
    merge=db.execute('SELECT * FROM account_merges WHERE exact_email=?',(login,)).fetchone()
    if not alias or not merge or alias['user_id']!=merge['canonical_user_id']:return None
    target=db.execute('SELECT * FROM users WHERE id=?',(alias['user_id'],)).fetchone()
    source=db.execute('SELECT * FROM users WHERE id=?',(merge['retired_user_id'],)).fetchone()
    if (not target or not source or source['id']==target['id'] or is_retired(db,target['id'])
            or target['login']!=OWNER_LOGIN or target['role']!='maintainer' or _suspended(db,target['id'])
            or source['login']!=OWNER_EMAIL or source['role']!='reviewer'
            or source['password']!=RETIRED_PASSWORD or not _suspended(db,source['id'])
            or alias['provenance']!=PROVENANCE or merge['provenance']!=PROVENANCE):return None
    if any(db.execute('SELECT COUNT(*) FROM users WHERE lower(login)=?',(name,)).fetchone()[0]!=1 for name in (OWNER_LOGIN,OWNER_EMAIL)):return None
    verified=db.execute('SELECT user_id,email,verified FROM verified_emails WHERE lower(email)=?',(login,)).fetchall()
    if len(verified)!=1 or tuple(verified[0])!=(target['id'],login,alias['verified_at']):return None
    google=db.execute('SELECT user_id,email FROM google_identities WHERE user_id IN (?,?) OR lower(email) IN (?,?)',(target['id'],source['id'],login,OWNER_GOOGLE_EMAIL)).fetchall()
    if len(google)!=1 or tuple(google[0])!=(target['id'],OWNER_GOOGLE_EMAIL):return None
    # Neither endpoint may participate in another one-way identity link.
    if db.execute('SELECT COUNT(*) FROM account_merges WHERE retired_user_id IN (?,?) OR canonical_user_id IN (?,?)',(source['id'],target['id'],source['id'],target['id'])).fetchone()[0]!=1:return None
    if db.execute('SELECT COUNT(*) FROM auth_aliases WHERE user_id IN (?,?)',(source['id'],target['id'])).fetchone()[0]!=1:return None
    return target


def resolve_login(db,login):
    if alias_claimed(db,login):return resolve_alias(db,login)
    row=db.execute('SELECT * FROM users WHERE login=?',(login,)).fetchone()
    return row if row and not is_retired(db,row['id']) else None


def login_claimed(db,login):
    return alias_claimed(db,login) or bool(db.execute('SELECT 1 FROM users WHERE login=?',(login,)).fetchone())


def same_person(db,left,right):
    """Fail closed for independence checks, without granting historical edit ACLs."""
    if left==right:return True
    if not _table(db,'account_merges'):return False
    return bool(db.execute('SELECT 1 FROM account_merges WHERE (retired_user_id=? AND canonical_user_id=?) OR (retired_user_id=? AND canonical_user_id=?)',(left,right,right,left)).fetchone())


def recovery_user_ids(db,user_id):
    """Include retired-token history in the canonical account's existing daily cap."""
    ids=[user_id]
    if _table(db,'account_merges'):
        ids.extend(row[0] for row in db.execute('SELECT retired_user_id FROM account_merges WHERE canonical_user_id=?',(user_id,)))
    return ids


def alias_binding(db,email):
    if not alias_claimed(db,email):return []
    target=resolve_alias(db,email)
    if not target:raise IdentityError('The explicit owner identity needs maintenance.')
    merge=db.execute('SELECT * FROM account_merges WHERE exact_email=?',(email,)).fetchone()
    return [merge['retired_user_id'],merge['canonical_user_id'],merge['exact_email'],merge['created'],merge['provenance'],target['role']]


def _pair(db):
    target=db.execute('SELECT * FROM users WHERE login=?',(OWNER_LOGIN,)).fetchone()
    source=db.execute('SELECT * FROM users WHERE login=?',(OWNER_EMAIL,)).fetchone()
    if not target or not source or target['id']==source['id']:raise IdentityError('The exact approved pair was not found.')
    if alias_claimed(db,OWNER_EMAIL):
        linked=resolve_alias(db,OWNER_EMAIL)
        if not linked or linked['id']!=target['id']:raise IdentityError('An existing identity link is inconsistent.')
        return target,source,True
    if (target['role']!='maintainer' or source['role']!='reviewer' or target['force_change'] or source['force_change']
            or _suspended(db,target['id']) or _suspended(db,source['id'])
            or is_retired(db,target['id']) or is_retired(db,source['id'])):raise IdentityError('The approved account roles or authentication state changed.')
    if any(db.execute('SELECT COUNT(*) FROM users WHERE lower(login)=?',(name,)).fetchone()[0]!=1 for name in (OWNER_LOGIN,OWNER_EMAIL)):raise IdentityError('Case variants make the approved pair ambiguous.')
    if _table(db,'auth_aliases') and db.execute('SELECT 1 FROM auth_aliases WHERE lower(alias)=?',(OWNER_EMAIL,)).fetchone():raise IdentityError('A conflicting alias already exists.')
    if _table(db,'auth_aliases') and db.execute('SELECT 1 FROM auth_aliases WHERE user_id IN (?,?)',(target['id'],source['id'])).fetchone():raise IdentityError('The approved pair already has another alias.')
    if _table(db,'account_merges') and db.execute('SELECT 1 FROM account_merges WHERE canonical_user_id IN (?,?)',(target['id'],source['id'])).fetchone():raise IdentityError('Chained identity links are not supported.')
    google=db.execute('SELECT * FROM google_identities WHERE user_id IN (?,?) OR lower(email) IN (?,?)',(target['id'],source['id'],OWNER_EMAIL,OWNER_GOOGLE_EMAIL)).fetchall()
    if len(google)!=1 or google[0]['user_id']!=target['id'] or google[0]['email']!=OWNER_GOOGLE_EMAIL:raise IdentityError('The existing owner Google linkage is not the approved one.')
    verified=db.execute('SELECT * FROM verified_emails WHERE user_id IN (?,?) OR lower(email)=?',(target['id'],source['id'],OWNER_EMAIL)).fetchall()
    if len(verified)!=1 or verified[0]['user_id']!=source['id'] or verified[0]['email']!=OWNER_EMAIL:raise IdentityError('The exact verified institutional identity is not exclusive.')
    if not re.fullmatch(r'[0-9a-f]{32}:[0-9a-f]{128}',source['password']):raise IdentityError('The source password hash is not supported.')
    if not db.execute("SELECT 1 FROM events WHERE actor=? AND target=? AND action='password_reset_completed'",(source['id'],source['id'])).fetchone():raise IdentityError('A completed source password reset is required.')
    checks=(('applications','user_id'),('contributions','owner'),('amendments','owner'),('maintainer_revisions','author'),('daily_usage','user_id'),('admission_checks','actor'),('role_reservations','created_by'))
    if any(db.execute('SELECT 1 FROM '+table+' WHERE '+column+'=?',(source['id'],)).fetchone() for table,column in checks):raise IdentityError('The source has business history; this narrow helper cannot merge it.')
    if db.execute('SELECT 1 FROM role_reservations WHERE email=?',(OWNER_EMAIL,)).fetchone():raise IdentityError('A role reservation conflicts with the approved identity.')
    return target,source,False


def inspect_fixed_owner(db):
    _,_,done=_pair(db)
    return {'ready':True,'already_applied':done,'canonical_role':'maintainer','retired_role':'reviewer','business_rows_transferred':0,'password_values_returned':False}


def apply_fixed_owner(db,now):
    if not db.in_transaction:raise IdentityError('An explicit immediate transaction is required.')
    target,source,done=_pair(db)
    if done:return inspect_fixed_owner(db)|{'changed':False}
    initialize_owner_identity(db)
    verified=db.execute('SELECT verified FROM verified_emails WHERE user_id=?',(source['id'],)).fetchone()[0]
    db.execute('INSERT INTO auth_aliases VALUES(?,?,?,?,?)',(OWNER_EMAIL,target['id'],verified,now,PROVENANCE))
    db.execute('INSERT INTO account_merges VALUES(?,?,?,?,?)',(source['id'],target['id'],OWNER_EMAIL,now,PROVENANCE))
    db.execute('UPDATE verified_emails SET user_id=? WHERE user_id=? AND email=?',(target['id'],source['id'],OWNER_EMAIL))
    db.execute('UPDATE users SET password=?,force_change=0 WHERE id=?',(source['password'],target['id']))
    db.execute('UPDATE users SET password=? WHERE id=?',(RETIRED_PASSWORD,source['id']))
    db.execute('INSERT INTO account_controls VALUES(?,1,?,?,?) ON CONFLICT(user_id) DO UPDATE SET suspended=1,note=excluded.note,updated_by=excluded.updated_by,updated=excluded.updated',(source['id'],'Dormant historical identity; explicit owner alias points to the original maintainer.',target['id'],now))
    ids=(target['id'],source['id'])
    db.execute('DELETE FROM oauth_states WHERE actor IN (?,?) OR session_token IN (SELECT token FROM sessions WHERE user_id IN (?,?))',(*ids,*ids))
    db.execute('DELETE FROM sessions WHERE user_id IN (?,?)',ids)
    db.execute('UPDATE password_reset_tokens SET used=1 WHERE user_id IN (?,?)',ids)
    db.execute('DELETE FROM email_challenges WHERE email=?',(OWNER_EMAIL,))
    db.execute('INSERT INTO events(actor,target,action,note,created) VALUES(?,?,?,?,?)',(target['id'],source['id'],'owner_identity_consolidated',PROVENANCE+'; historical row retained; verified email moved; canonical Google and role preserved.',now))
    if not resolve_alias(db,OWNER_EMAIL):raise IdentityError('The completed identity link failed validation.')
    return inspect_fixed_owner(db)|{'changed':True}
