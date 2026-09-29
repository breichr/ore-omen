from datetime import timedelta

from tests.conftest import register


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "db": "ok"}


def test_register_sets_secure_httponly_cookie(client):
    r = register(client)
    assert r.status_code == 201
    cookie = r.headers["set-cookie"]
    assert "oo_session=" in cookie
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "samesite=lax" in cookie.lower()
    assert "Max-Age=2592000" in cookie  # 30 days


def test_me_requires_login(client):
    r = client.get("/me")
    assert r.status_code == 401
    assert r.json()["detail"]["code"] == "not_authenticated"


def test_me_after_register(client):
    register(client, email="Rosa@Example.com")
    r = client.get("/me")
    assert r.status_code == 200
    body = r.json()
    assert body["user"] == {"email": "rosa@example.com", "timezone": "Europe/Vienna"}
    assert body["character"] is None


def test_register_duplicate_email_case_insensitive(client):
    register(client)
    client.cookies.clear()
    r = register(client, email="ROSA@example.com")
    assert r.status_code == 409
    assert r.json()["detail"]["code"] == "email_taken"


def test_register_validation(client):
    assert register(client, email="kein-email").status_code == 422
    assert register(client, password="kurz").status_code == 422


def test_login_logout(client):
    register(client)
    client.cookies.clear()
    assert client.get("/me").status_code == 401

    r = client.post("/auth/login", json={"email": "rosa@example.com", "password": "falsch123"})
    assert r.status_code == 401
    assert r.json()["detail"]["code"] == "invalid_credentials"

    r = client.post("/auth/login", json={"email": "rosa@example.com", "password": "geheim123"})
    assert r.status_code == 200
    assert client.get("/me").status_code == 200

    old_token = client.cookies.get("oo_session")
    assert client.post("/auth/logout").status_code == 200
    assert client.get("/me").status_code == 401
    # The token is invalid server-side, not just deleted from the browser
    assert old_token
    client.cookies.clear()
    assert client.get("/me", headers={"Cookie": f"oo_session={old_token}"}).status_code == 401


def test_login_unknown_email(client):
    r = client.post("/auth/login", json={"email": "niemand@example.com", "password": "geheim123"})
    assert r.status_code == 401


def test_session_slides_and_expires(client, clock):
    register(client)
    # 29 days later: still valid, and the expiry slides forward
    clock.now += timedelta(days=29)
    assert client.get("/me").status_code == 200
    clock.now += timedelta(days=29)
    assert client.get("/me").status_code == 200
    # 30 days without activity: expired
    clock.now += timedelta(days=30, seconds=1)
    assert client.get("/me").status_code == 401


def test_login_rate_limit(client):
    for _ in range(10):
        client.post("/auth/login", json={"email": "x@example.com", "password": "falsch"})
    r = client.post("/auth/login", json={"email": "x@example.com", "password": "falsch"})
    assert r.status_code == 429
    assert r.json()["detail"]["code"] == "rate_limited"
