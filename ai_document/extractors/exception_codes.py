"""Canonical error codes for the upload pipeline.

Why this exists:
    The previous ``/ai/upload/`` endpoint conflated every failure mode into
    one of three responses:

        * ``"Invalid document"`` (any LLM failure or non-CV upload)
        * The raw exception text in the 500 body
        * An empty 200 with a half-populated dict

    The view layer must NEVER leak raw exception messages to the client, and
    must NEVER use a single generic "Invalid document" label for unrelated
    failure modes. This module is the single source of truth for what the
    client can be told.

Contract:
    ``ErrorCode`` is a ``str`` enum, so it serialises to JSON as the value
    (``"not_a_cv"``) without a custom encoder. ``client_message()`` returns a
    human-readable string that is SAFE to return in an HTTP response.
"""

from __future__ import annotations

from enum import Enum


class ErrorCode(str, Enum):
    """All error codes that ``/ai/upload/`` can return to the client.

    Values are the wire format. Add new codes here so the catalogue stays
    exhaustive — do not invent string literals in views/tests.
    """

    # ── File / upload shape ────────────────────────────────────────────
    FILE_MISSING            = "file_missing"
    FILE_TOO_LARGE          = "file_too_large"
    FILE_UNSUPPORTED_FORMAT = "file_unsupported_format"

    # ── Document content classification ───────────────────────────────
    NOT_A_CV                = "not_a_cv"               # random non-CV PDF/DOCX
    NOT_SAKR_TEMPLATE       = "not_sakr_template"      # a CV, but not our form
    PARSE_FAILED            = "parse_failed"           # Sakr form detected, but field parse broke

    # ── Pipeline / extractor failures ──────────────────────────────────
    EXTRACTOR_UNAVAILABLE   = "extractor_unavailable"  # all extractors failed
    LLM_UNAVAILABLE         = "llm_unavailable"        # LLM fallback (later) failed

    # ── Persistence / dedup ────────────────────────────────────────────
    DUPLICATE_UPLOAD        = "duplicate_upload"       # same file hash within TTL
    AUTH_REQUIRED           = "auth_required"

    # ── Catch-all (NEVER leak underlying exception text) ───────────────
    INTERNAL                = "internal_error"


# Safe client-facing messages. These are the ONLY strings we put in HTTP
# response bodies. They are deliberately generic so they do not leak
# implementation details, internal model state, or stack traces.
CLIENT_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.FILE_MISSING:            "Please attach a CV file (PDF or DOCX).",
    ErrorCode.FILE_TOO_LARGE:          "File is too large. Maximum size is 20 MB.",
    ErrorCode.FILE_UNSUPPORTED_FORMAT: "Only PDF and DOCX files are supported.",

    ErrorCode.NOT_A_CV:                "This document does not look like a CV.",
    ErrorCode.NOT_SAKR_TEMPLATE:       "We support the standard Sakr Manning Agency form. Please upload that template.",
    ErrorCode.PARSE_FAILED:            "We could not read this document. Try re-uploading, or contact support if the problem persists.",

    ErrorCode.EXTRACTOR_UNAVAILABLE:   "Document extraction is temporarily unavailable. Please try again in a few minutes.",
    ErrorCode.LLM_UNAVAILABLE:         "AI extraction is temporarily unavailable. Please try again in a few minutes.",

    ErrorCode.DUPLICATE_UPLOAD:        "This document was just uploaded. The previous result is being returned.",
    ErrorCode.AUTH_REQUIRED:           "Authentication required.",

    ErrorCode.INTERNAL:                "Something went wrong on our side. Please try again.",
}


def client_message(code: ErrorCode) -> str:
    """Return the safe, user-facing message for an ``ErrorCode``.

    Falls back to a generic message if the code is somehow unknown — defensive
    against future codes being added without a CLIENT_MESSAGES entry.
    """
    return CLIENT_MESSAGES.get(code, CLIENT_MESSAGES[ErrorCode.INTERNAL])
