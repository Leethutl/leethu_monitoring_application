"""Auth unit tests — login, logout, protected routes."""


def test_login_success_creates_session(client):
    resp = client.post(
        "/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)
    assert resp.headers["Location"].endswith("/")
    with client.session_transaction() as sess:
        assert sess.get("user") == "admin"


def test_login_failure_does_not_create_session(client):
    resp = client.post(
        "/login",
        data={"username": "admin", "password": "wrong"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Invalid username or password" in resp.data
    with client.session_transaction() as sess:
        assert "user" not in sess


def test_logout_clears_session(logged_in_client):
    resp = logged_in_client.post("/logout", follow_redirects=False)
    assert resp.status_code in (302, 303)
    assert "/login" in resp.headers["Location"]
    with logged_in_client.session_transaction() as sess:
        assert "user" not in sess


def test_logout_get_not_allowed(logged_in_client):
    resp = logged_in_client.get("/logout")
    assert resp.status_code == 405


def test_protected_routes_redirect_when_logged_out(client):
    for path in ("/", "/manage", "/servers/00000000-0000-0000-0000-000000000001"):
        resp = client.get(path, follow_redirects=False)
        assert resp.status_code in (302, 303)
        assert "/login" in resp.headers["Location"]


def test_api_requires_auth(client):
    resp = client.get("/api/metrics")
    assert resp.status_code in (302, 303)
    assert "/login" in resp.headers["Location"]
