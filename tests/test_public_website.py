"""Only the dedicated canonical loopback ingress reaches the application."""

import io
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from website.runtime import PublicApplication, RuntimeState  # noqa: E402


@pytest.fixture
def app(tmp_path):
    state = RuntimeState(tmp_path, bootstrap_password="Synthetic!Password42")
    return PublicApplication(
        state,
        "synthetic-sitekey",
        lambda *_: True,
    )


def call(app, path="/api/health", method="GET", data=None, **changes):
    body = json.dumps(data).encode() if data is not None else b""
    env = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": "",
        "REMOTE_ADDR": "127.0.0.1",
        "HTTP_HOST": "elvia-atlas.org",
        "HTTP_CF_CONNECTING_IP": "192.0.2.10",
        "HTTP_CF_VISITOR": '{"scheme":"https"}',
        "HTTP_ORIGIN": "https://elvia-atlas.org",
        "CONTENT_TYPE": "application/json",
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.input": io.BytesIO(body),
    }
    env.update(changes)
    result = {}

    def start(status, headers):
        result.update(status=int(status.split()[0]), headers=dict(headers))

    payload = b"".join(app(env, start))
    result["body"] = (
        json.loads(payload)
        if payload and "json" in result["headers"].get("Content-Type", "")
        else payload
    )
    return result


@pytest.mark.parametrize(
    "changes",
    [
        {"HTTP_HOST": "unrelated.example"},
        {"REMOTE_ADDR": "192.0.2.100"},
        {"HTTP_CF_VISITOR": '{"scheme":"http"}'},
        {"HTTP_CF_CONNECTING_IP": "unknown"},
        {"HTTP_X_ELVIA_LOGIN_CONTEXT": "forged"},
    ],
)
def test_forged_ingress_fails_before_application(app, changes):
    assert call(app, **changes)["status"] == 403


def test_public_health_and_permission_boundary(app):
    assert call(app)["status"] == 200
    assert call(app, "/api/admin")["status"] == 401
    assert (
        call(app, "/api/public-config")["body"]["turnstile_sitekey"]
        == "synthetic-sitekey"
    )


def test_canonical_origin_and_secure_session_cookie(app):
    data = {
        "login": "minhao",
        "password": "Synthetic!Password42",
        "turnstile_token": "accepted",
    }
    assert (
        call(app, "/api/auth/login", "POST", data, HTTP_ORIGIN="https://evil.example")[
            "status"
        ]
        == 403
    )
    response = call(app, "/api/auth/login", "POST", data)
    assert response["status"] == 200
    cookie = response["headers"]["Set-Cookie"]
    assert "Secure" in cookie and "HttpOnly" in cookie and "Domain=" not in cookie


def test_challenge_fails_before_credentials_or_mail(app):
    app.verify_challenge = lambda *_: False
    result = call(
        app,
        "/api/auth/email-code",
        "POST",
        {"email": "person@example.edu", "turnstile_token": "bad"},
    )
    assert result["status"] == 403


def test_missing_challenge_cannot_use_verifier_bypass(app):
    assert (
        call(
            app,
            "/api/auth/login",
            "POST",
            {"login": "minhao", "password": "Synthetic!Password42"},
        )["status"]
        == 403
    )


def test_invalid_body_and_encoded_auth_route_are_rejected(app):
    assert call(app, "/api/auth/%6cogin", "POST", {})["status"] == 400
    assert call(app, CONTENT_LENGTH="17000000")["status"] == 413


def test_production_initialization_has_no_synthetic_tasks(app):
    from local_service import connect

    with connect(app.state.db_path) as db:
        assert (
            db.execute("SELECT COUNT(*) FROM tasks WHERE synthetic=1").fetchone()[0]
            == 0
        )
