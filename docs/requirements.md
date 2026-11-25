# PRD: Demo Monitoring Infrastructure (Linux Servers)

## 1. Overview

Local demo web app for internal L1/L2/L3 and app/infra teams to view Linux server metrics without logging into each host.

**Problem:** Checking live memory, CPU, network, and port usage requires SSH into each server.

**Goal:** A simple, attractive, read-only Flask UI with mock metrics for up to 5 demo servers.

## 2. Users

| Role | Access |
|------|--------|
| Single admin | Sign in, manage server inventory, view all metrics |

No multi-user accounts. No RBAC.

## 3. Scope

### In scope

- Flask UI (read-only metrics views)
- Single admin login (hashed password)
- Add / edit / delete up to **5** Linux servers
- Mock metrics + short history charts
- Auto-refresh every **5 seconds**
- Local run only (where Cursor is running)

### Out of scope

- Multi-user accounts
- RBAC
- Docker / containerized deploy
- Real SSH or agents (mock data only)
- Alerts, email, HTTPS

## 4. Features

### F1 — Read-only, user-friendly UI

- Dashboard of monitored servers
- Per-server detail with metrics and short charts
- Ports view on server detail
- No actions that change remote systems (metrics are display-only)

### F2 — Admin sign-in

- Default username: `admin`
- Password stored hashed (e.g. Werkzeug)
- Session required for all pages except login
- Simple logout

### F3 — Server inventory (max 5)

Fields:

| Field | Required |
|-------|----------|
| Hostname / IP | Yes |
| SSH user | Yes |
| SSH port | Yes (default 22) |
| Label | Optional |

Actions: **Add**, **Edit**, **Delete**. Block add when count = 5.

> SSH fields are inventory metadata for the demo only; data is **not** collected over SSH.

## 5. Metrics (mock)

Per server, refreshed every **5s**:

| Metric | Display |
|--------|---------|
| CPU | % |
| Memory | used / total / % |
| Network | rx / tx |
| Disk | % |
| Load average | 1 / 5 / 15 |
| Uptime | human-readable |
| Listening ports | list (port, proto, process name mock) |

**Charts:** short recent history (e.g. last ~1–2 minutes) for CPU, memory, network, disk.

## 6. UI pages

1. **Login**
2. **Dashboard** — server cards/list + high-level status
3. **Server detail** — live metrics, short charts, ports
4. **Manage servers** — add / edit / delete (admin)

## 7. Tech stack

| Layer | Choice |
|-------|--------|
| Backend | Python + Flask |
| Frontend | Flask templates + CSS (attractive, simple) |
| Charts | Lightweight JS chart lib (e.g. Chart.js) |
| Auth | Flask session + hashed password |
| Storage | JSON file for server inventory |
| Metrics | Local mock / demo generator |

## 8. Hosting & local run (minimal)

| Item | Value |
|------|-------|
| Host bind | `0.0.0.0` |
| Port | `5779` |
| URL | `http://127.0.0.1:5779` |

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

App must start with `host="0.0.0.0"` and `port=5779`. Open `http://127.0.0.1:5779` and sign in as `admin`.

## 9. Acceptance criteria

- [x] Login works with `admin` + hashed password; unauthenticated users redirected to login
- [x] UI is usable and metrics views are read-only
- [x] Can add / edit / delete servers; max 5 enforced
- [x] Dashboard and server detail show all metrics listed above
- [x] Short charts update; page data refreshes every 5s
- [x] Metrics come from mock data (no real remote collection)
- [x] Runs locally with the steps in §8

## 10. Non-goals (reminder)

Not a production monitor. No multi-user, RBAC, or Docker for this demo.
