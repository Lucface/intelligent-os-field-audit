#!/usr/bin/env python3
"""Render LEDGER.md from ledger.json, the one record of accepted entries.

    python3 scripts/render_ledger.py            # write LEDGER.md
    python3 scripts/render_ledger.py --check    # exit 1 if LEDGER.md differs

Standard library only. ledger.json is append-only: a correction is a new row in
an entry's `corrections`, never an edit to the entry.

source: 2026-09-30, the site's copy of the ledger stopped at the 07-22 entry
while LEDGER.md already held 09-25. Two hand-kept copies drifted; one source
and a generated view cannot.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUBMIT = "https://github.com/Lucface/intelligent-os-field-audit/issues/new?template=scorecard.md"
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PRIVATE = re.compile(r"/(?:Users|home|private|tmp)/|[A-Za-z]:\\|[\x00-\x08\x0b\x0c\x0e-\x1f]")
DIM_IDS = ["D%d" % i for i in range(1, 13)]


class LedgerError(ValueError):
    pass


def _text(value, where):
    if not isinstance(value, str) or not value.strip():
        raise LedgerError(f"{where}: expected text")
    if PRIVATE.search(value):
        raise LedgerError(f"{where}: private path or control character")
    return value


def _https(value, where):
    if not isinstance(value, str) or not value.startswith("https://") or any(c.isspace() for c in value):
        raise LedgerError(f"{where}: expected an https URL")
    return value


def _int(value, where, low, high):
    if not isinstance(value, int) or isinstance(value, bool) or not low <= value <= high:
        raise LedgerError(f"{where}: expected an integer from {low} to {high}")
    return value


def validate(data: dict) -> dict:
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise LedgerError("schema: expected 1")
    if not DATE.match(str(data.get("updated", ""))):
        raise LedgerError("updated: expected YYYY-MM-DD")
    _text(data.get("maintainer"), "maintainer")
    _int(data.get("review_days"), "review_days", 1, 60)
    versions = set()
    for i, method in enumerate(data.get("methods") or []):
        where = f"methods[{i}]"
        if not re.match(r"^v\d+$", str(method.get("version", ""))):
            raise LedgerError(f"{where}.version: expected vN")
        if method.get("status") not in ("current", "draft", "retired"):
            raise LedgerError(f"{where}.status: expected current, draft or retired")
        if "discussion" in method:
            _https(method["discussion"], f"{where}.discussion")
        versions.add(method["version"])
    if not versions:
        raise LedgerError("methods: expected at least one")
    dims = data.get("dimensions") or []
    if [d.get("id") for d in dims] != DIM_IDS:
        raise LedgerError("dimensions: expected D1 to D12 in order")
    for i, dim in enumerate(dims):
        _text(dim.get("short"), f"dimensions[{i}].short")
        _text(dim.get("full"), f"dimensions[{i}].full")
    seen = set()
    for i, entry in enumerate(data.get("entries") or []):
        where = f"entries[{i}]"
        n = _int(entry.get("n"), f"{where}.n", 1, 100000)
        if n in seen:
            raise LedgerError(f"{where}.n: duplicate entry number {n}")
        seen.add(n)
        if not DATE.match(str(entry.get("date", ""))):
            raise LedgerError(f"{where}.date: expected YYYY-MM-DD")
        for key in ("builder", "system", "shape"):
            _text(entry.get(key), f"{where}.{key}")
        if entry.get("method") not in versions:
            raise LedgerError(f"{where}.method: not in methods")
        if entry.get("phase") not in (None, "T0", "T1"):
            raise LedgerError(f"{where}.phase: expected T0, T1 or null")
        scores = entry.get("scores")
        if not isinstance(scores, list) or len(scores) != 12:
            raise LedgerError(f"{where}.scores: expected 12 scores")
        for j, score in enumerate(scores):
            if score is not None:
                _int(score, f"{where}.scores[{j}]", 0, 10)
        if not re.match(r"^\d{1,2}/12$", str(entry.get("leads", ""))):
            raise LedgerError(f"{where}.leads: expected N/12")
        _https(entry.get("receipts"), f"{where}.receipts")
        if entry.get("issue") is not None:
            _https(entry["issue"], f"{where}.issue")
        ghost = entry.get("ghost")
        if ghost is not None:
            _text(ghost.get("note"), f"{where}.ghost.note")
            if ghost.get("against") is not None:
                _int(ghost["against"], f"{where}.ghost.against", 1, 100000)
        if entry.get("note") is not None:
            _text(entry["note"], f"{where}.note")
        for k, correction in enumerate(entry.get("corrections") or []):
            cw = f"{where}.corrections[{k}]"
            if not isinstance(correction.get("at"), str) or not DATE.match(correction["at"][:10]):
                raise LedgerError(f"{cw}.at: expected an ISO timestamp")
            if correction.get("dimension") not in (None, *DIM_IDS):
                raise LedgerError(f"{cw}.dimension: expected D1 to D12 or null")
            if not isinstance(correction.get("score_changed"), bool):
                raise LedgerError(f"{cw}.score_changed: expected true or false")
            _text(correction.get("note"), f"{cw}.note")
    if not seen:
        raise LedgerError("entries: expected at least one")
    return data


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _method_line(methods: list) -> str:
    bits = []
    for method in methods:
        if method["status"] == "current":
            details = []
            if method.get("frozen"):
                details.append(f"frozen {method['frozen']}")
            if method.get("tag"):
                details.append(f"tag `{method['tag']}`")
            bits.append(f"{method['version']} is current" + (f" ({', '.join(details)})" if details else ""))
        elif method["status"] == "draft":
            bit = f"{method['version']} is a draft open for input"
            if method.get("discussion"):
                bit += f" at {method['discussion']}"
            bits.append(bit)
    return "; ".join(bits)


def render(data: dict) -> str:
    validate(data)
    entries = sorted(data["entries"], key=lambda e: e["n"], reverse=True)
    lines = [
        "<!-- Generated from ledger.json by scripts/render_ledger.py. Edit ledger.json, never this file. -->",
        "# The Ledger",
        "",
        "The running record of harness shapes. Not a leaderboard: nobody wins a scorecard. "
        "Every entry is one builder's Intelligent OS, audited with [`prompt.md`](./prompt.md), receipts first. "
        f"Post yours as an [issue]({SUBMIT}). {data['maintainer']} reviews it within {data['review_days']} days, "
        "and an accepted entry is appended to [`ledger.json`](./ledger.json). "
        "Entries are never rewritten; a correction is added under its entry.",
        "",
        f"Method: {_method_line(data['methods'])}. Changes between versions: "
        f"[`METHOD-CHANGELOG.md`](./METHOD-CHANGELOG.md). Updated {data['updated']}.",
        "",
        "| # | Date | Builder | System | Method | " + " | ".join(DIM_IDS) + " | Leads | Shape, in one line |",
        "|---|------|---------|--------|--------|" + "|".join("----" for _ in DIM_IDS) + "|-------|--------------------|",
    ]
    for e in entries:
        method = e["method"] + (f" {e['phase']}" if e.get("phase") else "")
        scores = ["N/A" if s is None else str(s) for s in e["scores"]]
        row = [f"{e['n']:03d}", e["date"], _cell(e["builder"]), _cell(e["system"]), method, *scores, e["leads"], _cell(e["shape"])]
        lines.append("| " + " | ".join(row) + " |")
    for e in entries:
        lines += ["", f"## Entry {e['n']:03d}", "", f"- Receipts: {e['receipts']}"]
        if e.get("issue"):
            lines.append(f"- Issue: {e['issue']}")
        ghost = e.get("ghost")
        if ghost:
            against = f" (against entry {ghost['against']:03d})" if ghost.get("against") else ""
            lines.append(f"- Ghost vs now{against}: {ghost['note']}")
        if e.get("note"):
            lines.append(f"- Note: {e['note']}")
        for c in e.get("corrections") or []:
            dim = f", {c['dimension']}" if c.get("dimension") else ""
            changed = "score changed" if c["score_changed"] else "score unchanged"
            lines.append(f"- Correction ({c['at']}{dim}, {changed}): {c['note']}")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Render LEDGER.md from ledger.json.")
    parser.add_argument("--check", action="store_true", help="exit 1 if LEDGER.md differs from the render")
    parser.add_argument("--ledger", type=Path, default=ROOT / "ledger.json")
    parser.add_argument("--out", type=Path, default=ROOT / "LEDGER.md")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.ledger.read_text(encoding="utf-8"))
        text = render(data)
    except Exception as exc:  # any malformed ledger is exit 2, never a traceback that reads as drift
        print(f"ledger.json is invalid: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != text:
            print("LEDGER.md is out of date or hand-edited. Edit ledger.json, then run: python3 scripts/render_ledger.py", file=sys.stderr)
            return 1
        print("LEDGER.md matches ledger.json")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out.name}: {len(data['entries'])} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
