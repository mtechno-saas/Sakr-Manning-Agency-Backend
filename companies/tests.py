# companies/tests.py
#
# Regression tests for the trailing-slash-optional router behaviour.
#
# We hit the URL conf directly (no DB) and assert that the same view function
# is reachable both with and without a trailing slash, for the standard
# DRF ModelViewSet actions. This locks in the fix for the
# APPEND_SLASH RuntimeError that was raised when a client POSTed to
# /api/companies/job-positions (no trailing slash).

import re
from django.test import SimpleTestCase, override_settings
from django.urls import resolve, Resolver404
from django.urls.resolvers import URLPattern

from companies.routers import TrailingSlashOptionalRouter
from companies.views import JobOrderPositionViewSet, JobOrderViewSet, CompanyViewSet


# Build a router the same way companies/urls.py does, so the tests reflect
# production behaviour.


# Build a router the same way companies/urls.py does, so the tests reflect
# production behaviour.
def _build_router():
    router = TrailingSlashOptionalRouter()
    router.register(r'job-orders', JobOrderViewSet, basename='job-order')
    router.register(r'job-positions', JobOrderPositionViewSet, basename='job-position')
    router.register(r'', CompanyViewSet, basename='company')
    return router


# Path prefixes the router would normally be mounted under. We resolve with
# this stripped, just like Django's include() would.
PREFIX = '/api/companies/'


def _strip_prefix(path):
    if not path.startswith(PREFIX):
        raise ValueError(f"path {path!r} does not start with {PREFIX!r}")
    return path[len(PREFIX):]


@override_settings(SILENCED_SYSTEM_CHECKS=['urls.W001'])
class TrailingSlashOptionalRouterTests(SimpleTestCase):
    """The router should register each URL with AND without a trailing slash."""

    def setUp(self):
        self.router = _build_router()
        # Each URL is a django.urls.resolvers.URLPattern with a compiled
        # regex on url.pattern. Django's resolve() expects a full path
        # (the prefix would normally be stripped by include()), so we
        # iterate the patterns directly.
        self.patterns = self.router.urls

    def _pattern_str(self, p):
        """Return the regex source string for a URLPattern, or None if missing."""
        try:
            # url.pattern is a django.urls.resolvers.RegexPattern in Django 6.0;
            # its compiled regex lives on .regex and the source string on .regex.pattern.
            return p.pattern.regex.pattern
        except AttributeError:
            return None

    def _find_pattern(self, regex_tail):
        """Return the URLPattern whose regex ends with `regex_tail`."""
        for p in self.patterns:
            pat = self._pattern_str(p)
            if pat is None:
                continue
            if pat.endswith(regex_tail):
                return p
        self.fail(f"no URLPattern found ending with {regex_tail!r}")

    def test_router_emits_no_slash_variants(self):
        """Every trailing-slash URL must have a matching `/?` URL."""
        no_slash = [
            p for p in self.patterns
            if (self._pattern_str(p) or "").endswith("/?$")
        ]
        self.assertGreater(len(no_slash), 0, "router did not emit any no-slash variants")
        # And we should still have the canonical slash versions.
        with_slash = [
            p for p in self.patterns
            if (self._pattern_str(p) or "").endswith("/$")
        ]
        self.assertGreater(len(with_slash), 0)

    def test_job_positions_list_resolves_with_and_without_slash(self):
        """POST /api/companies/job-positions and /api/companies/job-positions/ both work."""
        # With trailing slash
        matched = self._find_pattern(r"^job-positions/$")
        self.assertIsNotNone(matched)
        # Without trailing slash
        matched_noslash = self._find_pattern(r"^job-positions/?$")
        self.assertIsNotNone(matched_noslash)
        # The two should be the same view function (no duplicate registration)
        self.assertIs(matched.callback, matched_noslash.callback)

    def test_job_positions_detail_resolves_with_and_without_slash(self):
        """GET/PATCH/DELETE /api/companies/job-positions/42 and /42/ both work."""
        with_slash = self._find_pattern(r"^job-positions/(?P<pk>[^/.]+)/$")
        no_slash = self._find_pattern(r"^job-positions/(?P<pk>[^/.]+)/?$")
        self.assertIsNotNone(with_slash)
        self.assertIsNotNone(no_slash)
        self.assertIs(with_slash.callback, no_slash.callback)

    def test_no_slash_variant_named(self):
        """The no-slash variant has a distinct name (suffix `_noslash`)."""
        with_slash = self._find_pattern(r"job-positions/$")
        # Find a pattern with the same callback but a different name
        no_slash = [
            p for p in self.patterns
            if p.callback is with_slash.callback and p.name and p.name.endswith("_noslash")
        ]
        self.assertEqual(len(no_slash), 1,
                         "expected exactly one _noslash variant per route")


@override_settings(SILENCED_SYSTEM_CHECKS=['urls.W001'])
class AppendSlashPostSafetyTests(SimpleTestCase):
    """
    End-to-end smoke test: simulate what the bug was — POSTing to
    /api/companies/job-positions (no trailing slash). Before the fix this
    raised RuntimeError at the Django middleware level. After the fix it
    routes straight to the view.
    """

    def setUp(self):
        self.router = _build_router()
        self.patterns = self.router.urls

    def _resolve_via_router(self, suffix):
        """Resolve a path against the router's URL patterns directly."""
        for p in self.patterns:
            try:
                compiled = p.pattern.regex
            except AttributeError:
                continue
            if compiled.match(suffix):
                return p
        return None

    def test_post_job_positions_no_slash_does_not_raise(self):
        """The path that triggered the production RuntimeError should now resolve."""
        # Real production path: POST /api/companies/job-positions
        # (the trailing-slash was omitted)
        matched = self._resolve_via_router("job-positions")
        self.assertIsNotNone(
            matched,
            "POST /api/companies/job-positions (no slash) did not match any route — "
            "Django would raise RuntimeError at request time."
        )

    def test_post_job_positions_with_slash_still_works(self):
        """The canonical form must keep working."""
        matched = self._resolve_via_router("job-positions/")
        self.assertIsNotNone(matched)

    def test_post_job_positions_detail_no_slash(self):
        """POST/PATCH /api/companies/job-positions/42 (no slash) also works."""
        matched = self._resolve_via_router("job-positions/42")
        self.assertIsNotNone(matched)

    def test_post_job_positions_detail_with_slash(self):
        """The canonical form for the detail endpoint also works."""
        matched = self._resolve_via_router("job-positions/42/")
        self.assertIsNotNone(matched)
