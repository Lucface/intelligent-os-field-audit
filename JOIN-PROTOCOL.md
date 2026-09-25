# Join Protocol: benchmark two harnesses before and after they share

**Status:** v1 of the protocol, 2026-09-25. Companion to [`prompt.md`](./prompt.md) (the audit) and [`LEDGER.md`](./LEDGER.md) (the record).

Two builders are about to open their systems to each other: read each other's machines, adopt each other's patterns, maybe share compute. The claim "our systems got stronger by joining" is only worth making if it was measured before the door opened. This protocol makes the before-and-after a benchmark instead of a story.

## The four phases

### T0: individual baseline, doors closed
Each builder runs [`prompt.md`](./prompt.md) on their own machine **before pulling anything from the other**. No reading the other's repo, no adopting a hook, no shared corpus. Same prompt, same model tier (Fable/Opus at max effort), same reference field.

Deliverable per builder: a scorecard issue using the ledger template, plus the rendered dossier attached or linked. The ledger appends it as `T0` for that builder.

### P: pre-registration, before any adoption
Each builder writes down, per dimension, the score they **predict** after adopting the other's patterns, and names the specific artifact that would move it (the hook, the lease, the bench, the job). This is posted as a comment on the builder's own T0 issue before the first adoption lands.

Why: a post-merge score with no prediction on record can always be narrated as a win. A prediction that missed is the interesting result.

Format, one line per dimension you expect to move:

```
D7  7 -> 8   canaries for the deny-class hooks, two-sided, run at pre-commit
D3  9 -> 9   no change expected; PreCompact tripwire is hygiene, not provenance
```

Dimensions not listed are predicted unchanged.

### M: the merge window, bounded
Adopt what you said you would, in a fixed window. Default: **seven days** from the later of the two T0 dates. Extend only by saying so on the issue before the window closes. Everything adopted gets a one-line note on the issue as it lands (date, artifact, which prediction it serves).

Reading each other's machine is allowed in M, not before. So is cross-grading (below).

### T1: individual re-audit, same prompt
Each builder re-runs the identical prompt on their own machine at the end of the window. Post it as a new ledger issue titled `T1`. The ledger appends both rows and a delta line: per-dimension change, predicted vs actual, and the leads count against the frozen field.

## Rules that differ from a first audit

1. **The reference field stays frozen** at the 2026-07-22 rows for G-Brain, OpenClaw and Hermes. Only the builder's own row moves between T0 and T1. Re-verifying rivals is a separate exercise and would contaminate the delta.
2. **Drops are allowed and must be stated.** Method rule 5 (never silently lower a score) was written for same-day re-grades. Across weeks or months a score may fall. Say what decayed: a bench that stopped running, a job that went dead, a receipt that no longer exists. A T1 that only goes up is suspect.
3. **Measured dimensions stay measured on your own harness.** D4 and D7 numbers come from each builder's own goldens and fixtures. Cross-harness numbers count only when both systems ran the identical golden set, and then they are reported as a head-to-head line, not as a score.
4. **Adopted is not the same as scored.** A pattern copied but not exercised (no canary fired, no job ran, no ledger row) is "staged" and moves nothing. The receipt rule from the audit applies unchanged.
5. **Cross-grading is encouraged in the merge window.** Once doors are open, the other builder's model reads your T0 dossier and your machine read-only and may contest any score with a receipt. A contested score is recorded as `score (contested: other score, reason)` on the T1 issue. Neither side edits the other's row.
6. **N/A stays N/A.** Joining does not make an out-of-scope dimension in scope unless the builder decides it does, on the record.

## What the ledger records for a join

For each builder: the T0 row, the prediction comment, the T1 row. Beneath the table, one "join delta" paragraph per builder: dimensions moved, predicted vs actual, what was adopted, what was staged and did not count, what dropped and why. Two builders joining produce four rows and two paragraphs. Never rewritten; a correction is a new line.

## Why bother

The before-and-after is the only evidence that "joining" did anything a solo builder could not have done that week. If the T1 rows beat the predictions, the delta is the pitch for the next builder who joins. If they miss, the miss tells you which patterns did not transfer, which is worth more than the pitch.
