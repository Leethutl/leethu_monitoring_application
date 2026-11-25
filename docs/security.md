# Security notes (demo)

Leethu is a **local demo**, not a production monitor.

## What we protect (lightly)

- Admin password stored as a **Werkzeug hash** only (default demo password documented in README — change for any shared use)
- `SECRET_KEY` and optional `ADMIN_PASSWORD_HASH` from environment
- Session cleared on login and logout; logout is **POST-only**
- All pages and metrics APIs except `/login` require authentication
- Inventory JSON path is confined to the app data directory; server ids must be UUIDs (no path traversal)
- Field validation: hostname, SSH user, port range 1–65535, length limits, max 5 servers
- Metrics are **pure Python mocks** — no SSH, no shell, no remote agents
- Basic response headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`
- Static files served only via Flask’s `static/` folder

## Explicit non-goals / tradeoffs

- **No CSRF tokens** — acceptable only for a trusted local demo; do not expose on the public internet
- **No HTTPS**, rate limiting, RBAC, or multi-user accounts
- Binding `0.0.0.0:5779` exposes the app on all interfaces — use only on trusted networks
- Inventory may contain hostnames and SSH usernames; treat `data/servers.json` as sensitive for shared machines

## Threat model (demo)

| Risk | Mitigation |
|------|------------|
| Casual local access without login | Session gate on routes/APIs |
| Accidental secret commit | `.gitignore` for `.env`, venv; password hash only in config |
| Someone mistakes mock for live ops | UI banner + README/footer: mock metrics only |
