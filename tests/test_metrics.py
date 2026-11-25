"""Mock metrics shape and API auth/404 tests."""

from metrics import generate_metrics


REQUIRED_KEYS = {
    "server_id",
    "ts",
    "cpu_percent",
    "memory",
    "network",
    "disk_percent",
    "load_avg",
    "uptime_seconds",
    "uptime_human",
    "ports",
}


def test_mock_metrics_shape():
    m = generate_metrics("00000000-0000-0000-0000-000000000099")
    assert REQUIRED_KEYS <= set(m.keys())
    assert "used_gb" in m["memory"]
    assert "total_gb" in m["memory"]
    assert "percent" in m["memory"]
    assert "rx_mbps" in m["network"]
    assert "tx_mbps" in m["network"]
    assert len(m["load_avg"]) == 3
    assert isinstance(m["ports"], list)
    for p in m["ports"]:
        assert {"port", "proto", "process"} <= set(p.keys())


def test_api_metrics_requires_auth(client):
    resp = client.get("/api/metrics")
    assert resp.status_code in (302, 303)


def test_api_metrics_ok_when_logged_in(logged_in_client):
    # Add a server first
    logged_in_client.post(
        "/manage",
        data={
            "action": "add",
            "hostname": "metrics-01.local",
            "ssh_user": "ubuntu",
            "ssh_port": "22",
            "label": "m1",
        },
    )
    resp = logged_in_client.get("/api/metrics")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "servers" in data
    assert len(data["servers"]) == 1
    assert "metrics" in data["servers"][0]
    assert "ssh_user" in data["servers"][0]["server"]
    # No password field in inventory/API
    assert "password" not in data["servers"][0]["server"]
    assert "ssh_password" not in data["servers"][0]["server"]


def test_api_unknown_server_404(logged_in_client):
    resp = logged_in_client.get(
        "/api/metrics/00000000-0000-0000-0000-000000000001"
    )
    assert resp.status_code == 404


def test_detail_page_200_when_logged_in(logged_in_client, app):
    from inventory import InventoryStore

    logged_in_client.post(
        "/manage",
        data={
            "action": "add",
            "hostname": "detail-01.local",
            "ssh_user": "ubuntu",
            "ssh_port": "22",
            "label": "detail",
        },
    )
    sid = InventoryStore(app.config["INVENTORY_PATH"]).list_servers()[0]["id"]
    resp = logged_in_client.get(f"/servers/{sid}")
    assert resp.status_code == 200
    assert b"Listening ports" in resp.data
    assert b"chart-cpu" in resp.data


def test_detail_anonymous_redirected(client):
    resp = client.get(
        "/servers/00000000-0000-0000-0000-000000000001",
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)
    assert "/login" in resp.headers["Location"]


def test_logout_clears_dashboard_access(logged_in_client):
    logged_in_client.post("/logout")
    resp = logged_in_client.get("/", follow_redirects=False)
    assert resp.status_code in (302, 303)
    assert "/login" in resp.headers["Location"]
    resp = logged_in_client.get("/api/metrics", follow_redirects=False)
    assert resp.status_code in (302, 303)
