"""Exact optional private origin; never infer browser identity from proxy headers."""
from http.cookies import SimpleCookie
from urllib.parse import urlsplit
from trusted_login_proxy import HEADER_NAMES

PRIVATE_ORIGIN = 'https://elvia-atlas.org'


def validate_private_origin(value):
    if value is not None and value != PRIVATE_ORIGIN:
        raise ValueError('The private origin must be the explicitly authorized ELVIA HTTPS origin.')
    return value


class OriginPolicy:
    def __init__(self, port, private_origin=None):
        self.private_origin = validate_private_origin(private_origin)
        self.loopback = f'http://127.0.0.1:{port}'
        self.origins = (self.loopback,) + ((self.private_origin,) if self.private_origin else ())
        self.hosts = {urlsplit(origin).netloc: origin for origin in self.origins}

    def canonical(self, origin=None):
        origin = self.loopback if origin is None else origin
        if origin not in self.origins:
            raise ValueError('Use the configured ELVIA origin.')
        return origin

    def request_origin(self, headers, method, *, allow_login_context=False):
        names = [name.casefold() for name in headers.keys()]
        if len(names) != len(set(names)):
            raise ValueError('Duplicate request headers are not accepted.')
        if any(name == 'forwarded' or name.startswith(('x-forwarded-', 'cf-'))
               or (name.startswith('x-elvia-') and not (allow_login_context and name in HEADER_NAMES)) for name in names):
            raise ValueError('Untrusted forwarding headers are not accepted.')
        origin = self.hosts.get(headers.get('Host'))
        if origin is None:
            raise ValueError('Use the configured ELVIA address.')
        if method not in ('GET', 'HEAD') and headers.get('Origin') != origin:
            raise ValueError('Open this ELVIA page directly before making changes.')
        return origin

    @staticmethod
    def cookie(value, origin):
        if not origin.startswith('https://'):
            return value
        cookie = SimpleCookie()
        cookie.load(value)
        if len(cookie) != 1 or next(iter(cookie)) not in ('elvia_session', 'elvia_oauth'):
            raise ValueError('Invalid application cookie.')
        morsel = next(iter(cookie.values()))
        if morsel['domain']:
            raise ValueError('Application cookies must be host-only.')
        morsel['secure'] = True
        morsel['httponly'] = True
        return morsel.OutputString()
