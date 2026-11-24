"""Leethu — demo Linux server monitoring UI (local run only)."""

import os

from flask import Flask, render_template

app = Flask(__name__)

# Demo default only — set SECRET_KEY in the environment for any shared use.
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-only-change-me-leethu-demo"
)


@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "same-origin"
    return response


@app.route("/")
def dashboard():
    """Dashboard placeholder — empty until servers are added (Phase 2+)."""
    servers = []
    return render_template("dashboard.html", servers=servers)


@app.route("/servers/<server_id>")
def server_detail(server_id):
    """Server detail placeholder."""
    return render_template(
        "server_detail.html",
        server_id=server_id,
        server=None,
    )


@app.route("/manage")
def manage_servers():
    """Manage servers placeholder."""
    servers = []
    return render_template("manage_servers.html", servers=servers)


if __name__ == "__main__":
    # Binds all interfaces — use only on trusted networks.
    # Open locally at http://127.0.0.1:5779
    app.run(host="0.0.0.0", port=5779, debug=True)
