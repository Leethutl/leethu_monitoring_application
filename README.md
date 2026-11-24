# Leethu

Local demo Flask UI for viewing mock Linux server metrics (CPU, memory, network, disk, ports) without SSH into each host.

Full product requirements: [docs/requirements.md](docs/requirements.md) · Build plan: [docs/TODO.md](docs/TODO.md)

## Hosting

| Item | Value |
|------|-------|
| Where | Local machine only (same host as Cursor) |
| Bind | `0.0.0.0` (all interfaces) |
| Port | `5779` |
| URL | `http://127.0.0.1:5779` |

**Security note:** Binding `0.0.0.0` exposes the demo on all network interfaces. Use only on trusted networks. Prefer opening via `http://127.0.0.1:5779`.

Not deployed to cloud, Docker, or remote servers. CI may run tests elsewhere; the app itself stays local.

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open [http://127.0.0.1:5779](http://127.0.0.1:5779).

Optional: set `SECRET_KEY` in the environment (demo default is used if unset — change it for any shared use).

```bash
export SECRET_KEY="your-own-secret"
python app.py
```

## UI pages

| Page | Path | Purpose |
|------|------|---------|
| **Dashboard** | `/` | Server overview; empty state when no inventory (“No servers yet”) |
| **Server detail** | `/servers/<id>` | Per-host metrics, charts, and ports (placeholder shell for now) |
| **Manage servers** | `/manage` | Add / edit / delete up to 5 hosts (placeholder shell for now) |

Login arrives in Phase 1. Inventory and mock metrics follow in later phases.

## UI look

Dark slate background with teal accents, DM Sans + IBM Plex Mono, sticky nav (Leethu brand, Dashboard, Manage servers), and dashed empty-state panels with a primary CTA. Static assets are served only from Flask’s `static/` folder.
