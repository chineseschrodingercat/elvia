"""Institutional email eligibility and actual SMTP delivery; no production outbox bypass."""
import json,os,re,secrets,smtplib,ssl,tempfile
from email.message import EmailMessage
from email.utils import formataddr,formatdate,make_msgid
from html import escape
from pathlib import Path

class MailError(Exception):pass

def normalize_email(value):
    if not isinstance(value,str):return ''
    value=value.strip().casefold()
    if len(value)>254 or not re.fullmatch(r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+',value):return ''
    return value

def eligible_email(email,domains):
    email=normalize_email(email)
    if not email:return False
    host=email.rsplit('@',1)[1]
    return bool(re.search(r'\.(?:edu(?:\.[a-z]{2})?|ac\.[a-z]{2})$',host)) or any(host==d or host.endswith('.'+d) for d in domains)


def single_mailbox(value):
    """SMTP envelopes and address headers accept one unambiguous mailbox only."""
    value=normalize_email(value)
    if not value or any(ord(c)<32 or ord(c)==127 or c in ',;:"()[]\\' for c in value):return ''
    return value

class EmailAccess:
    def __init__(self,data_dir):
        self.data_dir=Path(data_dir);self.path=self.data_dir/'email-settings.json';self.config={}
        if self.path.exists():
            try:self.config=self.validate_config(json.loads(self.path.read_text('utf-8')))
            except (ValueError,OSError,MailError):pass
        key=self.data_dir/'email-verification.key'
        if not key.exists():key.write_bytes(secrets.token_bytes(32))
        self.key=key.read_bytes()

    @property
    def enabled(self):
        try:self.validate_config(self.config);return True
        except MailError:return False

    @property
    def domains(self):return self.config.get('research_domains',[])

    def public(self):return {'enabled':self.enabled,'research_domains':self.domains,'academic_suffixes':['.edu','.edu.<country>','.ac.<country>'],'message':'Email settings are configured. Live delivery must be verified separately.' if self.enabled else 'Email registration is waiting for valid sending-service settings.'}

    def settings(self):return {k:v for k,v in self.config.items() if k!='password'}|{'enabled':self.enabled,'password_saved':bool(self.config.get('password'))}

    @staticmethod
    def validate_config(data,saved_password=''):
        if not isinstance(data,dict):raise MailError('Use an SMTP settings object.')
        if any(not isinstance(data.get(k,''),str) for k in ('host','username','sender','security')):raise MailError('Use text values for SMTP settings.')
        config={k:data.get(k,'').strip() for k in ('host','username','sender','security')}
        config['host']=config['host'].casefold()
        if not re.fullmatch(r'[A-Za-z0-9.-]+',config['host']) or '.' not in config['host']:raise MailError('Enter the SMTP hostname supplied by your email provider.')
        port=data.get('port',0)
        if isinstance(port,bool) or not isinstance(port,(str,int)):raise MailError('Enter the SMTP port.')
        try:config['port']=int(port)
        except (ValueError,TypeError):raise MailError('Enter the SMTP port.') from None
        if config['security'] not in ('ssl','starttls') or not 1<=config['port']<=65535:raise MailError('Choose SSL/TLS or STARTTLS and a valid port.')
        config['sender']=single_mailbox(config['sender'])
        if not config['sender'] or not config['username'] or len(config['username'])>254 or any(c in config['username'] for c in '\r\n\x00'):raise MailError('Enter the sending email and SMTP username.')
        name=data.get('sender_name','ELVIA Accounts')
        if not isinstance(name,str) or len(name)>120 or any(ord(c)<32 or ord(c)==127 for c in name):raise MailError('Use a short sender display name without control characters.')
        config['sender_name']=name.strip() or 'ELVIA Accounts'
        reply=data.get('reply_to','')
        if not isinstance(reply,str) or (reply and not single_mailbox(reply)):raise MailError('Use one reply email address without a display name.')
        config['reply_to']=single_mailbox(reply) if reply else ''
        config['password']=data.get('password') or saved_password
        if not isinstance(config['password'],str) or not config['password'] or len(config['password'])>1000 or any(c in config['password'] for c in '\r\n\x00'):raise MailError('Enter the SMTP password or app-specific password.')
        domains=data.get('research_domains',[])
        if not isinstance(domains,list) or len(domains)>300:raise MailError('Use a list of institutional domains.')
        config['research_domains']=[]
        consumer={'gmail.com','googlemail.com','outlook.com','hotmail.com','live.com','yahoo.com','icloud.com','qq.com','163.com','proton.me','protonmail.com','mail.com'}
        for domain in domains:
            if not isinstance(domain,str):raise MailError('Use institutional domain names as text.')
            domain=domain.strip().casefold()
            if domain in consumer or not re.fullmatch(r'(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}',domain):raise MailError('Use institutional domains, without @ or a URL. Personal email providers cannot be added.')
            if domain not in config['research_domains']:config['research_domains'].append(domain)
        return config

    def save(self,data):
        # The historical settings form omits these optional fields.
        if isinstance(data,dict):data={**{k:self.config[k] for k in ('sender_name','reply_to') if k in self.config},**data}
        config=self.validate_config(data,self.config.get('password',''))
        if self.path.is_symlink():raise MailError('The private email settings path needs attention.')
        temporary=None
        try:
            with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=self.data_dir,prefix='.email-settings-',suffix='.tmp',delete=False) as output:
                temporary=Path(output.name)
                output.write(json.dumps(config,indent=2)+'\n');output.flush();os.fsync(output.fileno())
            temporary.replace(self.path)
        except OSError:raise MailError('The private email settings could not be saved.') from None
        finally:
            if temporary is not None:temporary.unlink(missing_ok=True)
        self.config=config

    def _message(self,email,subject,text,html):
        recipient=single_mailbox(email)
        if not recipient:raise MailError('Use one valid recipient email address.')
        message=EmailMessage()
        message['From']=formataddr((self.config.get('sender_name','ELVIA Accounts'),self.config['sender']))
        message['To']=recipient;message['Subject']=subject
        message['Date']=formatdate(localtime=False,usegmt=True)
        message['Message-ID']=make_msgid(domain=self.config['sender'].rsplit('@',1)[1])
        if self.config.get('reply_to'):message['Reply-To']=self.config['reply_to']
        message.set_content(text)
        message.add_alternative('<!doctype html><html lang="en"><body>'+html+'</body></html>',subtype='html')
        return message,recipient

    def _send(self,message,recipient,error):
        try:
            if self.config['security']=='ssl':connection=smtplib.SMTP_SSL(self.config['host'],self.config['port'],timeout=10,context=ssl.create_default_context())
            else:
                connection=smtplib.SMTP(self.config['host'],self.config['port'],timeout=10);connection.ehlo();connection.starttls(context=ssl.create_default_context());connection.ehlo()
            with connection:
                connection.login(self.config['username'],self.config['password'])
                connection.send_message(message,from_addr=self.config['sender'],to_addrs=[recipient])
        except (OSError,smtplib.SMTPException):raise MailError(error) from None

    def send_code(self,email,code):
        if not self.enabled:raise MailError('Registration is waiting for the maintainer to configure the domain email service. No verification email was sent.')
        text=f'Your ELVIA verification code is {code}.\n\nIt expires in 10 minutes. Enter it only in the ELVIA registration page you opened. If you did not request this code, ignore this message.\n\nELVIA Accounts\n'
        html=f'<h1>Verify your ELVIA email</h1><p>Your verification code is <strong>{escape(str(code))}</strong>.</p><p>It expires in 10 minutes. Enter it only in the ELVIA registration page you opened.</p><p>If you did not request this code, ignore this message.</p><p>ELVIA Accounts</p>'
        message,recipient=self._message(email,'Your ELVIA email verification code',text,html)
        self._send(message,recipient,'The verification email could not be sent. Check the sending service settings and try again. No account was created.')

    def send_application_update(self,email,status,note,event_id):
        if not self.enabled:raise MailError('Application notifications are waiting for valid sending-service settings.')
        titles={'pending':'Application submitted','under_review':'Application under review','approved':'Reviewer access approved','needs_information':'More information requested','declined':'Application decision'}
        descriptions={
            'pending':'Your application for reviewer access has been received. Please allow 1–3 days for review. You can follow its progress in My work and submit your own analyses while you wait.',
            'under_review':'An admin or maintainer has opened your application and begun reviewing it. Reviewer access is awaiting a decision. We will email you when the status changes.',
            'approved':'Your application has been approved. You can now choose an available review in the contribution workspace.',
            'needs_information':'We need additional information before deciding on your reviewer access. Please read the note below and update your application in My work.',
            'declined':'Your reviewer application was not approved. Please read the decision note below. You can continue browsing and submitting your own analyses.'}
        url='https://elvia-atlas.org/contribute.html?view=my-work'
        title,description=titles[status],descriptions[status]
        text=title+'\n\n'+description+('\n\nDecision note:\n'+note if note else '')+'\n\nFollow your application: '+url+'\n\nELVIA\n'
        html='<h1>'+escape(title)+'</h1><p>'+escape(description)+'</p>'
        if note:html+='<h2>Decision note</h2><p>'+escape(note).replace('\n','<br>')+'</p>'
        html+='<p><a href="'+escape(url,quote=True)+'">Open My work</a></p><p>ELVIA</p>'
        message,recipient=self._message(email,'ELVIA: '+title,text,html)
        # Replays after ambiguous transport failures retain the same identifier.
        message.replace_header('Message-ID',f'<application-{event_id}@{self.config["sender"].rsplit("@",1)[1]}>')
        self._send(message,recipient,'The application notification could not be sent.')

    def send_password_reset(self,email,url):
        if not self.enabled:raise MailError('Password recovery is waiting for valid sending-service settings.')
        access_note='For the private HTTPS address, first complete the owner-only access sign-in if requested, then reopen this email link. The access gate does not create or change your ELVIA account.' if url.startswith('https://') else 'Open this link on the computer running your private ELVIA workspace.'
        text=f'A password reset was requested for your ELVIA account.\n\nOpen this one-time link in the ELVIA workspace where you requested it:\n{url}\n\n{access_note}\n\nThe link expires in 15 minutes. It changes only your local password and signs out existing sessions. If you did not request it, ignore this message.\n\nELVIA Accounts\n'
        html=f'<h1>Reset your ELVIA password</h1><p>A password reset was requested for your ELVIA account.</p><p><a href="{escape(url,quote=True)}">Reset your password</a></p><p>{escape(access_note)}</p><p>This one-time link expires in 15 minutes. It changes only your local password and signs out existing sessions.</p><p>If you did not request it, ignore this message.</p><p>ELVIA Accounts</p>'
        message,recipient=self._message(email,'Reset your ELVIA password',text,html)
        self._send(message,recipient,'The password-reset email could not be sent.')
