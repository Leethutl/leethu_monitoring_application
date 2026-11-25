"""Authentication helpers for the single demo admin user."""

from functools import wraps

from flask import redirect, session, url_for
from werkzeug.security import check_password_hash

import config


def verify_password(password: str) -> bool:
    """Check a plaintext password against the configured admin hash."""
    if not password:
        return False
    return check_password_hash(config.ADMIN_PASSWORD_HASH, password)


def login_user(username: str) -> None:
    """Establish a fresh session for the authenticated admin."""
    session.clear()
    session["user"] = username
    session.permanent = False


def logout_user() -> None:
    """Clear the session entirely."""
    session.clear()


def is_authenticated() -> bool:
    return session.get("user") == config.ADMIN_USERNAME


def login_required(view):
    """Redirect anonymous users to /login without leaking resource existence."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped
