from datetime import timedelta

from app.services.credentials import normalize_recovery_key
from tests.conftest import register


def login(client, username="rosa", password="geheim123"):
    return client.post("/auth/login", json={"username": username, "password": password})


def recover(client, key, username="rosa", new_password="neuesPasswort"):
    return client.post(
        "/auth/recover",
        json={"username": username, "recovery_key": key, "new_password": new_password},
    )


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


def test_register_returns_recovery_key_once(client):
    key = register(client).json()["recovery_key"]
    assert normalize_recovery_key(key) is not None
    assert len(key) == 29  # 5 groups of 5 plus 4 hyphens
    assert "recovery_key" not in client.get("/me").text


def test_me_requires_login(client):
    r = client.get("/me")
    assert r.status_code == 401
    assert r.json()["detail"]["code"] == "not_authenticated"


def test_me_after_register(client):
    register(client, username="Rosa_1878")
    r = client.get("/me")
    assert r.status_code == 200
    body = r.json()
    assert body["user"] == {"username": "Rosa_1878", "timezone": "Europe/Vienna"}
    assert body["character"] is None


def test_register_duplicate_username_case_insensitive(client):
    register(client)
    client.cookies.clear()
    r = register(client, username="ROSA")
    assert r.status_code == 409
    assert r.json()["detail"]["code"] == "username_taken"


def test_register_validation(client):
    for username, password, code in [
        ("ro", "geheim123", "username_length"),
        ("rosa mae", "geheim123", "username_chars"),
        ("rosa", "kurz", "password_length"),
    ]:
        r = register(client, username=username, password=password)
        assert r.status_code == 422
        assert r.json()["detail"]["code"] == code


def test_login_logout(client):
    register(client)
    client.cookies.clear()
    assert client.get("/me").status_code == 401

    r = login(client, password="falsch123")
    assert r.status_code == 401
    assert r.json()["detail"]["code"] == "invalid_credentials"

    assert login(client, username="ROSA").status_code == 200  # case-insensitive
    assert client.get("/me").status_code == 200

    old_token = client.cookies.get("oo_session")
    assert client.post("/auth/logout").status_code == 200
    assert client.get("/me").status_code == 401
    # The token is invalid server-side, not just deleted from the browser
    assert old_token
    client.cookies.clear()
    assert client.get("/me", headers={"Cookie": f"oo_session={old_token}"}).status_code == 401


def test_login_unknown_user(client):
    r = login(client, username="niemand")
    assert r.status_code == 401


def test_recover_resets_password_rotates_key_and_ends_sessions(client):
    key = register(client).json()["recovery_key"]
    other_device = client.cookies.get("oo_session")
    client.cookies.clear()

    # Typed by hand: lowercase, spaces instead of hyphens
    r = recover(client, key.lower().replace("-", " "))
    assert r.status_code == 200, r.text
    new_key = r.json()["recovery_key"]
    assert new_key != key
    assert client.get("/me").status_code == 200  # logged in right away

    # Old sessions are gone, old password and old key no longer work
    assert client.get("/me", headers={"Cookie": f"oo_session={other_device}"}).status_code == 401
    client.cookies.clear()
    assert login(client).status_code == 401
    assert login(client, password="neuesPasswort").status_code == 200
    assert recover(client, key).status_code == 401
    assert recover(client, new_key, new_password="nochEinPasswort").status_code == 200


def test_recover_rejects_wrong_input(client):
    key = register(client).json()["recovery_key"]
    client.cookies.clear()
    wrong = ("0" if key[0] != "0" else "1") + key[1:]
    for username, k in [("rosa", wrong), ("niemand", key), ("rosa", "kaputt")]:
        r = recover(client, k, username=username)
        assert r.status_code == 401
        assert r.json()["detail"]["code"] == "invalid_recovery"
    r = recover(client, key, new_password="kurz")
    assert r.status_code == 422
    assert r.json()["detail"]["code"] == "password_length"
    assert login(client).status_code == 200  # nothing changed


def test_recover_rate_limit(client):
    for _ in range(5):
        recover(client, "x")
    r = recover(client, "x")
    assert r.status_code == 429


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
        login(client, username="x", password="falsch")
    r = login(client, username="x", password="falsch")
    assert r.status_code == 429
    assert r.json()["detail"]["code"] == "rate_limited"
