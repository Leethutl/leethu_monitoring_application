"""JSON server inventory — path confined to the app data directory."""

from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any

import config

_HOST_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,253}$")
_USER_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
_ID_RE = re.compile(r"^[a-f0-9-]{36}$")


class InventoryError(ValueError):
    """Validation or business-rule failure."""


class InventoryStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path) if path else config.DEFAULT_INVENTORY_PATH
        self._ensure_parent()

    def _ensure_parent(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            raise InventoryError("Inventory file must contain a JSON array")
        return data

    def _write(self, servers: list[dict[str, Any]]) -> None:
        self._ensure_parent()
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(servers, fh, indent=2)
            fh.write("\n")
        tmp.replace(self.path)

    def list_servers(self) -> list[dict[str, Any]]:
        return list(self._read())

    def get(self, server_id: str) -> dict[str, Any] | None:
        if not _ID_RE.match(server_id or ""):
            return None
        for server in self._read():
            if server.get("id") == server_id:
                return dict(server)
        return None

    def add(
        self,
        *,
        hostname: str,
        ssh_user: str,
        ssh_port: int | str = 22,
        label: str = "",
    ) -> dict[str, Any]:
        servers = self._read()
        if len(servers) >= config.MAX_SERVERS:
            raise InventoryError(f"Maximum of {config.MAX_SERVERS} servers allowed")
        record = self._validated(
            hostname=hostname,
            ssh_user=ssh_user,
            ssh_port=ssh_port,
            label=label,
        )
        record["id"] = str(uuid.uuid4())
        servers.append(record)
        self._write(servers)
        return record

    def update(
        self,
        server_id: str,
        *,
        hostname: str,
        ssh_user: str,
        ssh_port: int | str = 22,
        label: str = "",
    ) -> dict[str, Any]:
        if not _ID_RE.match(server_id or ""):
            raise InventoryError("Unknown server")
        servers = self._read()
        for idx, server in enumerate(servers):
            if server.get("id") == server_id:
                record = self._validated(
                    hostname=hostname,
                    ssh_user=ssh_user,
                    ssh_port=ssh_port,
                    label=label,
                )
                record["id"] = server_id
                servers[idx] = record
                self._write(servers)
                return record
        raise InventoryError("Unknown server")

    def delete(self, server_id: str) -> None:
        if not _ID_RE.match(server_id or ""):
            raise InventoryError("Unknown server")
        servers = self._read()
        new_servers = [s for s in servers if s.get("id") != server_id]
        if len(new_servers) == len(servers):
            raise InventoryError("Unknown server")
        self._write(new_servers)

    @staticmethod
    def _validated(
        *,
        hostname: str,
        ssh_user: str,
        ssh_port: int | str,
        label: str,
    ) -> dict[str, Any]:
        hostname = (hostname or "").strip()
        ssh_user = (ssh_user or "").strip()
        label = (label or "").strip()

        if not hostname or not _HOST_RE.match(hostname):
            raise InventoryError("Invalid hostname / IP")
        if len(hostname) > 253:
            raise InventoryError("Hostname too long")
        if not ssh_user or not _USER_RE.match(ssh_user):
            raise InventoryError("Invalid SSH user")
        try:
            port = int(ssh_port)
        except (TypeError, ValueError) as exc:
            raise InventoryError("SSH port must be an integer") from exc
        if port < 1 or port > 65535:
            raise InventoryError("SSH port must be between 1 and 65535")
        if len(label) > 64:
            raise InventoryError("Label too long (max 64 characters)")

        return {
            "hostname": hostname,
            "ssh_user": ssh_user,
            "ssh_port": port,
            "label": label,
        }
