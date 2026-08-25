"""CV extraction pipeline.

Public surface:
    ExtractorResult       - typed result envelope (no more dicts in dicts)
    ErrorCode             - canonical error codes for upload failures
    SakrTemplateExtractor - deterministic parser for the Sakr Seafarer
                            Employment Application form (Revision 1.3, May 2022)
    extract               - top-level entry point used by views.py

Design goals:
    1. Deterministic over LLM-by-default. The Sakr form is a fixed template;
       regex + positional parsing beats LLM extraction on speed, cost, and
       reliability.
    2. Typed return value. No `magic` keys like ``validation_error`` leaking
       through the layer boundary.
    3. No global state mutation. ``api_keys_config``-style in-place mutation is
       banned; the LLM fallback (when added) will use an explicit state object.
    4. Each parser is a pure function. Section parsers never call APIs, never
       read settings, never touch the database.
"""

from .base import ExtractorResult
from .exception_codes import ErrorCode, client_message
from .sakr_template import SakrTemplateExtractor, detect_sakr_template

__all__ = [
    "ExtractorResult",
    "ErrorCode",
    "SakrTemplateExtractor",
    "detect_sakr_template",
    "client_message",
]
