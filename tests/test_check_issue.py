"""Tests for scripts/check_issue.py. Run: python3 -m unittest discover -s tests -v"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_issue as ci  # noqa: E402

# Built at runtime so this public repo's history holds no home-directory path, even a made-up one
# (the pre-push leak guard refuses them, 2026-09-30).
MAC_HOME = "/" + "Users" + "/"
LINUX_HOME = "/" + "home" + "/"

FIXTURE = (ROOT / "tests" / "fixtures" / "issue-001-as-posted.md").read_text(encoding="utf-8")
WITH_METHOD = FIXTURE.replace("**Model used:**", "**Method version:** v1\n**Model used:**", 1)


def replace_receipt(body: str, dim: str, text: str) -> str:
    out = []
    for line in body.splitlines():
        m = ci.ROW.match(line)
        if m and m.group(1) == dim:
            line = f"| {dim} replaced | {m.group(2).strip()} | {text} |"
        out.append(line)
    return "\n".join(out) + "\n"


class CheckIssue(unittest.TestCase):
    def test_issue_1_as_posted_needs_only_the_method_version(self):
        # source: issue #1 predates the method-version field (FIELD-AUDIT-JOURNEY-SPEC, Proof)
        result = ci.check(FIXTURE)
        self.assertEqual(result.verdict, "needs_fix")
        self.assertEqual(len(result.problems), 1)
        self.assertIn("method version", result.problems[0])

    def test_issue_1_with_method_version_is_ready(self):
        self.assertEqual(ci.check(WITH_METHOD).verdict, "ready_for_review")

    def test_method_named_in_the_date_line_counts(self):
        # source: issue #3 (2026-09-26) states "method v1" inside its date line
        body = FIXTURE.replace("(Join Protocol phase T0, doors closed)", "(Join Protocol phase T0, doors closed; method v1)")
        self.assertEqual(ci.check(body).verdict, "ready_for_review")

    def test_local_path_is_unsafe_and_never_quoted(self):
        result = ci.check(replace_receipt(WITH_METHOD, "D4", f"bench notes in {MAC_HOME}someone/vault/bench.md"))
        self.assertEqual(result.verdict, "unsafe_extract")
        comment = result.comment()
        self.assertIn("D4 row: looks like a local file path", comment)
        self.assertNotIn(MAC_HOME, comment)
        self.assertNotIn("someone", comment)

    def test_tailscale_address_is_unsafe_and_never_quoted(self):
        result = ci.check(replace_receipt(WITH_METHOD, "D10", "GPU box at 100.101.5.7 runs whisper"))
        self.assertEqual(result.verdict, "unsafe_extract")
        self.assertIn("D10 row: looks like a Tailscale address", result.comment())
        self.assertNotIn("100.101", result.comment())

    def test_token_is_unsafe_and_never_quoted(self):
        token = "ghp_" + "a1B2" * 9
        result = ci.check(replace_receipt(WITH_METHOD, "D9", f"deploy key {token}"))
        self.assertEqual(result.verdict, "unsafe_extract")
        self.assertIn("D9 row: looks like a key or token", result.comment())
        self.assertNotIn(token, result.comment())

    def test_unsafe_outranks_needs_fix(self):
        self.assertEqual(ci.check(replace_receipt(FIXTURE, "D4", f"see {LINUX_HOME}someone/x")).verdict, "unsafe_extract")

    def test_missing_dimension_bad_score_and_empty_receipt(self):
        body = "\n".join(line for line in WITH_METHOD.splitlines() if not line.startswith("| D7 "))
        body = replace_receipt(body, "D3", "")
        body = body.replace("| D2 Autonomy | 9 |", "| D2 Autonomy | 11 |")
        result = ci.check(body)
        self.assertEqual(result.verdict, "needs_fix")
        self.assertIn("D7 is missing from the table.", result.problems)
        self.assertIn("D2 row: the score must be a whole number from 0 to 10, or N/A.", result.problems)
        self.assertIn("D3 row: the receipt is empty.", result.problems)

    def test_na_score_is_allowed(self):
        body = WITH_METHOD.replace("| D12 Ecosystem | 2 |", "| D12 Ecosystem | N/A |")
        self.assertEqual(ci.check(body).verdict, "ready_for_review")

    def test_decimals_and_versions_are_not_ip_addresses(self):
        # issues #1 and #3 are full of numbers like 0.914 and 0.60 to 0.80
        result = ci.check(replace_receipt(WITH_METHOD, "D4", "hit@5 0.60 to 0.80, p < 0.001, v1.2.3"))
        self.assertEqual(result.verdict, "ready_for_review")

    def test_windows_line_endings_get_the_same_verdict(self):
        # review focus 1: the GitHub web editor posts \r\n
        self.assertEqual(ci.check(WITH_METHOD.replace("\n", "\r\n")).verdict, "ready_for_review")

    def test_score_written_as_nine_out_of_ten_needs_fix(self):
        # review focus 2: a newcomer's AI often writes 9/10
        result = ci.check(WITH_METHOD.replace("| D2 Autonomy | 9 |", "| D2 Autonomy | 9/10 |"))
        self.assertEqual(result.verdict, "needs_fix")
        self.assertIn("D2 row: the score must be a whole number from 0 to 10, or N/A.", result.problems)

    def test_only_the_bots_own_comment_is_ever_updated(self):
        # review focus 3: anyone can paste the marker into their own comment
        calls = []

        def someone_else_has_the_marker(method, url, token, payload=None):
            calls.append((method, url))
            if method == "GET":
                return [
                    {"id": 11, "user": {"login": "someone"}, "body": ci.MARKER + " copied"},
                    {"id": 12, "user": {"login": "github-actions[bot]"}, "body": "unrelated"},
                ]
            return {}

        self.assertEqual(ci.post_or_update("o/r", 3, "body", "t", request=someone_else_has_the_marker), "posted")
        self.assertEqual(calls[-1][0], "POST")

        def bot_has_the_marker(method, url, token, payload=None):
            calls.append((method, url))
            if method == "GET":
                return [{"id": 12, "user": {"login": "github-actions[bot]"}, "body": ci.MARKER + "\nold"}]
            return {}

        self.assertEqual(ci.post_or_update("o/r", 3, "body", "t", request=bot_has_the_marker), "updated")
        self.assertTrue(calls[-1][1].endswith("/issues/comments/12"))


if __name__ == "__main__":
    unittest.main()
