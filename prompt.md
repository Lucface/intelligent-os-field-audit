# Intelligent-OS Field Audit v1 — the prompt

**Method v1, frozen 2026-07-22 (tag `method-v1`).** Every entry on the ledger says which method version scored it; a pair's T0 and T1 always share one version. Proposed changes live in [`METHOD-CHANGELOG.md`](./METHOD-CHANGELOG.md) and are adopted only at a fresh T0.

Paste everything below into Claude Code at your system root.

```
You are running the Intelligent-OS Field Audit v1 (method of 2026-07-22) on THIS machine.

An "Intelligent OS" is the whole operating layer a person builds around their AI tooling: memory, retrieval, skills, agents, scheduled autonomy, evals, security rails, business integration. Your job: audit the one on this machine, receipts first, and score it against the reference field below. Work at maximum effort. Do not ask the user anything; work from the disk and state assumptions inline.

RULES (non-negotiable)
1. Receipts before scores. Inventory by actually looking: count skills/commands/agents (list their directories), scheduled jobs (crontab -l; launchd or systemd user units), hooks, memory/notes files, vector collections, eval harnesses and their result ledgers. Run read-only commands freely; invent nothing. Anything you cannot verify is written "unverified" and scores as absent.
2. Measured beats claimed. A benchmark number in a ledger outranks an architecture that "should" work. If a dimension has zero measurements, the receipt must say so.
3. N/A is never 0. If a dimension is out of scope BY DESIGN (and you can point to where that was decided), grade it N/A and exclude it from lead counts.
4. No flattery. The gaps are the product. Classify every trailing dimension as CHOSEN (deliberate, cite the decision) or EARNED (real gap; name the smallest artifact that would close it).
5. Zero-regression honesty. If you re-grade later the same day, never silently lower a score; state what changed.

THE 12 DIMENSIONS (score 0-10)
D1  Ingress + voice — channels a human can reach it through; live voice loop. (2 one CLI · 5 CLI + one chat channel · 8 multi-channel + mobile · 10 many channels + wake word + live voice)
D2  Autonomy + scheduling — does useful work happen with nobody in the chair, and does dead work get loud? (2 manual · 5 a few crons · 8 dozens of jobs + failure detection · 10 self-healing fleet with heartbeats)
D3  Memory truth + provenance — can it PROVE where a fact came from; does history survive updates? (2 chat logs · 5 curated notes · 8 append-only + source IDs · 10 hashed lineage on every derived value)
D4  Retrieval, measured — hybrid search quality AND whether anyone measured it. Hard cap at 6 if zero benchmark numbers exist, regardless of architecture.
D5  Skill library quality × breadth — packaged capability, and how it is kept trustworthy (linting, curation, install gates).
D6  Self-improvement loop — does it get better on its own, and is that safe? Ungated autonomous self-modification also caps D9 at 5.
D7  Evals + dispatch measurement — is "does the right capability fire, and is the output good" measured, or vibes? (0-4 vibes · 5-7 deterministic fixtures on a schedule · 8-10 plus a semantic judge and regression history)
D8  Multi-agent orchestration — fan-out, pipelines, cross-model adjudication, quarantine tiers.
D9  Security architecture — injection defense, blast-radius control, secrets handling, supply chain. Score the architecture, not the absence of incidents.
D10 Compute sovereignty — local models, own hardware, no single vendor able to turn it off.
D11 Institution + business integration — finance, CRM, legal, client delivery, approval-gated publishing.
D12 Ecosystem + momentum — who else improves it while the operator sleeps. (n=1 by design is a legitimate CHOSEN 2.)

REFERENCE FIELD (as sourced 2026-07-22; D1..D12 in order; null = N/A; re-verify anything that matters to you)
{
 "gbrain":      {"scores":[null,8,7,9,6,8,9,6,6,2,3,7],  "note":"Garry Tan's memory/eval layer: hybrid retrieval w/ published benchmarks (BrainBench), routing-eval + resolvability audits, hosted-API only"},
 "openclaw":    {"scores":[10,8,4,6,8,8,3,8,3,8,4,10],   "note":"biggest ecosystem (384K stars, 52K skills) + best ingress; monthly CVE cadence and a poisoned-registry incident"},
 "hermes":      {"scores":[9,7,3,5,9,9,4,8,5,8,5,9],     "note":"~20 channels + full local voice, autonomous skill Curator; zero memory provenance"},
 "lucface_now": {"scores":[5,9,9,9,9,8,7,9,9,9,10,2],    "note":"the author's one-person system, post-execution 2026-07-22: dispatch evals 0.914 weekly, retrieval hit@5 0.76 weekly, beat a live gbrain install 0.90-0.80 on identical goldens; leads/co-leads 8 of 12"}
}

DO, IN ORDER
1. Inventory sweep (read-only). Enumerate and count the primitives above. Note the 3 most surprising findings.
2. Score all 12 dimensions with a one-line receipt each. The receipt is the evidence itself, not a justification.
3. Comparison table: your row against the reference field. Mark lead / co-lead / trail per dimension; count leads (N/A dims excluded).
4. Verdict in three honest sentences. Then classify every trailing dimension CHOSEN vs EARNED.
5. Ranked moves: the 3 smallest artifacts that would most move the EARNED gaps. Steal proven shapes: a routing-fixtures file scored weekly (does the right capability fire), a golden-set retrieval bench (hit@5 over 20+ questions with known answers), a nightly propose-only librarian over your backlogs. Size each S/M/L.
6. Render a single-file dark-theme HTML dossier (inline CSS, zero external requests, robots noindex): a scorecard section with one bar row per runner per dimension and the receipt beside it, the comparison table, the verdict, the ranked moves. Save it and open it.
7. Ghost mechanic (optional, recommended): if the operator executes a move today, re-run scoring and show GHOST (before) vs NOW (after) rows for the changed dimensions.

Print the scorecard table and verdict in the terminal as well, not only the file.
Method + reference dossier: https://lucface.github.io/intelligent-os-field-audit/ — post your scorecard as a GitHub issue there and it joins the ledger (LEDGER.md), the running record of harness shapes.

```

## Re-running the audit (T0/T1 of the Join Protocol)

If this is a re-run of a system already on the ledger, paste the block above unchanged and add these lines at the end of it, inside the same paste:

```
RE-RUN RULES (Join Protocol, see JOIN-PROTOCOL.md)
A. This is phase <T0|T1> for builder <handle>. Score only THIS machine. The reference field above stays frozen at its 2026-07-22 values; do not re-verify rivals.
B. Load the builder's previous ledger row as GHOST. For every dimension print GHOST -> NOW, and a drop is allowed if the receipt says what decayed. Never silently lower; always explain.
C. If a prediction comment exists for this builder, print predicted vs actual per dimension and name each miss.
D. Anything adopted from another builder counts only if it has a receipt of its own (a fired canary, a ledger row, a job outcome). Otherwise list it as STAGED and score it as absent.
```
