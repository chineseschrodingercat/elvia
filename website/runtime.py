"""Bounded public WSGI entry for the dedicated loopback-only Cloudflare Tunnel.

The connector and other programs on this owner-controlled PC are trusted. The
loopback listener and canonical Host isolate ingress from LAN/public connections.
Only Cloudflare's client metadata supplies rate-limit identities; application
roles never come from proxy headers. Do not expose this listener on a LAN or
route another host or a Worker relay to it.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import io
import json
import secrets
import sys
import threading
import time
from collections import deque
from email.message import Message
from http import HTTPStatus
from pathlib import Path
from urllib.parse import unquote

from website.storage import install_limits
from website.supervisor import load_config

SERVER = Path(__file__).resolve().parent / "preview/server"
sys.path.insert(0, str(SERVER))

from local_service import (  # noqa: E402
    SITE,
    AbuseBudget,
    AdmissionEngine,
    AtlasStatic,
    EmailAccess,
    GoogleLogin,
    Handler,
    LocalServer,
    LoginGuard,
    OriginPolicy,
    connect,
    generated_password,
    initialize,
    password_hash,
)
from trusted_login_proxy import canonical_client_ip, protected_action, sign_context  # noqa: E402

ORIGIN = "https://elvia-atlas.org"
MAX_BODY = 16 * 1024 * 1024
CHALLENGES = {
    "/api/auth/login": "login",
    "/api/auth/email-code": "email",
    "/api/auth/password-reset/request": "reset",
}
ALLOWED_HEADERS = {
    "accept",
    "accept-language",
    "user-agent",
    "content-type",
    "content-length",
    "x-csrf-token",
    "x-version",
    "x-filename",
    "cookie",
    "origin",
}
CSP = (
    "default-src 'self'; script-src 'self' https://challenges.cloudflare.com; "
    "style-src 'self'; font-src 'self'; img-src 'self' data:; "
    "connect-src 'self' https://challenges.cloudflare.com; "
    "frame-src https://challenges.cloudflare.com; base-uri 'none'; "
    "form-action 'self'; object-src 'none'; frame-ancestors 'none'"
)


class RuntimeState:
    """Application state without the prototype HTTP listener."""

    def __init__(self, data_dir, *, bootstrap_password=None):
        self.data_dir = Path(data_dir).resolve()
        self.db_path = initialize(self.data_dir, bootstrap_password, seed_demo=False)
        self.atlas = AtlasStatic(SITE / "atlas")
        self.attempts = {}
        self.rate_lock = threading.Lock()
        self.reset_mail_slots = threading.BoundedSemaphore(2)
        self.auth_slots = threading.BoundedSemaphore(4)
        self.dummy_hash = password_hash(generated_password())
        self.admission = AdmissionEngine()
        self.origins = OriginPolicy(8797, ORIGIN)
        self.google = GoogleLogin(self.data_dir, 8797, private_origin=ORIGIN)
        self.mailer = EmailAccess(self.data_dir)
        self.abuse = AbuseBudget(self.mailer.key)
        self.login_guard = LoginGuard(self.mailer.key)
        self.login_proxy_key = secrets.token_bytes(32)
        with connect(self.db_path) as db:
            install_limits(db)
            self.google.initialize(db)

    deliver_password_reset = LocalServer.deliver_password_reset


class PublicBudget:
    def __init__(self, key):
        self.key = key
        self.lock = threading.Lock()
        self.sources = {}

    def allow(self, source, method, path):
        identity = hmac.new(self.key, source.encode(), hashlib.sha256).digest()
        category = (
            "auth"
            if path.startswith("/api/auth/")
            else "read"
            if method in {"GET", "HEAD"}
            else "write"
        )
        limits = {"auth": 30, "read": 600, "write": 60}
        now = time.monotonic()
        with self.lock:
            for key, queue in list(self.sources.items()):
                while queue and queue[0] <= now - 60:
                    queue.popleft()
                if not queue:
                    self.sources.pop(key)
            key = (identity, category)
            if key not in self.sources and len(self.sources) >= 4096:
                return False
            queue = self.sources.setdefault(key, deque())
            if len(queue) >= limits[category]:
                return False
            queue.append(now)
            return True


class WSGIHandler(Handler):
    def __init__(self, state, method, target, headers, body, source):
        self.server = state
        self.command = method
        self.path = target
        self.headers = headers
        self.rfile = io.BytesIO(body)
        self.wfile = io.BytesIO()
        self.client_address = (source, 0)
        self.response_headers = []
        self.response_status = 500

    def send_response(self, code, message=None):
        self.response_status = code

    def send_header(self, key, value):
        if key.casefold() == "content-security-policy":
            value = CSP
        self.response_headers.append((key, value))

    def end_headers(self):
        pass


class PublicApplication:
    def __init__(self, state, sitekey, verify_challenge):
        if not sitekey:
            raise ValueError(
                "Configure Turnstile before enabling public authentication."
            )
        self.state = state
        self.origin_host = "elvia-atlas.org"
        self.sitekey = sitekey
        self.verify_challenge = verify_challenge
        self.budget = PublicBudget(state.mailer.key)

    @staticmethod
    def reply(start, status, value):
        blob = json.dumps(value).encode()
        start(
            f"{status} {HTTPStatus(status).phrase}",
            [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(blob))),
                ("Cache-Control", "no-store"),
                ("X-Content-Type-Options", "nosniff"),
                ("Content-Security-Policy", CSP),
            ],
        )
        return [blob]

    def __call__(self, env, start):
        try:
            if env.get("REMOTE_ADDR") not in {
                "127.0.0.1",
                "::1",
            } or not hmac.compare_digest(env.get("HTTP_HOST", ""), self.origin_host):
                raise ValueError
            if json.loads(env.get("HTTP_CF_VISITOR", "{}")) != {"scheme": "https"}:
                raise ValueError
            source = canonical_client_ip(env.get("HTTP_CF_CONNECTING_IP", ""))
            if any(name.startswith("HTTP_X_ELVIA_") for name in env):
                raise ValueError
        except (ValueError, TypeError):
            return self.reply(
                start, 403, {"error": "Use the secure ELVIA website address."}
            )
        method = env.get("REQUEST_METHOD", "")
        path = env.get("PATH_INFO", "")
        query = env.get("QUERY_STRING", "")
        if method not in {"GET", "HEAD", "POST", "PUT"}:
            return self.reply(start, 405, {"error": "Method not allowed."})
        if (
            not path.startswith("/")
            or path.startswith("//")
            or "%" in path
            or "\\" in path
            or any(ord(c) < 32 for c in path + query)
            or len(path + query) > 8192
            or ".." in unquote(path).split("/")
            or (query and path.startswith("/api/auth/") and method != "GET")
        ):
            return self.reply(start, 400, {"error": "Invalid request address."})
        if method not in {"GET", "HEAD"} and env.get("HTTP_ORIGIN") != ORIGIN:
            return self.reply(
                start,
                403,
                {"error": "Open the ELVIA page directly before making changes."},
            )
        try:
            length = int(env.get("CONTENT_LENGTH", "0") or "0")
        except (ValueError, TypeError):
            return self.reply(start, 400, {"error": "Invalid request length."})
        if not 0 <= length <= MAX_BODY:
            return self.reply(start, 413, {"error": "The upload is too large."})
        if not self.budget.allow(source, method, path):
            return self.reply(
                start,
                429,
                {"error": "Too many requests. Wait one minute and try again."},
            )
        body = env["wsgi.input"].read(length)
        if len(body) != length:
            return self.reply(start, 400, {"error": "The upload was interrupted."})
        if path == "/api/public-config" and method == "GET":
            return self.reply(start, 200, {"turnstile_sitekey": self.sitekey})
        if method == "POST" and path in CHALLENGES:
            try:
                data = json.loads(body)
                token = data.get("turnstile_token", "")
                accepted = (
                    isinstance(token, str)
                    and 0 < len(token) <= 2048
                    and self.verify_challenge(token, source, CHALLENGES[path])
                )
            except (ValueError, TypeError, AttributeError):
                accepted = False
            if not accepted:
                return self.reply(
                    start,
                    403,
                    {"error": "Complete the security check, then try again."},
                )
        headers = Message()
        headers["Host"] = "elvia-atlas.org"
        for key, value in env.items():
            name = (
                key[5:].replace("_", "-").lower()
                if key.startswith("HTTP_")
                else key.replace("_", "-").lower()
            )
            if name in ALLOWED_HEADERS and name not in {
                "content-type",
                "content-length",
            }:
                headers[name] = value
        headers["Content-Type"] = env.get("CONTENT_TYPE", "")
        headers["Content-Length"] = str(length)
        target = path + ("?" + query if query else "")
        if protected_action(method, target):
            for key, value in sign_context(
                self.state.login_proxy_key, method, target, source, body
            ).items():
                headers[key] = value
        request = WSGIHandler(self.state, method, target, headers, body, source)
        request.handle_request()
        start(
            f"{request.response_status} {HTTPStatus(request.response_status).phrase}",
            request.response_headers,
        )
        return [request.wfile.getvalue()]


class TurnstileVerifier:
    def __init__(self, secret):
        self.secret = secret

    def __call__(self, token, source, action):
        import requests

        try:
            with requests.Session() as session:
                session.trust_env = False
                with session.post(
                    "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                    data={"secret": self.secret, "response": token, "remoteip": source},
                    timeout=(5, 5),
                    allow_redirects=False,
                    stream=True,
                ) as response:
                    if response.status_code != 200:
                        return False
                    raw = response.raw.read(16385, decode_content=True)
                    if len(raw) > 16384:
                        return False
                    result = json.loads(raw)
                    return (
                        isinstance(result, dict)
                        and result.get("success") is True
                        and result.get("hostname") == "elvia-atlas.org"
                        and result.get("action") == action
                    )
        except (requests.RequestException, ValueError, OSError):
            return False


def main():
    from waitress import serve

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    data = Path(config["data_dir"])
    if (
        not (data / "elvia.sqlite3").is_file()
        or not (data / "email-verification.key").is_file()
    ):
        raise SystemExit(
            "An existing, verified operational data directory is required."
        )
    state = RuntimeState(data)
    if not state.mailer.enabled or not state.atlas.files:
        raise SystemExit(
            "Configure mail and build the validated Atlas before public startup."
        )
    app = PublicApplication(
        state,
        config["turnstile_sitekey"],
        TurnstileVerifier(config["turnstile_secret"]),
    )
    print(
        "ELVIA public application ready on the dedicated loopback Tunnel port.",
        flush=True,
    )
    serve(
        app,
        host="127.0.0.1",
        port=8799,
        threads=4,
        connection_limit=48,
        channel_timeout=30,
        cleanup_interval=5,
        max_request_header_size=32768,
        max_request_body_size=MAX_BODY,
        inbuf_overflow=1048576,
        outbuf_overflow=1048576,
        clear_untrusted_proxy_headers=True,
        expose_tracebacks=False,
        ident="ELVIA",
    )


if __name__ == "__main__":
    main()
