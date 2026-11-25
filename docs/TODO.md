# TODO: Demo Monitoring Infrastructure

Small increments for AI-assisted development. Each step includes **implementation**, **security**, and **docs**. Check boxes as you complete them.

Reference: [requirements.md](./requirements.md)

---

## Hosting (explicit)

| Item | Decision |
|------|----------|
| **Where** | Local machine only — the same host where Cursor is running |
| **Bind** | `0.0.0.0` (all interfaces) |
| **Port** | `5779` |
| **URL** | `http://127.0.0.1:5779` (or `http://<host-ip>:5779` on the LAN) |
| **How** | `python app.py` after venv + `pip install -r requirements.txt` |
| **Not hosted on** | Cloud, Docker, Kubernetes, or remote servers (out of scope) |

CI (GitHub Actions) runs tests in the cloud; **the app itself is not deployed there**.

---

## Phase 0 — Project initialization & basic UI

### Step 0.1 — Repo skeleton
- [x] Create project layout: `app.py`, `requirements.txt`, `.gitignore`, `README.md`, `docs/`
- [x] **Security:** Add `.gitignore` entries for `.venv/`, `__pycache__/`, `.env`, secrets, and inventory JSON if it may hold demo credentials
- [x] **Docs:** README with one-line project purpose and link to `docs/requirements.md`

### Step 0.2 — Flask app boots locally (hosting target)
- [x] Minimal Flask app that serves `/` with a placeholder page bound to `0.0.0.0:5779`
- [x] Start with `app.run(host="0.0.0.0", port=5779)` (or equivalent)
- [x] Pin Flask (and later deps) in `requirements.txt`
- [x] **Security:** Do not hardcode secrets; use a placeholder `SECRET_KEY` from env with a safe demo default documented; document that `0.0.0.0` exposes the demo on all interfaces — use only on trusted networks
- [x] **Docs:** README “Hosting” + “Local run” — bind `0.0.0.0:5779`, open `http://127.0.0.1:5779` (venv → pip → `python app.py`)

### Step 0.3 — Basic UI shell
- [x] Base template (nav, footer, CSS) — attractive, simple layout
- [x] Placeholder pages: Dashboard, Server detail, Manage servers (static / empty)
- [x] **Security:** Set basic response headers where easy (e.g. `X-Content-Type-Options: nosniff`); no inline secrets in templates
- [x] **Docs:** Short note in README describing main UI pages

### Step 0.4 — Static assets & polish
- [x] Shared CSS; consistent colors/typography for demo look
- [x] Empty-state messaging on dashboard (“No servers yet”)
- [x] **Security:** Serve static files via Flask static folder only; no directory listing of project root
- [x] **Docs:** Update README screenshot/placeholder description of UI

---

## Phase 1 — Sign-in & unit tests

### Step 1.1 — Password hashing helper
- [x] Add hashed password for default user `admin` (Werkzeug `generate_password_hash` / `check_password_hash`)
- [x] Store hash in config/env — never store plaintext password in repo
- [x] **Security:** Document that default demo password must be changed for any shared use; hash only in code/config
- [x] **Docs:** Auth section in README (username `admin`, how password hash is set)

### Step 1.2 — Login / logout routes
- [x] `GET/POST /login` form; `POST /logout`
- [x] Flask session after successful login
- [x] **Security:** POST-only logout; regenerate/clear session on login & logout; CSRF not required for pure local demo but document the tradeoff
- [x] **Docs:** Login steps in README

### Step 1.3 — Protect routes
- [x] Require login for dashboard, detail, manage pages; redirect anonymous users to `/login`
- [x] **Security:** Central `@login_required` decorator; do not leak whether a server id exists to anonymous users
- [x] **Docs:** Note “all pages except login require auth”

### Step 1.4 — Unit tests for auth
- [x] Add `pytest` (+ Flask test client); tests for login success, login failure, logout, protected redirect
- [x] **Security:** Assert failed login does not create a session; assert protected routes return redirect/401 when logged out
- [x] **Docs:** README “Tests” — `pytest` command

### Step 1.5 — CI: GitHub Actions (tests)
- [x] Add `.github/workflows/ci.yml`: checkout, setup Python, install deps, run `pytest`
- [x] **Security:** No secrets in workflow; use public demo config only
- [x] **Docs:** Badge or “CI” note in README pointing at the workflow

---

## Phase 2 — Server inventory (JSON, max 5)

### Step 2.1 — JSON storage layer
- [x] Read/write server list from a JSON file (e.g. `data/servers.json`)
- [x] Schema: id, hostname/IP, ssh_user, ssh_port (default 22), label
- [x] **Security:** Validate/sanitize fields; path confined to app data dir (no user-controlled file paths)
- [x] **Docs:** Document JSON schema and file location

### Step 2.2 — List & add servers
- [x] Manage page: list servers; add form; enforce **max 5**
- [x] **Security:** Server-side validation (required fields, port range 1–65535, length limits); reject over-limit adds
- [x] **Docs:** Update Manage servers usage in README

### Step 2.3 — Edit & delete
- [x] Edit and delete by id; confirm delete in UI
- [x] **Security:** Only allow mutating known ids; POST for mutations; no path traversal via id
- [x] **Docs:** CRUD behavior + max-5 rule

