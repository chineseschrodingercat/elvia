"""Only the dedicated canonical loopback ingress reaches the application."""

import io
import json
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


from website.runtime import MAX_BODY, PublicApplication, RuntimeState  # noqa: E402


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


def test_public_reading_is_cacheable_but_workflow_and_query_routes_are_not(app):
    for path in (
        "/",
        "/project.html",
        "/robots.txt",
        "/assets/report-templates/first-report/main.pdf",
    ):
        result = call(app, path)
        assert result["status"] == 200
        assert result["headers"]["Cache-Control"].startswith("public, max-age=300")
        assert "stale-if-error=86400" in result["headers"]["Cache-Control"]
        assert "Set-Cookie" not in result["headers"]
    for path in (
        "/api/health",
        "/api/auth/me",
        "/contribute.html",
        "/password-reset-complete.html",
        "/missing.html",
    ):
        assert call(app, path)["headers"]["Cache-Control"] == "no-store"
    assert (
        call(app, "/", QUERY_STRING="view=compose")["headers"]["Cache-Control"]
        == "no-store"
    )
    assert (
        call(app, "/", QUERY_STRING="unknown=1")["headers"]["Cache-Control"]
        == "no-store"
    )


def test_public_reading_does_not_need_the_operational_database(app, monkeypatch):
    import local_service

    def unavailable(*_):
        raise OSError("Synthetic workflow database interruption")

    monkeypatch.setattr(local_service, "connect", unavailable)
    result = call(app, "/project.html")
    assert result["status"] == 200
    assert b"ELVIA" in result["body"]
    assert call(app, "/api/auth/me")["headers"]["Cache-Control"] == "no-store"


def test_crawler_groups_allow_public_content_and_exclude_operational_api(app):
    from urllib.robotparser import RobotFileParser

    rules = RobotFileParser()
    rules.parse(call(app, "/robots.txt")["body"].decode().splitlines())
    for crawler in (
        "OAI-SearchBot",
        "ChatGPT-User",
        "GPTBot",
        "Claude-SearchBot",
        "Claude-User",
        "ClaudeBot",
        "Googlebot",
        "Google-Extended",
        "bingbot",
        "PerplexityBot",
        "Perplexity-User",
        "UnlistedExampleBot",
    ):
        assert rules.can_fetch(
            crawler, "https://elvia-atlas.org/atlas/cases/example.html"
        )
        assert not rules.can_fetch(crawler, "https://elvia-atlas.org/api/contributions")


def test_cache_policy_never_caches_errors_aliases_or_session_setting_responses():
    from public_reading import cache_control

    for path in (
        "/api/health",
        "/contribute.html",
        "/%61tlas/index.html",
        "/atlas/?token=x",
    ):
        assert cache_control(path, "GET", 200) == "no-store"
    assert cache_control("/", "GET", 500) == "no-store"
    assert cache_control("/", "POST", 200) == "no-store"
    assert cache_control("/", "GET", 200, {"Set-Cookie": "example"}) == "no-store"


def test_public_report_starter_can_be_packaged_without_a_special_manifest(app):
    from local_service import inspect_zip

    template = call(app, "/assets/report-template.txt")
    assert template["status"] == 200
    assert b"ELVIA FOCUSED REPORT TEMPLATE" in template["body"]
    assert b"Counter" in template["body"] or b"counterevidence" in template["body"]
    example = call(app, "/assets/clarification-example.txt")
    assert example["status"] == 200
    assert b"SYNTHETIC TEACHING EXAMPLE" in example["body"]
    package = io.BytesIO()
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("report.txt", template["body"])
    manifest = inspect_zip(package.getvalue(), "report.zip")
    assert manifest == [{"name": "report.txt", "bytes": len(template["body"])}]


def test_public_configuration_and_ingress_errors_are_not_indexed(app):
    for result in (call(app, "/api/public-config"), call(app, HTTP_HOST="bad.example")):
        assert result["headers"].get("X-Robots-Tag") == "noindex, nofollow"


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
    assert call(app, CONTENT_LENGTH=str(MAX_BODY + 1))["status"] == 413


def test_fifty_mib_upload_reaches_application_authentication(app):
    # The public ingress must admit the full paper size. The endpoint still
    # rejects an unauthenticated upload before any operational data is saved.
    body = b"%PDF-1.4\n" + bytes(50 * 1024 * 1024 - 15) + b"\n%%EOF"
    result = call(
        app,
        "/api/contributions/synthetic/source",
        "POST",
        CONTENT_TYPE="application/octet-stream",
        CONTENT_LENGTH=str(len(body)),
        **{"wsgi.input": io.BytesIO(body)},
    )
    assert result["status"] == 401


def test_production_initialization_has_no_synthetic_tasks(app):
    from local_service import connect

    with connect(app.state.db_path) as db:
        assert (
            db.execute("SELECT COUNT(*) FROM tasks WHERE synthetic=1").fetchone()[0]
            == 0
        )
