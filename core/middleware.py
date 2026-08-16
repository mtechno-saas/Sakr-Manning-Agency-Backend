"""
Custom middleware for the project.

``CurrentUserMiddleware`` mirrors ``request.user`` into a thread-local so
signal handlers (and any other code that runs outside the view layer) can
ask "who triggered this request?" without re-plumbing the request object
through every call site.
"""
from .threadlocals import clear_current_user, set_current_user


class CurrentUserMiddleware:
    """
    Place near the end of ``MIDDLEWARE`` (after AuthenticationMiddleware
    so ``request.user`` is populated).

    Sets the thread-local user on the way in and clears it on the way
    out so a long-lived worker thread doesn't leak the previous request's
    user into the next request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ``request.user`` is set by AuthenticationMiddleware. For
        # anonymous requests it's ``AnonymousUser``; treat that as None
        # so callers can do a single truthy check.
        #
        # We deliberately only WRITE the threadlocal when the user is
        # authenticated. Leaving an anonymous request untouched is safe
        # because: (a) signal handlers treat ``None`` as "no actor";
        # (b) it lets tests that pre-set the threadlocal (e.g. for
        # APIClient.force_authenticate, which sets request.user AFTER
        # middleware runs) keep their value through the request.
        user = getattr(request, "user", None)
        if getattr(user, "is_authenticated", False):
            set_current_user(user)
        try:
            return self.get_response(request)
        finally:
            # Always clear so a long-lived worker thread doesn't leak
            # the previous request's user into the next request.
            clear_current_user()
