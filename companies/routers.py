# companies/routers.py
#
# Trailing-slash-optional router.
#
# Django's APPEND_SLASH=True (the default) means a GET to /api/companies/job-positions
# (no trailing slash) gets a 301 redirect to /api/companies/job-positions/ (with the
# trailing slash). But for POST / PUT / PATCH / DELETE, Django cannot safely
# change the request method on a redirect, so it raises RuntimeError instead:
#
#     "You called this URL via POST, but the URL doesn't end in a slash and you
#      have APPEND_SLASH set. Django can't redirect to the slash URL while
#      maintaining POST data."
#
# We hit this on production when a client (curl, a third-party integration, or
# a stale browser build) hits POST /api/companies/job-positions without the
# trailing slash. The fix is to register each router URL twice — once with the
# trailing slash (canonical), once without — so the no-slash request goes
# straight to the same view with no redirect needed.
#
# We use this router in companies/urls.py. The same router can be reused by
# other apps if they need the same behaviour (e.g. api/urls.py for the
# user-management endpoints).

import re
from rest_framework.routers import DefaultRouter
from django.urls.resolvers import URLPattern, RegexPattern


class TrailingSlashOptionalRouter(DefaultRouter):
    """
    Like :class:`rest_framework.routers.DefaultRouter`, but every URL pattern
    is also registered with the trailing slash made optional, so callers can
    POST / PUT / PATCH / DELETE without it and not hit the APPEND_SLASH
    RuntimeError.

    Example:

        router = TrailingSlashOptionalRouter()
        router.register(r'job-positions', JobOrderPositionViewSet,
                        basename='job-position')

        # Now all of these resolve to JobOrderPositionViewSet:
        #   GET    /api/companies/job-positions/        list
        #   GET    /api/companies/job-positions        list  (no slash)
        #   POST   /api/companies/job-positions/       create
        #   POST   /api/companies/job-positions        create  (no slash)
        #   GET    /api/companies/job-positions/42/     retrieve
        #   GET    /api/companies/job-positions/42     retrieve  (no slash)
        #   POST   /api/companies/job-positions/42/apply/  apply
        #   POST   /api/companies/job-positions/42/apply   apply  (no slash)
    """

    def get_urls(self):
        urls = super().get_urls()
        no_slash_urls = []
        for url in urls:
            # url is a django.urls.resolvers.URLPattern. The regex lives
            # on url.pattern.regex (a compiled re.Pattern in Django 6.0)
            # and the source string is on .pattern.
            try:
                regex = url.pattern.regex.pattern
            except AttributeError:
                # Older Django / different URLPattern structure — skip.
                continue
            # DRF's router always appends `/$` (slash + end anchor) to
            # its generated URL patterns. Replace the trailing `/$`
            # with `/?$` so the URL matches with or without a slash.
            if not regex.endswith("/$"):
                continue
            new_regex = regex[:-2] + "/?$"
            # Wrap the new regex in a RegexPattern so Django's URL
            # checker (which expects .name on the pattern) is happy.
            # We preserve the original name and any namespace metadata.
            new_pattern_obj = RegexPattern(new_regex, name=url.pattern.name)
            no_slash_urls.append(
                URLPattern(
                    new_pattern_obj,
                    url.callback,
                    default_args=url.default_args,
                    name=(url.name + "_noslash") if url.name else None,
                )
            )
        return urls + no_slash_urls
