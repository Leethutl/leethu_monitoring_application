"""Pure-Python mock metrics — no SSH or shell calls."""

from __future__ import annotations

import math
import time
from collections import defaultdict, deque
from typing import Any

import config

# In-memory ring buffers of recent samples per server id.
_history: dict[str, deque[dict[str, Any]]] = defaultdict(
    lambda: deque(maxlen=config.METRICS_HISTORY_POINTS)
)


def _seed(server_id: str) -> float:
    """Stable numeric seed derived from server id."""
    return sum(ord(c) for c in server_id) % 997 / 997.0


def _wave(seed: float, period: float, amp: float, mid: float) -> float:
    t = time.time()
    return mid + amp * math.sin((t / period) + seed * math.pi * 2)


def generate_metrics(server_id: str) -> dict[str, Any]:
    """Return current mock metrics for a server id (any string)."""
    seed = _seed(server_id)
    cpu = round(max(2.0, min(98.0, _wave(seed, 17, 18, 35 + seed * 20))), 1)
    mem_total_gb = 8 + int(seed * 24)  # 8–31 GiB
    mem_pct = round(max(15.0, min(92.0, _wave(seed + 0.1, 23, 12, 55))), 1)
    mem_used_gb = round(mem_total_gb * mem_pct / 100.0, 2)
    disk_pct = round(max(10.0, min(95.0, _wave(seed + 0.2, 41, 8, 48))), 1)
    net_rx = round(max(0.1, _wave(seed + 0.3, 11, 40, 55) + 20), 1)
    net_tx = round(max(0.1, _wave(seed + 0.4, 13, 25, 30) + 10), 1)
    load1 = round(max(0.05, cpu / 100 * (1.2 + seed)), 2)
    load5 = round(max(0.05, load1 * 0.85), 2)
    load15 = round(max(0.05, load1 * 0.7), 2)
    uptime_seconds = int(86_400 * (3 + seed * 20) + (time.time() % 86_400))

    sample = {
        "server_id": server_id,
        "ts": int(time.time()),
        "cpu_percent": cpu,
        "memory": {
            "used_gb": mem_used_gb,
            "total_gb": mem_total_gb,
            "percent": mem_pct,
        },
        "network": {
            "rx_mbps": net_rx,
            "tx_mbps": net_tx,
        },
        "disk_percent": disk_pct,
        "load_avg": [load1, load5, load15],
        "uptime_seconds": uptime_seconds,
        "uptime_human": _format_uptime(uptime_seconds),
        "ports": _mock_ports(server_id, seed),
    }
    _record_history(server_id, sample)
    return sample


def get_history(server_id: str) -> list[dict[str, Any]]:
    """Return short recent history suitable for charts (~1–2 minutes)."""
    # Ensure at least one sample exists.
    if not _history[server_id]:
        generate_metrics(server_id)
    return list(_history[server_id])


def clear_history() -> None:
    """Test helper — reset in-memory buffers."""
    _history.clear()


def _record_history(server_id: str, sample: dict[str, Any]) -> None:
    point = {
        "ts": sample["ts"],
        "cpu_percent": sample["cpu_percent"],
        "memory_percent": sample["memory"]["percent"],
        "disk_percent": sample["disk_percent"],
        "network_rx_mbps": sample["network"]["rx_mbps"],
        "network_tx_mbps": sample["network"]["tx_mbps"],
    }
    buf = _history[server_id]
    # Avoid duplicate points within the same second for rapid polling in tests.
    if buf and buf[-1]["ts"] == point["ts"]:
        buf[-1] = point
    else:
        buf.append(point)


def _format_uptime(seconds: int) -> str:
    days, rem = divmod(seconds, 86_400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours or days:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


def _mock_ports(server_id: str, seed: float) -> list[dict[str, Any]]:
    base = 20 + int(seed * 40)
    catalog = [
        {"port": 22, "proto": "tcp", "process": "sshd"},
        {"port": 80, "proto": "tcp", "process": "nginx"},
        {"port": 443, "proto": "tcp", "process": "nginx"},
        {"port": 5432, "proto": "tcp", "process": "postgres"},
        {"port": 6379, "proto": "tcp", "process": "redis-server"},
        {"port": 9100, "proto": "tcp", "process": "node_exporter"},
        {"port": 8080, "proto": "tcp", "process": "java"},
    ]
    count = 3 + (base % 4)
    # Rotate selection by seed so hosts look different.
    start = int(seed * len(catalog)) % len(catalog)
    selected = []
    for i in range(count):
        selected.append(dict(catalog[(start + i) % len(catalog)]))
    return selected
