"""Leethu — demo Linux server monitoring UI (local run only)."""

from __future__ import annotations

from pathlib import Path

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

import auth
import config
from inventory import InventoryError, InventoryStore
from metrics import generate_metrics, get_history


def create_app(
    *,
    inventory_path: Path | None = None,
    testing: bool = False,
) -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["TESTING"] = testing
    app.config["INVENTORY_PATH"] = str(
        inventory_path or config.DEFAULT_INVENTORY_PATH
    )

    store = InventoryStore(Path(app.config["INVENTORY_PATH"]))

    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "same-origin"
        return response

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if auth.is_authenticated():
            return redirect(url_for("dashboard"))
        error = None
        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""
            if (
                username == config.ADMIN_USERNAME
                and auth.verify_password(password)
            ):
                auth.login_user(username)
                return redirect(url_for("dashboard"))
            error = "Invalid username or password"
        return render_template("login.html", error=error)

    @app.route("/logout", methods=["POST"])
    def logout():
        auth.logout_user()
        return redirect(url_for("login"))

    @app.route("/")
    @auth.login_required
    def dashboard():
        servers = store.list_servers()
        cards = []
        for server in servers:
            m = generate_metrics(server["id"])
            cards.append({"server": server, "metrics": m})
        return render_template("dashboard.html", cards=cards)

    @app.route("/servers/<server_id>")
    @auth.login_required
    def server_detail(server_id):
        server = store.get(server_id)
        if server is None:
            return render_template("server_detail.html", server=None), 404
        metrics = generate_metrics(server["id"])
        history = get_history(server["id"])
        return render_template(
            "server_detail.html",
            server=server,
            metrics=metrics,
            history=history,
        )

    @app.route("/manage", methods=["GET", "POST"])
    @auth.login_required
    def manage_servers():
        if request.method == "POST":
            action = request.form.get("action", "add")
            try:
                if action == "add":
                    store.add(
                        hostname=request.form.get("hostname", ""),
                        ssh_user=request.form.get("ssh_user", ""),
                        ssh_port=request.form.get("ssh_port", 22),
                        label=request.form.get("label", ""),
                    )
                    flash("Server added.", "ok")
                elif action == "edit":
                    store.update(
                        request.form.get("server_id", ""),
                        hostname=request.form.get("hostname", ""),
                        ssh_user=request.form.get("ssh_user", ""),
                        ssh_port=request.form.get("ssh_port", 22),
                        label=request.form.get("label", ""),
                    )
                    flash("Server updated.", "ok")
                elif action == "delete":
                    store.delete(request.form.get("server_id", ""))
                    flash("Server deleted.", "ok")
                else:
                    flash("Unknown action.", "error")
            except InventoryError as exc:
                flash(str(exc), "error")
            return redirect(url_for("manage_servers"))

        servers = store.list_servers()
        return render_template(
            "manage_servers.html",
            servers=servers,
            max_servers=config.MAX_SERVERS,
            at_limit=len(servers) >= config.MAX_SERVERS,
        )

    @app.route("/api/metrics")
    @auth.login_required
    def api_metrics_all():
        servers = store.list_servers()
        payload = []
        for server in servers:
            m = generate_metrics(server["id"])
            payload.append(
                {
                    "server": {
                        "id": server["id"],
                        "hostname": server["hostname"],
                        "label": server.get("label") or "",
                        "ssh_user": server["ssh_user"],
                        "ssh_port": server["ssh_port"],
                    },
                    "metrics": m,
                }
            )
        return jsonify({"servers": payload})

    @app.route("/api/metrics/<server_id>")
    @auth.login_required
    def api_metrics_one(server_id):
        server = store.get(server_id)
        if server is None:
            return jsonify({"error": "not found"}), 404
        metrics = generate_metrics(server["id"])
        history = get_history(server["id"])
        return jsonify(
            {
                "server": {
                    "id": server["id"],
                    "hostname": server["hostname"],
                    "label": server.get("label") or "",
                    "ssh_user": server["ssh_user"],
                    "ssh_port": server["ssh_port"],
                },
                "metrics": metrics,
                "history": history,
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    # Binds all interfaces — use only on trusted networks.
    # Open locally at http://127.0.0.1:5779
    app.run(host="0.0.0.0", port=5779, debug=True)
