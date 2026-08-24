"""
Tests for the Groq model rotation logic in
ai_document.document_to_json._get_active_llm.

We don't hit the network — we inject a fake `langchain_groq` module
into sys.modules with a recording ChatGroq that records which
model names it was asked to instantiate, and we verify the order
+ fallback behaviour matches settings.
"""
import sys
import types
from unittest import mock

from django.test import SimpleTestCase, override_settings

from ai_document import document_to_json


class _RecordingChatGroq:
    """Fake ChatGroq that records every init call. If a model name
    is in ``broken_models``, the init raises (simulating a 404 from
    Groq). Otherwise the call is recorded and a sentinel is returned."""

    broken_models: set = set()
    calls: list = []

    def __init__(self, *args, **kwargs):
        model = kwargs.get("model")
        type(self).calls.append(model)
        if model in type(self).broken_models:
            raise RuntimeError(f"simulated 404 for model {model!r}")


def _install_fake_langchain_groq():
    """Install a fake ``langchain_groq`` module with our recording
    ChatGroq so the code under test can import it. Returns the
    module object (and cleans sys.modules on context exit)."""
    fake = types.ModuleType("langchain_groq")
    fake.ChatGroq = _RecordingChatGroq
    return fake


class GetActiveLlmModelRotationTests(SimpleTestCase):
    """The router tries the configured models in order, and falls
    through to the next one if the previous fails to instantiate."""

    def setUp(self):
        _RecordingChatGroq.broken_models = set()
        _RecordingChatGroq.calls = []
        # Inject a fake langchain_groq into sys.modules so the
        # lazy import inside _get_active_llm finds our recorder.
        self._fake = _install_fake_langchain_groq()
        sys.modules["langchain_groq"] = self._fake

    def tearDown(self):
        sys.modules.pop("langchain_groq", None)

    def test_tries_models_in_order_until_one_works(self):
        # First model is broken (404), second works.
        _RecordingChatGroq.broken_models = {"primary-model"}
        with override_settings(GROQ_MODEL_FALLBACKS=[
            "primary-model",
            "fallback-1",
            "fallback-2",
        ]):
            llm, source = document_to_json._get_active_llm({
                "groq": [{"key": "test-key", "status": "live",
                          "reset_time": None}],
            })
        self.assertIsNotNone(llm)
        self.assertEqual(source["model"], "fallback-1")
        self.assertEqual(source["provider"], "groq")
        # We tried primary (broken) then fallback-1 (worked); the
        # 3rd model is never tried.
        self.assertEqual(_RecordingChatGroq.calls,
                         ["primary-model", "fallback-1"])

    def test_returns_none_when_no_model_initializes(self):
        def fake_chat_groq_always_broken(*args, **kwargs):
            raise RuntimeError("all broken")
        # Override ChatGroq on the fake module to be the always-broken variant.
        self._fake.ChatGroq = mock.MagicMock(side_effect=fake_chat_groq_always_broken)
        with override_settings(GROQ_MODEL_FALLBACKS=["only-one"]):
            llm, source = document_to_json._get_active_llm({
                "groq": [{"key": "test-key", "status": "live",
                          "reset_time": None}],
            })
        self.assertIsNone(llm)
        self.assertIsNone(source)

    def test_does_not_retry_other_keys_when_one_works(self):
        """If the first key works, we don't iterate to the second
        key for the same model (no point burning keys)."""
        with override_settings(GROQ_MODEL_FALLBACKS=["primary-model"]):
            document_to_json._get_active_llm({
                "groq": [
                    {"key": "k1", "status": "live", "reset_time": None},
                    {"key": "k2", "status": "live", "reset_time": None},
                ],
            })
        self.assertEqual(_RecordingChatGroq.calls, ["primary-model"])

    def test_skips_exhausted_keys(self):
        """Keys with status=exhausted are not tried."""
        with override_settings(GROQ_MODEL_FALLBACKS=["primary-model"]):
            document_to_json._get_active_llm({
                "groq": [
                    {"key": "k1", "status": "exhausted",
                     "reset_time": 9999999999},
                    {"key": "k2", "status": "live", "reset_time": None},
                ],
            })
        # Only the second key was tried (the exhausted one was
        # skipped).
        self.assertEqual(_RecordingChatGroq.calls, ["primary-model"])

