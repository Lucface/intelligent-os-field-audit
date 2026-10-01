#!/usr/bin/env python3
"""Pre-review a Field Audit ledger-entry issue, then post or update one comment.

Code checks the format and looks for leaks. It never accepts, labels or closes
anything: Lucas Cooper-Bey reviews every entry and makes the accept call.

    python3 scripts/check_issue.py --dry-run BODY.md   # print the verdict and comment
    python3 scripts/check_issue.py                     # in Actions: check and comment

Verdicts, strongest first: unsafe_extract, needs_fix, ready_for_review.

source: Dan's ledger entry (issue #3) waited from 2026-09-26 with no check and
no reply. jev-interview 2026-09-30: PASS; code decides format and leaks, and
naming a private person stays with the maintainer.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import re
import sys
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

API = "https://api.github.com"
MARKER = "<!-- ledger-check -->"
BOT = "github-actions[bot]"
MAINTAINER = "Lucas Cooper-Bey"
REVIEW_DAYS = 7
DIM_IDS = ["D%d" % i for i in range(1, 13)]
TAILSCALE = ipaddress.ip_network("100.64.0.0/10")

LOCAL_PATH = re.compile(r"/Users/|/home/|\b[A-Za-z]:\\")
IPV4 = re.compile(r"(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?![\d.])")
TOKEN = re.compile(
    r"\bsk-[A-Za-z0-9_-]{20,}"
    r"|\bgh[pousr]_[A-Za-z0-9]{36,}"
    r"|\bgithub_pat_[A-Za-z0-9_]{22,}"
    r"|\bxox[abprs]-[A-Za-z0-9-]{10,}"
    r"|\bAKIA[0-9A-Z]{16}\b"
    r"|\bAIza[0-9A-Za-z_-]{35}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|(?i:\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*\S{12,})"
)
ROW = re.compile(r"^\|\s*(D\d{1,2})\b[^|]*\|([^|]*)\|(.*)\|\s*$")
DATE = re.compile(r"\*\*Date run:\*\*\s*(\d{4}-\d{2}-\d{2})")
METHOD_FIELD = re.compile(r"\*\*Method version:\*\*\s*(v\d+)\b", re.I)
METHOD_PHRASE = re.compile(r"\bmethod (v\d+)\b", re.I)

HEADS = {
    "unsafe_extract": "Ledger check: unsafe_extract. Something in this issue looks private.",
    "needs_fix": "Ledger check: needs_fix. A few things are missing before review.",
    "ready_for_review": f"Ledger check: ready_for_review. {MAINTAINER} reviews entries within {REVIEW_DAYS} days.",
}


@dataclass
class Result:
    verdict: str
    problems: list = field(default_factory=list)

    def comment(self) -> str:
        lines = [MARKER, f"**{HEADS[self.verdict]}**", ""]
        lines += [f"- {problem}" for problem in self.problems]
        if self.verdict == "unsafe_extract":
            lines += ["", "Edit the issue to remove it, then delete the old version from the issue's edit history "
                          "(the \"edited\" menu on the issue), because GitHub keeps earlier versions visible. "
                          "This comment updates when you save."]
        elif self.verdict == "needs_fix":
            lines += ["", "Edit the issue to add them. This comment updates when you save."]
        lines += ["", "This check reads format and looks for leaks only. It never accepts an entry; the maintainer does."]
        return "\n".join(lines) + "\n"


def _where(number: int, line: str) -> str:
    match = ROW.match(line)
    return f"{match.group(1)} row" if match else f"line {number}"


def leaks(body: str) -> list:
    found = []
    for number, line in enumerate(body.splitlines(), 1):
        kinds = []
        if LOCAL_PATH.search(line):
            kinds.append("a local file path")
        for raw in IPV4.findall(line):
            try:
                address = ipaddress.ip_address(raw)
            except ValueError:
                continue
            kinds.append("a Tailscale address" if address in TAILSCALE else "an IP address")
        if TOKEN.search(line):
            kinds.append("a key or token")
        for kind in dict.fromkeys(kinds):
            found.append(f"{_where(number, line)}: looks like {kind}. Remove it or describe it in words.")
    return found


def format_problems(body: str) -> list:
    problems = []
    if not DATE.search(body):
        problems.append("The date is missing. Add `**Date run:** YYYY-MM-DD`.")
    if not (METHOD_FIELD.search(body) or METHOD_PHRASE.search(body)):
        problems.append("The method version is missing. Add `**Method version:** v1` (v1 is the current method).")
    rows = {}
    for line in body.splitlines():
        match = ROW.match(line)
        if match and match.group(1) in DIM_IDS:
            rows.setdefault(match.group(1), (match.group(2).strip(), match.group(3).strip()))
    for dim in DIM_IDS:
        if dim not in rows:
            problems.append(f"{dim} is missing from the table.")
            continue
        score, receipt = rows[dim]
        if not (score.upper() == "N/A" or (score.isdigit() and 0 <= int(score) <= 10)):
            problems.append(f"{dim} row: the score must be a whole number from 0 to 10, or N/A.")
        if not receipt:
            problems.append(f"{dim} row: the receipt is empty.")
    return problems


def check(body: str) -> Result:
    found = leaks(body)
    if found:
        return Result("unsafe_extract", found)
    problems = format_problems(body)
    if problems:
        return Result("needs_fix", problems)
    return Result("ready_for_review", [])


def _request(method, url, token, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "field-audit-ledger-check",
    })
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read()
    return json.loads(raw) if raw else {}


def post_or_update(repo, number, body, token, request=_request) -> str:
    comments = request("GET", f"{API}/repos/{repo}/issues/{number}/comments?per_page=100", token)
    mine = [c for c in comments if (c.get("user") or {}).get("login") == BOT and str(c.get("body", "")).startswith(MARKER)]
    if mine:
        request("PATCH", f"{API}/repos/{repo}/issues/comments/{mine[0]['id']}", token, {"body": body})
        return "updated"
    request("POST", f"{API}/repos/{repo}/issues/{number}/comments", token, {"body": body})
    return "posted"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Pre-review a ledger-entry issue.")
    parser.add_argument("--dry-run", type=Path, metavar="BODY_FILE", help="check a saved body; post nothing")
    args = parser.parse_args(argv)
    if args.dry_run:
        result = check(args.dry_run.read_text(encoding="utf-8"))
        print(result.verdict)
        print(result.comment(), end="")
        return 0
    repo = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GITHUB_TOKEN"]
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    issue = event.get("issue")
    if issue is None:
        issue = _request("GET", f"{API}/repos/{repo}/issues/{int(os.environ['ISSUE_NUMBER'])}", token)
    result = check(issue.get("body") or "")
    action = post_or_update(repo, issue["number"], result.comment(), token)
    print(f"issue #{issue['number']}: {result.verdict} ({action})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
