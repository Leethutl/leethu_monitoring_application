"""Shared pytest fixtures — temp inventory path so CI never touches real data/."""

from __future__ import annotations

import pytest

from app import create_app
from metrics import clear_history


@pytest.fixture()
def app(tmp_path):
    inventory = tmp_path / "servers.json"
    inventory.write_text("[]\n", encoding="utf-8")
    application = create_app(inventory_path=inventory, testing=True)
    application.config["SECRET_KEY"] = "test-secret"
    yield application
    clear_history()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def logged_in_client(client):
    resp = client.post(
        "/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)
    return client
