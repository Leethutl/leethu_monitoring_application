"""Application configuration — secrets from env with safe demo defaults."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_INVENTORY_PATH = DATA_DIR / "servers.json"

# Demo-only defaults. Change SECRET_KEY and ADMIN_PASSWORD_HASH for any shared use.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me-leethu-demo")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")

# Default demo password is "admin" — never store plaintext in the repo.
# Override with ADMIN_PASSWORD_HASH env, or generate:
#   python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('yourpass'))"
ADMIN_PASSWORD_HASH = os.environ.get(
    "ADMIN_PASSWORD_HASH",
    "scrypt:32768:8:1$eM7w84LyGH8c3xMT$716f65373134232e576a67e2b60740813c7fe21c9dae66e998737c9b6c55d5b1f897bc7d0d736f52299d224c26669b60eaeaf043c753baf37d22ddfcc3105404",
)

MAX_SERVERS = 5
METRICS_HISTORY_POINTS = 24  # ~2 minutes at 5s refresh
