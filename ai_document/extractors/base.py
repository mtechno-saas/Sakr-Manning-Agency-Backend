"""Typed result envelope for CV extraction.

The previous endpoint returned a heterogeneous dict whose shape depended on
which code path executed (LLM happy path, LLM failure, validation failure,
LLM returned wrong type, etc.). The view then had to defensively re-shape it
with empty fallbacks for every section, which is exactly how the
``validation_error`` magic key leaked through.

``ExtractorResult`` fixes this:

    * ``data`` is ``None`` on hard failure and a ``dict`` on success.
    * ``extractor`` names which strategy produced the result (for telemetry,
      A/B testing, and trust boundaries).
    * ``confidence`` is a 0.0-1.0 score so the caller can decide whether to
      auto-save or ask the user to review.
    * ``warnings`` are non-fatal issues (e.g. ``"Could not parse Marline Test
      result %"``) that the view may surface to the user but do not block save.
    * ``error`` is an ``ErrorCode`` enum value, NEVER a raw exception string.

The view never has to inspect ``data`` shape — it can use ``result.ok`` to
decide success vs. failure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .exception_codes import ErrorCode


@dataclass
class ExtractorResult:
    """The single return type of every extractor in this package."""

    # The structured CV data. ``None`` on hard failure; ``dict`` on success.
    data: dict[str, Any] | None

    # Which extractor produced this result. Useful for logging and A/B tests.
    # Examples: "sakr_template", "llm", "none".
    extractor: str

    # 0.0 (no confidence) to 1.0 (fully deterministic parser matched all
    # fields). The Sakr template parser returns ~0.95; the LLM fallback
    # returns ~0.6-0.8 depending on completeness.
    confidence: float

    # Non-fatal issues. The view may include these in the response so the
    # user can correct the source document, but they do not block save.
    warnings: list[str] = field(default_factory=list)

    # ``ErrorCode`` on hard failure; ``None`` on success.
    error: ErrorCode | None = None

    @property
    def ok(self) -> bool:
        """True iff extraction succeeded and produced a usable dict."""
        return self.data is not None and self.error is None

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a JSON-safe dict (for the response payload)."""
        return {
            "data": self.data,
            "extractor": self.extractor,
            "confidence": self.confidence,
            "warnings": list(self.warnings),
            "error": self.error.value if self.error else None,
            "ok": self.ok,
        }


def make_failure(
    extractor: str,
    error: ErrorCode,
    *,
    confidence: float = 0.0,
    warnings: list[str] | None = None,
) -> ExtractorResult:
    """Helper: build a failed ``ExtractorResult`` with consistent shape."""
    return ExtractorResult(
        data=None,
        extractor=extractor,
        confidence=confidence,
        warnings=list(warnings or []),
        error=error,
    )


def make_success(
    data: dict[str, Any],
    extractor: str,
    *,
    confidence: float = 0.95,
    warnings: list[str] | None = None,
) -> ExtractorResult:
    """Helper: build a successful ``ExtractorResult`` with consistent shape."""
    return ExtractorResult(
        data=data,
        extractor=extractor,
        confidence=confidence,
        warnings=list(warnings or []),
        error=None,
    )
