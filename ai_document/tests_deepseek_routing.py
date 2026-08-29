"""
Tests for the DeepSeek routing logic in
ai_document.document_to_json._get_active_llm.

We don't hit the network — we inject a fake `langchain_openai` module
into sys.modules with a recording ChatOpenAI that records which API
key + base_url + model it was asked to instantiate, and we verify
the order + fallback behaviour matches settings.
"""
import os
import sys
import types
from unittest import mock

from django.test import SimpleTestCase, override_settings

from ai_document import document_to_json


class _RecordingChatOpenAI:
    """Fake ChatOpenAI that records every init call. If a key is in
    ``broken_keys``, the init raises (simulating a 401 from DeepSeek).
    Otherwise the call is recorded and a sentinel is returned."""

    broken_keys: set = set()
    calls: list = []

    def __init__(self, *args, **kwargs):
        # ChatOpenAI accepts both `api_key` and (older) `openai_api_key`.
        # Some versions of langchain-openai consume one and rewrite to the
        # other, so we check both when matching against broken_keys.
        api_key = kwargs.get("api_key") or kwargs.get("openai_api_key")
        type(self).calls.append({
            "model": kwargs.get("model"),
            "api_key": api_key,
            "base_url": kwargs.get("base_url"),
        })
        if api_key in type(self).broken_keys:
            raise RuntimeError(f"simulated 401 for key {api_key!r}")


def _install_fake_langchain_openai():
    """Install a fake ``langchain_openai`` module with our recording
    ChatOpenAI so the code under test can import it. Returns the
    module object (and cleans sys.modules on context exit)."""
    fake = types.ModuleType("langchain_openai")
    fake.ChatOpenAI = _RecordingChatOpenAI
    return fake


class GetActiveLlmDeepSeekTests(SimpleTestCase):
    """The DeepSeek branch of _get_active_llm. DeepSeek is the
    primary cloud LLM after Ollama (or after Ollama is skipped)."""

    def setUp(self):
        _RecordingChatOpenAI.broken_keys = set()
        _RecordingChatOpenAI.calls = []
        # Inject a fake langchain_openai into sys.modules so the
        # lazy import inside _get_active_llm finds our recorder.
        self._fake = _install_fake_langchain_openai()
        sys.modules["langchain_openai"] = self._fake

    def tearDown(self):
        sys.modules.pop("langchain_openai", None)

    def test_deepseek_wins_when_ollama_disabled_and_key_in_env(self):
        """OLLAMA_HOST empty (or ollama disabled) + DEEPSEEK_API_KEY
        in env → router returns a DeepSeek LLM with the right model
        and base_url."""
        with override_settings(
            OLLAMA_ENABLED=False,
            DEEPSEEK_API_KEY="sk-env-test",
            DEEPSEEK_MODEL="deepseek-chat",
            DEEPSEEK_BASE_URL="https://api.deepseek.com",
        ):
            llm, source = document_to_json._get_active_llm({})

        self.assertIsNotNone(llm)
        self.assertEqual(source["provider"], "deepseek")
        self.assertEqual(source["model"], "deepseek-chat")
        self.assertEqual(source["key"], "sk-env-test")
        # ChatOpenAI was constructed with the right kwargs.
        self.assertEqual(_RecordingChatOpenAI.calls, [{
            "model": "deepseek-chat",
            "api_key": "sk-env-test",
            "base_url": "https://api.deepseek.com",
        }])

    def test_deepseek_wins_when_key_in_api_keys_config(self):
        """No env key, but api_keys_config["deepseek"] has a key →
        router uses it. This is the path used by the view when the
        request supplies deepseek_api_key as a form field."""
        with override_settings(
            OLLAMA_ENABLED=False,
            DEEPSEEK_API_KEY="",  # empty env
        ):
            llm, source = document_to_json._get_active_llm({
                "deepseek": [
                    {"key": "sk-config-test", "status": "live",
                     "reset_time": None},
                ],
            })

        self.assertIsNotNone(llm)
        self.assertEqual(source["provider"], "deepseek")
        self.assertEqual(source["key"], "sk-config-test")

    def test_deepseek_skipped_when_deepseek_disabled_in_config(self):
        """``api_keys_config["deepseek_disabled"] = True`` → router
        skips DeepSeek entirely, falls through to Gemini (or None if
        no Gemini key either)."""
        with override_settings(
            OLLAMA_ENABLED=False,
            DEEPSEEK_API_KEY="sk-test",
        ):
            llm, source = document_to_json._get_active_llm(
                {"deepseek_disabled": True},
            )

        self.assertIsNone(llm)
        self.assertIsNone(source)
        # ChatOpenAI was NEVER instantiated.
        self.assertEqual(_RecordingChatOpenAI.calls, [])

    def test_deepseek_skipped_when_settings_deepseek_disabled(self):
        """``DEEPSEEK_ENABLED = False`` (env override) → router never
        tries DeepSeek even if a key is present."""
        with override_settings(
            OLLAMA_ENABLED=False,
            DEEPSEEK_ENABLED=False,
            DEEPSEEK_API_KEY="sk-test",
        ):
            llm, source = document_to_json._get_active_llm({})

        self.assertIsNone(llm)
        self.assertIsNone(source)
        self.assertEqual(_RecordingChatOpenAI.calls, [])

    def test_deepseek_skips_exhausted_keys(self):
        """Keys with status=exhausted are not tried (they're skipped,
        not retried — operator must rotate the key to recover)."""
        with override_settings(
            OLLAMA_ENABLED=False,
            DEEPSEEK_API_KEY="sk-test",
        ):
            document_to_json._get_active_llm({
                "deepseek": [
                    {"key": "sk-exhausted", "status": "exhausted",
                     "reset_time": None},
                ],
            })

        # The exhausted key was skipped, no ChatOpenAI call happened.
        self.assertEqual(_RecordingChatOpenAI.calls, [])

    def test_deepseek_init_failure_falls_through(self):
        """ChatOpenAI raises (e.g. base_url wrong, dep not installed)
        → router logs and returns (None, None) so caller can try the
        next provider (Gemini)."""
        _RecordingChatOpenAI.broken_keys = {"sk-broken"}
        with override_settings(
            OLLAMA_ENABLED=False,
            DEEPSEEK_API_KEY="sk-broken",
        ):
            llm, source = document_to_json._get_active_llm({})

        self.assertIsNone(llm)
        self.assertIsNone(source)
        # We did try (and it failed).
        self.assertEqual(len(_RecordingChatOpenAI.calls), 1)


