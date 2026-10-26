# Decided feedback items

The user asked to resolve these four open feedback items in one unit and chose the recommended option for the two
that needed a decision (2026-10-26).

1. `FB-handoff-refusals-emit-maintenance`
   (specs/2026-10/20261026-feedback-guidance-and-scope/feedback/handoff-refusals-emit-maintenance.md).
   Decision-free defect: refusals the caller can fix must not render as a tool defect. `SPEC_HANDOFF_NOT_READY`
   renders `BLOCKED` (or the mode its documented row names) and `SPEC_HANDOFF_REPLY_INVALID` renders `INPUT_ERROR`,
   matching the `CAP-DLV-proposal-incubation` error table. Check `SPEC_HANDOFF_STALE` against its row too. Also fix
   the stale "current report URI" wording in `HandoffNotReadyError.fix` and the `SPEC_HANDOFF_NOT_READY` row:
   acceptance and handoff take no published report. Targets: `base/errors.py`, `features/delivery/usecases/
   native_handoff.py`, tests, `CAP-DLV-proposal-incubation`.

2. `FB-code-reviewer-probe-deletion`
   (specs/2026-10/20261026-feedback-guidance-and-scope/feedback/code-reviewer-probe-deletion.md).
   Decision: unify with the workers. The code reviewer leaves its throwaway probes in the ignored probe path for
   worktree removal to clean, and writes each review round's probes in its own subdirectory (for example
   `<probe path>/review-NN/`) so a later round never reads an earlier round's probes. `git status --short` stays
   unchanged because the path is ignored. Rejected: keeping reviewer deletion (two rules across roles). Targets: the
   code-reviewer contract, the spec-delegate payload reference where it names the probe path, the
   `CAP-DLV-delivery-workflows` sentence ("deleted before it returns") and the pinned phrase in
   `test_delegation_sandbox_guidance.py`.

3. `FB-plain-handoff-skips-proposal-handoff-policy`
   (specs/2026-10/20261026-living-spec-consistency-sweep/feedback/plain-handoff-skips-proposal-handoff-policy.md).
   Decision: no code change. State in `CAP-DLV-proposal-incubation` (and `CAP-DLV-project-policy` rule 4 if it names
   the readers) that the plain `devkit spec proposal handoff <slug>` in a `dev-<slug>` checkout is the Host-run step
   after the `proposal-handoff` decision and reads no policy itself; `handoff --effort` and
   `accept --mode accept_and_handoff` read the policy. Rejected: a policy check with a new approval flag (the CLI
   does not authenticate the conversational decision, and the composed handoff would check twice).

4. `FB-config-template-reports-unchanged-after-writing`
   (specs/2026-10/20261026-living-spec-consistency-sweep/feedback/config-template-reports-unchanged-after-writing.md).
   Decision-free defect: whenever `devkit config template` changes the file's bytes, its result reports a state
   other than `unchanged` and names what it added, including commented blocks. Reproduce first with a regression
   test. Targets: the config template use case in devkit-dist, its tests, `CAP-DIST-sync-and-transactions`
   (Commented Template) and the reference page if it shows the result.
