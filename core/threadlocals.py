"""
Per-request thread-local storage.

Why this exists
---------------
Some parts of the system (notably the notification signals wired in the
``notifications`` app) need to know *which* user triggered a write so the
email that follows can be addressed correctly. Django signals fire from
``post_save`` / ``post_delete`` and do not get the request as a kwarg.

The standard fix is a small middleware that stashes the request user in a
``threading.local()`` and a tiny accessor that signal handlers can call.

Usage
-----
    from core.threadlocals import get_current_user

    actor = get_current_user()  # may be None outside an HTTP request
"""
import threading

_local = threading.local()


def set_current_user(user) -> None:
    """Stash the user that's making the current request (or None)."""
    _local.user = user


def get_current_user():
    """Return the user that triggered the current request, or None.

    Returns None when called outside an HTTP request (e.g. from a
    management command, the Django shell, or a Celery worker).
    """
    return getattr(_local, "user", None)


def clear_current_user() -> None:
    """Forget the current user. Called by the middleware on the way out."""
    _local.user = None