### Step 2.4 — Inventory unit tests
- [x] Tests: add, edit, delete, max-5 rejection, validation failures
- [x] **Security:** Tests for invalid port / empty hostname rejection
- [x] **Docs:** Mention inventory tests in README Tests section

### Step 2.5 — CI: extend workflow
- [x] Ensure CI runs full test suite including inventory tests
- [x] **Security:** Use temp JSON path in tests so CI never touches real `data/`
- [x] **Docs:** Note CI covers auth + inventory

---

## Phase 3 — Mock metrics & dashboard

### Step 3.1 — Mock metrics generator
- [x] Function returning CPU, memory, network, disk, load, uptime, ports for a server id
- [x] Deterministic-enough values suitable for demo (slight variation OK)
- [x] **Security:** No shell/SSH calls; pure Python mock only
- [x] **Docs:** Clarify metrics are mock in README and UI footer/banner

### Step 3.2 — Dashboard live summary
- [x] Show each server with key metrics (CPU, memory, disk)
- [x] Wire dashboard to inventory + mock generator
- [x] **Security:** Auth-gated; only show servers from inventory JSON
- [x] **Docs:** Dashboard field descriptions (brief)

### Step 3.3 — Metrics JSON API (for refresh)
- [x] Auth-protected endpoint(s) returning current metrics (+ optional history points)
- [x] **Security:** Login required; validate server id; no sensitive SSH password fields in API (inventory has no password field)
- [x] **Docs:** Document API paths briefly in `docs/` or README

### Step 3.4 — Auto-refresh (5s)
- [x] Frontend polls every 5s and updates dashboard numbers
- [x] **Security:** Same-origin fetch with session cookie; no API keys in JS
- [x] **Docs:** Note 5s refresh behavior

### Step 3.5 — Metrics unit tests + CI
- [x] Tests: mock shape/keys; API requires auth; unknown server → 404
- [x] **Security:** Unauthenticated API access rejected
- [x] **Docs:** CI still green with new tests

---

## Phase 4 — Server detail, ports, charts

### Step 4.1 — Server detail page
- [x] Full metrics for one server (all PRD fields)
- [x] **Security:** Auth + valid id only; 404 for missing
- [x] **Docs:** Detail page walkthrough (short)

### Step 4.2 — Listening ports table
- [x] Mock ports list (port, proto, process name)
- [x] **Security:** Display-only; no “kill process” or remote actions
- [x] **Docs:** Ports are mock data

### Step 4.3 — Short history charts
- [x] Chart.js (or similar) for CPU, memory, network, disk (~1–2 min window)
- [x] Keep short ring buffer of mock history per server (in memory OK for demo)
- [x] **Security:** Load chart lib from pinned local static or trusted CDN; document choice
- [x] **Docs:** Chart metrics and window length

### Step 4.4 — Detail auto-refresh (5s)
- [x] Refresh numbers + charts every 5s
- [x] **Security:** Auth-protected data endpoints only
- [x] **Docs:** Confirm refresh on detail page

### Step 4.5 — UI tests / smoke + CI
- [x] Smoke tests: detail page 200 when logged in; charts endpoint/data shape
- [x] **Security:** Anonymous detail access redirected
- [x] **Docs:** Final acceptance checklist vs PRD §9

---

## Phase 5 — Hardening, docs polish, CI complete

### Step 5.1 — Security pass
- [x] Review: hashed password only, session secret from env, validated inputs, auth on all mutating routes, no real SSH
- [x] **Security:** Add brief `docs/security.md` (demo threats & non-goals)
- [x] **Docs:** Link security note from README

### Step 5.2 — README finalization
- [x] Complete minimal run steps, default login, test command, out-of-scope (no multi-user/RBAC/Docker)
- [x] Document hosting clearly: local Cursor host, bind `0.0.0.0:5779` → `http://127.0.0.1:5779`; no cloud/Docker deploy
- [x] **Security:** Warn: local demo only — not for production
- [x] **Docs:** Align README with PRD acceptance criteria

### Step 5.3 — GitHub Actions finalize
- [x] CI: lint optional (e.g. `ruff` or skip if too heavy), `pytest` required on push/PR
- [x] **Security:** `permissions: contents: read` on workflow; no deploy secrets
- [x] **Docs:** Document CI triggers in README

### Step 5.4 — Demo acceptance walkthrough
- [x] Manually verify PRD §9 checklist locally
- [x] **Security:** Confirm logout clears access to dashboard/API
- [x] **Docs:** Check off PRD acceptance criteria; leave unchecked items noted

---

## Suggested order (summary)

| Order | Focus |
|------:|-------|
| 0 | Hosting = local Cursor machine, bind `0.0.0.0:5779` |
| 1 | Init + basic UI (Phase 0) |
| 2 | Sign-in + auth unit tests + CI (Phase 1) |
| 3 | Server inventory JSON CRUD (Phase 2) |
| 4 | Mock metrics + 5s refresh (Phase 3) |
| 5 | Detail, ports, charts (Phase 4) |
| 6 | Security/docs/CI polish (Phase 5) |

Work **one step at a time**. Do not skip security or docs checkboxes within a step.
