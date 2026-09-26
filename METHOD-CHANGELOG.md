# Method changelog

The bench has versions so a delta is always measured with one ruler. **A pair's T0 and T1 use the same version.** A new version applies only at a fresh T0 for everyone in the cycle; never mid-cycle, however tempting a rubric line looks after your own re-run.

## v1 (frozen 2026-07-22, tag `method-v1`)
The twelve dimensions and rubrics in `prompt.md` as first published. Entries 001 and 002 on the ledger use v1. The 2026-09-25 additions (RE-RUN RULES in the prompt, `JOIN-PROTOCOL.md`) change how a re-run is reported, not what is scored, so they stay inside v1.

## v2 (draft, open for input at issue #2, not adopted)
Proposed from the 2026-09-25 re-run of the author's own system, where the audit was executed as six parallel read-only sweeps plus lead re-verification. Two sweep claims were overturned on re-verification out of roughly sixty receipts, and five scores fell for reasons v1 never named. Each line below is a rubric gap the run exposed.

1. **Absence receipts name their scope.** "Not found" must say where the search ran. A builder's own rules can place a file outside the repo (bank rows never enter git); a sweep that searched only the repo reported a snapshot as never produced. A filtered zero is not an absence.
2. **D2, the three-state law as the 8-band gate.** Every scheduled job reports did_work, no_work or could_not, and a filtered zero is not an absence. Heartbeats older than their own cadence count as dead work. "Self-healing" at 10 means detect-and-repair with a recovery notice, not KeepAlive.
3. **D3, lineage rungs made explicit.** 8 = append-only rows with source ids. 9 = a per-row content hash chained to the previous row, with a verifier that actually runs on a schedule. 10 = an external timestamp authority or an off-machine copy that catches a whole-file rewrite. v1's "hashed lineage on every derived value" was too vague to fail.
4. **D4, measured means watched.** A weekly series nobody alarms on caps at 8. A one-time head-to-head is reported as a line, never as "measured weekly". A store that is empty or mid-rebuild at run time is could_not, not misses.
5. **D7, a rate that cannot move is not evidence.** A constant across N runs on unchanged fixtures says nothing; 8+ needs a semantic judge or a fixture set with a growth ledger. Count write-capable capabilities that have no behaviour fixture and report the ratio.
6. **D6, score the decide side.** Report proposed against decided for every self-improvement queue (levers, eval captures, org proposals). A loop that proposes and never drains is open, whatever the proposer's quality.
7. **D9, score the tests on the gates.** Count deny-class hooks against their two-sided canaries (fires on the violation, silent on the allow path). An enforcement log that has not been written in weeks is a dead gate until proven otherwise. A gate stored as two files in two repos is a drift risk and is named as such.
8. **D1, a channel is live when it reaches the same brain.** A bot on another box running a different model is ingress to that model, not to the system; count it once and say which.
9. **D11, a rail that produced output once is not a rail.** Cadence and the unreviewed tail count. A snapshot marked NOT FINAL with most rows unreviewed scores below a rail that runs monthly and drains.
10. **Candidate D13, cross-session coordination.** Claim leases before touching shared machine state, board injection at session start, collision detection between concurrent sessions. Evidence for the gap: two of the author's own sessions flipped a network profile under each other on 2026-09-25. Evidence it is measurable: the other builder's lockfile lease and 30-minute reconcile timer. Open question for the field: a dimension, or part of D2 and D8.
11. **Candidate D14, human-step capture.** How the system hands the operator the steps only a human can do (a login, a payment, a call) and gets the answer back without chat: action pages with taps, one living list, one-tap decisions. Open question: a dimension, or part of D11.
12. **Method meta.** Record for every audit: wall time, number of receipts, how many were re-verified by the lead, how many sweep claims were overturned. An audit that re-verifies nothing is a sweep, not an audit.
13. **Rival field refresh.** The reference rows (G-Brain, OpenClaw, Hermes) get re-sourced on their own quarterly cadence, never as part of a builder's T0 or T1.
14. **Contested scores.** Formalize cross-grading: after doors open, the other builder's model may contest any score with a receipt; the ledger records `score (contested: other, reason)`. Neither side edits the other's row.

Comments on any line, and any dimension this list still misses, go on issue #2.
