"""Inventory CRUD, max-5, and validation tests."""

import uuid


def _add(client, hostname="10.0.0.1", ssh_user="ubuntu", ssh_port="22", label=""):
    return client.post(
        "/manage",
        data={
            "action": "add",
            "hostname": hostname,
            "ssh_user": ssh_user,
            "ssh_port": ssh_port,
            "label": label,
        },
        follow_redirects=True,
    )


def test_add_list_edit_delete(logged_in_client, app):
    from inventory import InventoryStore

    store = InventoryStore(app.config["INVENTORY_PATH"])

    resp = _add(logged_in_client, hostname="app-01.local", label="API")
    assert resp.status_code == 200
    servers = store.list_servers()
    assert len(servers) == 1
    assert servers[0]["hostname"] == "app-01.local"
    sid = servers[0]["id"]

    resp = logged_in_client.post(
        "/manage",
        data={
            "action": "edit",
            "server_id": sid,
            "hostname": "app-02.local",
            "ssh_user": "deploy",
            "ssh_port": "2222",
            "label": "API-2",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    updated = store.get(sid)
    assert updated["hostname"] == "app-02.local"
    assert updated["ssh_user"] == "deploy"
    assert updated["ssh_port"] == 2222

    resp = logged_in_client.post(
        "/manage",
        data={"action": "delete", "server_id": sid},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert store.list_servers() == []


def test_max_five_rejection(logged_in_client, app):
    from inventory import InventoryStore

    store = InventoryStore(app.config["INVENTORY_PATH"])
    for i in range(5):
        _add(logged_in_client, hostname=f"host-{i}.local", label=f"h{i}")
    assert len(store.list_servers()) == 5

    resp = _add(logged_in_client, hostname="host-6.local")
    assert b"Maximum of 5" in resp.data
    assert len(store.list_servers()) == 5


def test_invalid_port_rejected(logged_in_client, app):
    from inventory import InventoryStore

    store = InventoryStore(app.config["INVENTORY_PATH"])
    resp = _add(logged_in_client, hostname="ok.local", ssh_port="70000")
    assert b"SSH port must be between 1 and 65535" in resp.data
    assert store.list_servers() == []


def test_empty_hostname_rejected(logged_in_client, app):
    from inventory import InventoryStore

    store = InventoryStore(app.config["INVENTORY_PATH"])
    resp = _add(logged_in_client, hostname="   ")
    assert b"Invalid hostname" in resp.data
    assert store.list_servers() == []


def test_unknown_id_delete_rejected(logged_in_client, app):
    from inventory import InventoryStore

    store = InventoryStore(app.config["INVENTORY_PATH"])
    fake = str(uuid.uuid4())
    resp = logged_in_client.post(
        "/manage",
        data={"action": "delete", "server_id": fake},
        follow_redirects=True,
    )
    assert b"Unknown server" in resp.data
    assert store.list_servers() == []


def test_path_traversal_id_ignored(logged_in_client, app):
    from inventory import InventoryStore

    store = InventoryStore(app.config["INVENTORY_PATH"])
    resp = logged_in_client.post(
        "/manage",
        data={"action": "delete", "server_id": "../etc/passwd"},
        follow_redirects=True,
    )
    assert b"Unknown server" in resp.data
    assert store.list_servers() == []
