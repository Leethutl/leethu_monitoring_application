# Leethu

Local demo Flask UI for viewing **mock** Linux server metrics (CPU, memory, network, disk, ports) without SSH into each host.

Full product requirements: [docs/requirements.md](docs/requirements.md) · Build plan: [docs/TODO.md](docs/TODO.md) · Security: [docs/security.md](docs/security.md)

> **Local demo only — not for production.** No multi-user accounts, RBAC, Docker, or real remote collection.

[![CI](https://github.com/Leethutl/leethu_monitoring_application/actions/workflows/ci.yml/badge.svg)](https://github.com/Leethutl/leethu_monitoring_application/actions/workflows/ci.yml)

## Hosting

| Item | Value |
|------|-------|
| Where | Local machine only (same host as Cursor) |
| Bind | `0.0.0.0` (all interfaces) |
| Port | `5779` |
| URL | `http://127.0.0.1:5779` |

**Security note:** Binding `0.0.0.0` exposes the demo on all network interfaces. Use only on trusted networks. Prefer opening via `http://127.0.0.1:5779`.

Not deployed to cloud, Docker, or remote servers. CI runs tests in GitHub Actions; the app itself stays local.

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open [http://127.0.0.1:5779](http://127.0.0.1:5779) and sign in.

```bash
export SECRET_KEY="your-own-secret"
python app.py
```

## Auth

| Item | Value |
|------|-------|
| Username | `admin` |
| Default demo password | `admin` |
| Storage | Werkzeug password hash (`ADMIN_PASSWORD_HASH` / `config.py`) — never plaintext in the repo |

Change the demo password for any shared use. Generate a new hash:

```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('yourpass'))"
```

Then set `ADMIN_PASSWORD_HASH` in the environment (or update the default in `config.py`).

All pages except `/login` require authentication. Logout is POST-only (`Log out` in the nav). CSRF protection is omitted for this trusted local demo — see [docs/security.md](docs/security.md).

## UI pages

| Page | Path | Purpose |
|------|------|---------|
| **Login** | `/login` | Admin sign-in |
| **Dashboard** | `/` | Server cards with CPU / memory / disk; auto-refresh every **5s** |
| **Server detail** | `/servers/<id>` | Full metrics, ~2 min Chart.js history, mock listening ports; 5s refresh |
| **Manage servers** | `/manage` | Add / edit / delete up to **5** hosts |

Dashboard fields: CPU %, memory %, disk %. Detail adds network rx/tx, load average, uptime, and ports (display-only — no kill/remote actions).

## Manage servers (inventory)

JSON file: `data/servers.json` (created/updated by the app).

| Field | Required | Notes |
|-------|----------|-------|
| `id` | yes | UUID assigned on add |
| `hostname` | yes | Hostname or IP |
| `ssh_user` | yes | Inventory metadata only |
| `ssh_port` | yes | Default 22; range 1–65535 |
| `label` | no | Display name |

Max **5** servers. SSH fields are **not** used for collection — metrics are mock.

## Metrics API

Session cookie required (same-origin fetch from the UI).

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/metrics` | All inventory servers + current mock metrics |
| GET | `/api/metrics/<id>` | One server + metrics + short history |

Unauthenticated callers are redirected to `/login`. Unknown ids return `404`. No SSH password fields exist in inventory or API responses.

Charts use **Chart.js 4.4.7** vendored at `static/vendor/chart.umd.min.js` (pinned local copy).

## Tests

```bash
source .venv/bin/activate
pytest -q
```

Covers auth (login success/failure, logout, protected redirects), inventory CRUD / max-5 / validation, mock metrics shape, and auth-gated APIs. Tests use a **temp** JSON path so CI never writes real `data/`.

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on push/PR to `main`: checkout → Python 3.10 → `pip install -r requirements.txt` → `pytest`. Workflow `permissions: contents: read` only; no deploy secrets.

## UI look

Dark slate + teal accents, DM Sans + IBM Plex Mono, sticky nav, mock-metrics banner, empty states, and 5s live refresh on dashboard/detail.
