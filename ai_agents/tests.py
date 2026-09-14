from django.test import TestCase

from .endpoint_query_engine import RESULTS_SUMMARY_PROMPT
from .endpoint_query_engine import summarize_query_results
from .sql_agent import (
    LIST_COMPANIES_SUMMARY_PROMPT,
    MONTHLY_STATS_PROMPT,
    OPEN_JOBS_SUMMARY_PROMPT,
    COMPANY_SUMMARY_PROMPT,
    PROFILE_SUMMARY_PROMPT,
    SYNTHESIS_PROMPT,
)


_PROMPTS_THAT_FORBID_MARKDOWN = [
    ("LIST_COMPANIES_SUMMARY_PROMPT", LIST_COMPANIES_SUMMARY_PROMPT),
    ("MONTHLY_STATS_PROMPT", MONTHLY_STATS_PROMPT),
    ("OPEN_JOBS_SUMMARY_PROMPT", OPEN_JOBS_SUMMARY_PROMPT),
    ("COMPANY_SUMMARY_PROMPT", COMPANY_SUMMARY_PROMPT),
    ("PROFILE_SUMMARY_PROMPT", PROFILE_SUMMARY_PROMPT),
    ("SYNTHESIS_PROMPT", SYNTHESIS_PROMPT),
    ("RESULTS_SUMMARY_PROMPT", RESULTS_SUMMARY_PROMPT),
]


class SummaryPromptPlainTextRulesTests(TestCase):
    """
    The AI Assistant frontend renders assistant messages as plain text.
    Every user-facing summary prompt must explicitly forbid Markdown syntax
    and instruct the LLM to emit plain text only.
    """

    def test_each_prompt_has_a_plain_text_rule(self):
        for name, prompt in _PROMPTS_THAT_FORBID_MARKDOWN:
            with self.subTest(prompt=name):
                self.assertIn("plain text only", prompt.lower())
                self.assertIn("do not use any markdown syntax", prompt.lower())

    def test_each_prompt_forbids_bold_and_pipe_tables(self):
        for name, prompt in _PROMPTS_THAT_FORBID_MARKDOWN:
            with self.subTest(prompt=name):
                self.assertIn("**bold**", prompt)
                self.assertIn("pipe-tables", prompt)

    def test_results_summary_prompt_format_renders_cleanly(self):
        rendered = RESULTS_SUMMARY_PROMPT.format(
            question="list active companies",
            hint="active=true",
            total=9,
            data="[]",
        )
        # The rendered output contains placeholders but no {{ }} leftovers
        self.assertNotIn("{{", rendered)
        self.assertNotIn("}}", rendered)


class CountOnlyResponseIsPlainTextTests(TestCase):
    """
    summarize_query_results short-circuits for the count_only path.
    That path used to render `**N**` Markdown, breaking the plain-text UI.
    """

    def test_count_only_response_has_no_markdown(self):
        class _DummyModel:
            def invoke(self, *args, **kwargs):
                raise AssertionError(
                    "count_only path must NOT call the LLM"
                )

        out = summarize_query_results(
            "how many companies?",
            {"count_only": True, "total": 9},
            _DummyModel(),
        )
        self.assertNotIn("**", out)
        self.assertNotIn("|", out)
        self.assertIn("9", out)
        self.assertTrue(out.endswith("matching records."))
