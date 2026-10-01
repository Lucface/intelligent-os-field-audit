# intelligent-os-field-audit changelog

## 2026-09-30 (evening) | intelligent-os-field-audit · one source for the ledger, a code check on new entries, safe-sharing steps, and entry 003 accepted | 🚀

**Before → After:** accepted entries were typed by hand into LEDGER.md and again into the Studio site, and the two copies had drifted (the site stopped at entry 001) → `ledger.json` is the one record; `scripts/render_ledger.py` generates LEDGER.md and CI fails if anyone edits LEDGER.md by hand. New ledger issues get an automatic comment from `scripts/check_issue.py`: unsafe_extract (a local path, an IP address, a key), needs_fix (a missing row, score, receipt, date or method version) or ready_for_review. The check never accepts anything; the maintainer does. `prompt.md` gained "Sharing a safe extract", the issue template gained method version, phase and a privacy checkbox, and the README names the maintainer and the 7-day review promise.

**Acceptance:** issue #3 (orionarchitekton, Orion estate harness, T0 2026-09-26) was checked ready_for_review, accepted as entry 003 at 20:29 PT, and appeared on sandiegoaistudio.com/projects#ledger at 20:47 PT, 18 minutes later, with no site commit in between.

**Tested:** 23 unittest tests on Python 3.9 and 3.14; a mutation that makes the check quote a matched line turns exactly the three never-quote tests red; CI green on every push.

**Takeaway:** test fixtures in a public repo build any fake home path at runtime; the pre-push leak guard refuses even a made-up one.

**Ref:** commits 6f4a15d, d5dbd3f, 993d2eb, 5d348cb; issue #3 closed by 5d348cb.

## 2026-09-25 (afternoon) | intelligent-os-field-audit · Re-audit before merging with Dan: Join Protocol written (T0 / prediction / 7-day window / T1), T0 scored 7/12 leads with five stated drops, ledger row 002 + issue #1 + prediction comment, Dan texted twice (session 69bc26f9) | 🎓

**Before → After:** July's dossier was the only baseline and it was two months stale → a public JOIN-PROTOCOL.md (rival rows frozen, drops allowed if stated, predictions on record before any adoption, adopted-but-unexercised counts as staged) and a T0 row scored today from receipts, not architecture.

**Blocked → Unblocked:** six parallel sweep agents finished idle with no report delivered → ListAgents showed them idle, one SendMessage resend each brought all six reports in about a minute. Lead re-verification then overturned two sweep claims: the retrieval series oscillates 0.60–0.80 rather than decaying, and the Telegram bot the sweep called unloaded runs on lux under systemd beside the OpenClaw gateway.

**Takeaway:** an honest re-grade two months later goes down where the receipts decayed (no hash field in any ledger row, an unwatched weekly bench, proposal queues at 338/30 and 131/0, about 8 tests for 66 hooks, a finance pipeline that never emitted a snapshot), and writing the predicted delta before merging is what keeps the post-merge number from being a story: the five adoptions are predicted to move exactly one dimension one point.

**Ref:** repo ~/Developer/lucface/intelligent-os-field-audit (1c1994a protocol, 0ad97d2 T0), https://github.com/Lucface/intelligent-os-field-audit/issues/1, dossier https://lucface.github.io/intelligent-os-field-audit/ledger/002-lucface-t0-2026-09-25.html, memory project_field_audit_join_protocol_t0, state ~/.claude/states/2026-09-25_1610_field-audit-join-protocol-t0.md

