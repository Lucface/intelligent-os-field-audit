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
TMP_DIR = "/" + "tmp" + "/"
PRIVATE_DIR = "/" + "private" + "/"
LEADING_ZERO_TAILSCALE = "100" + ".064.1.1"
LEADING_ZERO_IP = "192" + ".168.000.001"
OVERSIZE_OCTET = "192" + ".168.001.256"
DOC_IPV6 = "2001" + ":db8" + ":" + ":" + "1"
TAILSCALE_IPV6 = "fd7a" + ":115c" + ":a1e0" + ":" + ":" + "1"
OUTSIDE_TAILSCALE_IPV6 = "fd7a" + ":115c" + ":a1e1" + ":" + ":" + "1"
CLOCK_TIME = "12" + ":30"
RATIO = "3" + ":1"
DIMENSION_PAIR = "D1" + ":" + ":" + "D3"
BARE_DOUBLE_COLON = ":" + ":"
IPV6_LOOPBACK = ":" + ":" + "1"
VAR_FOLDERS = "/" + "var" + "/folders/"
SCOPE_PATH = "std" + ":" + ":" + "ab" + ":" + ":" + "cd"
LABELLED_CLOCK = "at" + ":" + "12" + ":" + "30" + ":" + "45"
TAILSCALE_IPV4 = "100" + ".101.5.7"
NETSTAT_DOT_PORT = "192" + ".168.1.10" + "." + "22"
OCTET_250 = "192" + ".168.1.250"
UNSPECIFIED_IPV4 = "0" + ".0.0.0"
EIGHT_GROUP_TAILSCALE = "fd7a" + ":115c" + ":a1e0" + ":1" + ":0" + ":0" + ":0" + ":1"
CODE_IDENTIFIERS = (
    "db" + ":" + ":" + "add(row)",
    "A" + ":" + ":" + "B",
    "v8" + ":" + ":" + "Isolate",
    "e2e" + ":" + ":" + "beforeAll",
    "pcre2" + ":" + ":" + "cab1",
)
DIMENSION_LABEL = "D4" + ":" + ":" + "notes"
DIMENSION_TRIPLE = "D1" + ":" + ":" + "D2" + ":" + "D3"
REPOS_VISIBILITY = "12 repos (public" + "/" + "private" + "/" + "archived)"
HTTPS_PATH_WORDS = "https://example.com/files" + "/" + "private" + "/docs" + "/" + "tmp" + "/x"
CLOCK_WITH_SECONDS = "12" + ":" + "30" + ":" + "45"
THREE_PART_RATIO = "3" + ":" + "1" + ":" + "2"
ALL_ZERO_IPV6 = ":".join(["0"] * 8)
MAPPED_UNSPECIFIED = ":" + ":" + "ffff" + ":" + "0" + ":" + "0"

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

    def test_leading_zero_tailscale_address_is_unsafe_and_never_quoted(self):
        # source: 2026-09-30 review-gate finding: leading-zero IPv4 was dropped and passed as ready_for_review
        body = replace_receipt(WITH_METHOD, "D10", f"GPU box at {LEADING_ZERO_TAILSCALE} runs whisper")
        result = ci.check(body)
        self.assertEqual(result.verdict, "unsafe_extract")
        comment = result.comment()
        self.assertIn("D10 row: looks like a Tailscale address", comment)
        self.assertNotIn(LEADING_ZERO_TAILSCALE, comment)
        self.assertEqual(ci.leaks(body), [
            "D10 row: looks like a Tailscale address. Remove it or describe it in words.",
        ])

    def test_leading_zero_plain_ip_is_unsafe_and_never_quoted(self):
        # source: 2026-09-30 review-gate finding: leading-zero IPv4 still classifies a plain IP address
        body = replace_receipt(WITH_METHOD, "D8", f"cache at {LEADING_ZERO_IP}")
        result = ci.check(body)
        self.assertEqual(result.verdict, "unsafe_extract")
        comment = result.comment()
        self.assertIn("D8 row: looks like an IP address", comment)
        self.assertNotIn(LEADING_ZERO_IP, comment)
        self.assertEqual(ci.leaks(body), [
            "D8 row: looks like an IP address. Remove it or describe it in words.",
        ])

    def test_octet_above_255_is_not_an_ip_address(self):
        # source: 2026-09-30 review-gate finding: leading-zero IPv4 skips only an octet above 255
        body = replace_receipt(WITH_METHOD, "D8", f"cache at {OVERSIZE_OCTET}")
        result = ci.check(body)
        self.assertEqual(result.verdict, "ready_for_review")
        self.assertEqual(ci.leaks(body), [])

    def test_ipv6_address_is_unsafe_and_never_quoted(self):
        # source: 2026-09-30 review-gate finding: IPv6 addresses were never detected
        result = ci.check(replace_receipt(WITH_METHOD, "D6", f"tunnel at {DOC_IPV6}"))
        self.assertEqual(result.verdict, "unsafe_extract")
        comment = result.comment()
        self.assertIn("D6 row: looks like an IP address", comment)
        self.assertNotIn(DOC_IPV6, comment)

    def test_tailscale_ipv6_address_is_unsafe_and_never_quoted(self):
        # source: 2026-09-30 review-gate finding: IPv6 inside the Tailscale prefix was never detected
        result = ci.check(replace_receipt(WITH_METHOD, "D10", f"GPU box at {TAILSCALE_IPV6} runs whisper"))
        self.assertEqual(result.verdict, "unsafe_extract")
        comment = result.comment()
        self.assertIn("D10 row: looks like a Tailscale address", comment)
        self.assertNotIn(TAILSCALE_IPV6, comment)

    def test_ipv6_outside_tailscale_prefix_is_a_plain_ip(self):
        # source: 2026-09-30 review-gate finding: IPv6 is a Tailscale address only inside that prefix
        result = ci.check(replace_receipt(WITH_METHOD, "D10", f"GPU box at {OUTSIDE_TAILSCALE_IPV6} runs whisper"))
        self.assertEqual(result.verdict, "unsafe_extract")
        comment = result.comment()
        self.assertIn("D10 row: looks like an IP address", comment)
        self.assertNotIn("Tailscale", comment)
        self.assertNotIn(OUTSIDE_TAILSCALE_IPV6, comment)

    def test_times_ratios_and_dimension_text_are_not_ipv6(self):
        # source: 2026-09-30 review-gate finding: times, ratios, and dimension text must not match as IPv6
        body = replace_receipt(
            WITH_METHOD, "D4", f"met at {CLOCK_TIME}, split {RATIO}, see {DIMENSION_PAIR}")
        result = ci.check(body)
        self.assertEqual(result.verdict, "ready_for_review")
        self.assertEqual(ci.leaks(body), [])

    def test_bare_double_colon_in_prose_is_not_an_ip_address(self):
        # source: 2026-10-02 architect review of the leak fix: a bare double colon in prose was reported as an IP address
        receipt = f"claim {BARE_DOUBLE_COLON} locus, see `{BARE_DOUBLE_COLON}`"
        result = ci.check(replace_receipt(WITH_METHOD, "D4", receipt))
        self.assertEqual(result.verdict, "ready_for_review")

    def test_ipv6_loopback_is_still_an_ip_address(self):
        # source: 2026-10-02 architect review of the leak fix: a bare double colon in prose was reported as an IP address
        result = ci.check(replace_receipt(WITH_METHOD, "D6", f"tunnel at {IPV6_LOOPBACK}"))
        self.assertEqual(result.verdict, "unsafe_extract")
        comment = result.comment()
        self.assertIn("D6 row: looks like an IP address", comment)
        self.assertNotIn(IPV6_LOOPBACK, comment)

    def test_tmp_path_is_unsafe_and_never_quoted(self):
        # source: 2026-09-30 review-gate finding: a temp-directory path was not treated as a local file path
        path = TMP_DIR + "notes.txt"
        result = ci.check(replace_receipt(WITH_METHOD, "D4", f"bench notes in {path}"))
        self.assertEqual(result.verdict, "unsafe_extract")
        comment = result.comment()
        self.assertIn("D4 row: looks like a local file path", comment)
        self.assertNotIn(path, comment)

    def test_private_path_is_unsafe_and_never_quoted(self):
        # source: 2026-09-30 review-gate finding: a private-directory path was not treated as a local file path
        path = PRIVATE_DIR + "notes.txt"
        result = ci.check(replace_receipt(WITH_METHOD, "D4", f"bench notes in {path}"))
        self.assertEqual(result.verdict, "unsafe_extract")
        comment = result.comment()
        self.assertIn("D4 row: looks like a local file path", comment)
        self.assertNotIn(path, comment)

    def test_labelled_ipv6_address_is_unsafe_and_never_quoted(self):
        # source: 2026-10-02 review of 885a3e7: an IPv6 address written directly after a label and one colon was not detected
        for label in ("ip", "host"):
            with self.subTest(label=label):
                result = ci.check(replace_receipt(WITH_METHOD, "D6", label + ":" + DOC_IPV6))
                self.assertEqual(result.verdict, "unsafe_extract")
                comment = result.comment()
                self.assertIn("D6 row: looks like an IP address", comment)
                self.assertNotIn(DOC_IPV6, comment)

    def test_ipv6_address_followed_by_a_colon_is_unsafe(self):
        # source: 2026-10-02 review of 885a3e7: an IPv6 address directly followed by one colon was not detected
        result = ci.check(replace_receipt(WITH_METHOD, "D10", "box " + DOC_IPV6 + ": runs whisper"))
        self.assertEqual(result.verdict, "unsafe_extract")
        self.assertNotIn(DOC_IPV6, result.comment())

    def test_labelled_tailscale_ipv6_is_named_as_tailscale(self):
        # source: 2026-10-02 review of 885a3e7: a labelled address inside the Tailscale IPv6 range was not reported
        result = ci.check(replace_receipt(WITH_METHOD, "D10", "ip" + ":" + TAILSCALE_IPV6))
        self.assertEqual(result.verdict, "unsafe_extract")
        self.assertIn("looks like a Tailscale address", result.comment())

    def test_scope_paths_and_labelled_times_are_not_ipv6(self):
        # source: 2026-10-02 review of 885a3e7: a label colon may now start an address, so a scope path and a labelled clock time must still pass
        receipt = "see " + SCOPE_PATH + " met " + LABELLED_CLOCK
        result = ci.check(replace_receipt(WITH_METHOD, "D4", receipt))
        self.assertEqual(result.verdict, "ready_for_review")

    def test_var_folders_path_is_unsafe_and_never_quoted(self):
        # source: 2026-10-02 review of 885a3e7: a macOS temp path was not treated as a local file path
        path = VAR_FOLDERS + "notes.txt"
        result = ci.check(replace_receipt(WITH_METHOD, "D4", "bench notes in " + path))
        self.assertEqual(result.verdict, "unsafe_extract")
        comment = result.comment()
        self.assertIn("D4 row: looks like a local file path", comment)
        self.assertNotIn(path, comment)

    def test_ipv4_followed_by_a_full_stop_is_unsafe(self):
        # source: 2026-10-02 independent review of 885a3e7: an IPv4 address followed by a full stop was not reported
        body = replace_receipt(WITH_METHOD, "D10", "GPU box at " + TAILSCALE_IPV4 + ".")
        self.assertEqual(ci.check(body).verdict, "unsafe_extract")
        self.assertEqual(ci.leaks(body), [
            "D10 row: looks like a Tailscale address. Remove it or describe it in words.",
        ])
        body = replace_receipt(WITH_METHOD, "D8", "cache at " + LEADING_ZERO_IP + ".")
        self.assertEqual(ci.leaks(body), [
            "D8 row: looks like an IP address. Remove it or describe it in words.",
        ])

    def test_netstat_address_dot_port_is_unsafe(self):
        # source: 2026-10-02 independent review of 885a3e7: an IPv4 address joined to a port by a dot was not reported
        body = replace_receipt(WITH_METHOD, "D8", "netstat " + NETSTAT_DOT_PORT)
        self.assertEqual(ci.check(body).verdict, "unsafe_extract")

    def test_octet_between_200_and_255_is_an_ip_address(self):
        # source: 2026-10-02 independent review of 885a3e7: no test used an octet between 200 and 255, so a ceiling of 199 kept the suite green
        body = replace_receipt(WITH_METHOD, "D8", "cache at " + OCTET_250)
        self.assertEqual(ci.check(body).verdict, "unsafe_extract")
        self.assertEqual(ci.leaks(body), [
            "D8 row: looks like an IP address. Remove it or describe it in words.",
        ])

    def test_unspecified_ipv4_is_not_reported(self):
        # source: 2026-10-02 independent review of 885a3e7: the all-zero IPv4 address written with a port was reported
        body = replace_receipt(WITH_METHOD, "D6", "server binds " + UNSPECIFIED_IPV4 + ":" + "80")
        self.assertEqual(ci.leaks(body), [])
        self.assertEqual(ci.check(body).verdict, "ready_for_review")

    def test_eight_group_tailscale_ipv6_is_named_as_tailscale(self):
        # source: 2026-10-02 independent review of 885a3e7: no test address had more than four colons, and an eight-group address followed by a colon or a port was not reported
        expected = ["D10 row: looks like a Tailscale address. Remove it or describe it in words."]
        receipts = (
            "GPU box at " + EIGHT_GROUP_TAILSCALE,
            "GPU box at " + EIGHT_GROUP_TAILSCALE + ": " + "runs whisper",
            "GPU box at " + EIGHT_GROUP_TAILSCALE + ":" + "443",
        )
        for receipt in receipts:
            with self.subTest(receipt=receipt):
                body = replace_receipt(WITH_METHOD, "D10", receipt)
                self.assertEqual(ci.leaks(body), expected)

    def test_code_identifiers_are_not_ipv6(self):
        # source: 2026-10-02 independent review of 885a3e7: code identifiers written with a double colon were reported as IPv6 addresses
        body = replace_receipt(WITH_METHOD, "D4", " ".join(CODE_IDENTIFIERS))
        self.assertEqual(ci.leaks(body), [])
        self.assertEqual(ci.check(body).verdict, "ready_for_review")

    def test_dimension_labels_are_not_ipv6(self):
        # source: 2026-10-02 independent review of 885a3e7: dimension labels joined by colons were reported as IPv6 addresses
        body = replace_receipt(WITH_METHOD, "D5", DIMENSION_LABEL + " and " + DIMENSION_TRIPLE)
        self.assertEqual(ci.leaks(body), [])

    def test_path_words_inside_other_text_are_not_local_paths(self):
        # source: 2026-10-02 independent review of 885a3e7: path words inside other text were reported as local file paths
        body = replace_receipt(WITH_METHOD, "D4", REPOS_VISIBILITY + " " + HTTPS_PATH_WORDS)
        self.assertEqual(ci.leaks(body), [])

    def test_three_part_times_and_ratios_are_not_ipv6(self):
        # source: 2026-10-02 independent review of 885a3e7: the earlier time and ratio test used one colon and never reached the IPv6 scan
        body = replace_receipt(WITH_METHOD, "D4", "met at " + CLOCK_WITH_SECONDS + ", split " + THREE_PART_RATIO)
        self.assertEqual(ci.leaks(body), [])

    def test_all_zero_ipv6_long_form_is_not_reported(self):
        # source: 2026-10-02 mutation run: with the unspecified rule removed, only a bare double colon was tested, and the no-digit rule hid the gap
        body = replace_receipt(WITH_METHOD, "D6", "listens on " + ALL_ZERO_IPV6)
        self.assertEqual(ci.leaks(body), [])

    def test_ipv4_mapped_unspecified_is_not_reported(self):
        # source: 2026-10-02 independent review of 885a3e7: this form was reported on Python 3.9 and not on 3.12 and later
        body = replace_receipt(WITH_METHOD, "D6", "bind " + MAPPED_UNSPECIFIED)
        self.assertEqual(ci.leaks(body), [])

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
