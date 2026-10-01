"""Tests for scripts/render_ledger.py. Run: python3 -m unittest discover -s tests -v"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import render_ledger as rl  # noqa: E402

# Built at runtime so this public repo's history holds no home-directory path, even a made-up one
# (the pre-push leak guard refuses them, 2026-09-30).
MAC_HOME = "/" + "Users" + "/"

SCRIPT = str(ROOT / "scripts" / "render_ledger.py")


def load() -> dict:
    return json.loads((ROOT / "ledger.json").read_text(encoding="utf-8"))


class RenderLedger(unittest.TestCase):
    def test_committed_ledger_md_is_the_render_of_ledger_json(self):
        # source: 2026-09-30, the site's hand-typed ledger stopped at 07-22 while LEDGER.md held 09-25
        self.assertEqual(rl.render(load()), (ROOT / "LEDGER.md").read_text(encoding="utf-8"))

    def test_check_goes_red_when_ledger_md_is_hand_edited(self):
        # mutation proof for the CI gate: a hand edit must fail --check
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "LEDGER.md"
            shutil.copy(ROOT / "LEDGER.md", out)
            ok = subprocess.run([sys.executable, SCRIPT, "--check", "--out", str(out)], capture_output=True, text=True)
            self.assertEqual(ok.returncode, 0, ok.stderr)
            out.write_text(out.read_text(encoding="utf-8").replace("| 7/12 |", "| 9/12 |"), encoding="utf-8")
            bad = subprocess.run([sys.executable, SCRIPT, "--check", "--out", str(out)], capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1)
            self.assertIn("hand-edited", bad.stderr)

    def test_newest_entry_renders_first(self):
        text = rl.render(load())
        self.assertLess(text.index("| 002 |"), text.index("| 001 |"))

    def test_correction_is_added_and_the_entry_is_not_rewritten(self):
        text = rl.render(load())
        self.assertIn("a finance snapshot never produced", text)
        self.assertIn("Correction (2026-09-25T16:40:00-07:00, D11, score unchanged)", text)

    def test_rejects_eleven_scores(self):
        data = load()
        data["entries"][0]["scores"] = data["entries"][0]["scores"][:11]
        with self.assertRaisesRegex(rl.LedgerError, r"entries\[0\]\.scores"):
            rl.render(data)

    def test_rejects_score_above_ten(self):
        data = load()
        data["entries"][0]["scores"][3] = 11
        with self.assertRaisesRegex(rl.LedgerError, r"scores\[3\]"):
            rl.render(data)

    def test_rejects_a_score_typed_as_text(self):
        # review focus 5: a hand-accepted entry with "6" instead of 6
        data = load()
        data["entries"][0]["scores"][0] = "6"
        with self.assertRaisesRegex(rl.LedgerError, r"scores\[0\]"):
            rl.render(data)

    def test_rejects_local_path_in_shape(self):
        data = load()
        data["entries"][1]["shape"] = f"notes live in {MAC_HOME}someone/vault"
        with self.assertRaisesRegex(rl.LedgerError, "private path"):
            rl.render(data)

    def test_rejects_unknown_method(self):
        data = load()
        data["entries"][0]["method"] = "v9"
        with self.assertRaisesRegex(rl.LedgerError, "not in methods"):
            rl.render(data)

    def test_pipe_in_text_cannot_break_the_table(self):
        data = load()
        data["entries"][0]["shape"] = "left | right"
        self.assertIn("left \\| right", rl.render(data))


if __name__ == "__main__":
    unittest.main()