class DeepSeekSettingsSanityTests(SimpleTestCase):
    """The DEEPSEEK_* settings in settings.py must be sensible.
    If they're empty/missing, the LLM path silently fails."""

    @classmethod
    def setUpClass(cls):
        from django.conf import settings as django_settings
        cls.deepseek_enabled = getattr(django_settings, "DEEPSEEK_ENABLED", False)
        cls.deepseek_model = getattr(django_settings, "DEEPSEEK_MODEL", "")
        cls.deepseek_base_url = getattr(django_settings, "DEEPSEEK_BASE_URL", "")

    def test_deepseek_settings_defined(self):
        self.assertTrue(
            hasattr(__import__("django.conf", fromlist=["settings"]),
                    "settings"),
        )
        # DEEPSEEK_MODEL and DEEPSEEK_BASE_URL must be set (not blank).
        self.assertTrue(
            self.deepseek_model,
            "DEEPSEEK_MODEL is empty — set it in settings.py or via env",
        )
        self.assertTrue(
            self.deepseek_base_url,
            "DEEPSEEK_BASE_URL is empty — set it in settings.py or via env",
        )

    def test_deepseek_base_url_points_to_deepseek(self):
        """The base URL should be api.deepseek.com (or a private
        proxy of it). Anything else is probably a typo."""
        self.assertIn(
            "deepseek.com", self.deepseek_base_url,
            f"DEEPSEEK_BASE_URL={self.deepseek_base_url!r} doesn't look "
            f"like DeepSeek's API endpoint. Expected something like "
            f"'https://api.deepseek.com'.",
        )

    def test_deepseek_model_looks_valid(self):
        """DeepSeek's supported models: deepseek-chat, deepseek-reasoner,
        deepseek-coder. Anything else is probably a typo."""
        valid = {"deepseek-chat", "deepseek-reasoner", "deepseek-coder"}
        self.assertIn(
            self.deepseek_model, valid,
            f"DEEPSEEK_MODEL={self.deepseek_model!r} is not a known "
            f"DeepSeek model. Choose from: {sorted(valid)}.",
        )
