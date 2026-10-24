# Author self-review of PROP-automatic-scope-collection

This is a source-backed review of a Backlog draft, not an independent challenger review or Planning acceptance.
No runtime implementation or cloud experiment was performed. Findings marked open block direction acceptance;
folded findings have corresponding design constraints but still require implementation verification.

## Findings

| Finding | Failure condition and source evidence | Disposition |
| --- | --- | --- |
| P1: Standalone cloud participation is absent | `features/scope/usecases/flow.py:233-242` skips `auto_register` outside linked worktrees. A cloud checkout with no token cannot refresh through the existing updater. | Open: Q2 requires a concrete eligibility/ownership design and a tokenless standalone test. Local collection does not imply cross-cloud visibility. |
| P1: Creation snapshots do not prove dispatch readiness | `bundle/skills/spec-orchestrate/SKILL.md.jinja:14` schedules using `scope query`; its prepare/run loop does not establish that a worker has written `tasks.md` and called `next` before the Host dispatches another task. Creation skeletons contain no completed boundaries. | Open: Q1 requires execution traces through first dispatch, continuation, reconciliation and worker acceptance. Do not claim continuous freshness or add a compensating manual update command. |
| P1: A generic evaluation hook has unintended write effects | `workflow/usecases/operations.py:41-57` exposes evaluation; `:77` evaluates during workflow handoff, and `delivery/usecases/integration.py:228` evaluates during integration readiness. A callback inside `Workspace.evaluate_unit` would mutate state in unrelated callers. | Folded: section 3.1 limits the trigger to the explicit next application operation and AC-03 requires negative call-count tests. The optional extension contract remains Q3. |
| P1: Existing update can retarget a registration | `features/scope/usecases/flow.py:413-421` constructs an update with the supplied `spec_dir`. Invoking next for another spec must not transfer attribution to it. | Folded: Q5 and AC-04 require same-unit identity validation before mutation and safe automatic handling of mismatches without changing attribution. |
| P2: Repeated next calls create churn if they reuse update unchanged | `features/scope/usecases/flow.py:400-421` generates a request ID and calls registry update for each non-replayed request; `:433-453` journals outcomes. | Folded: compare semantic inputs first; unchanged scope produces no update revision or journal entry. Performance and the finite budget remain Q4/AC-06. |
| P2: Silent failure leaves stale or absent evidence | Registry mutations need permissions and locks. A successful primary command does not prove publication; initial registration may also fail. | Accepted tradeoff: no automatic-path notices, result fields or exit-code changes, even under `--strict`. Preserve actual stored timestamps/revisions and expose diagnostics only under `-v`. Scope evidence cannot certify independence. Verify all three triggers under AC-05. |
| P2: Reusing the explicit updater leaks its failure protocol | The explicit updater returns ACK/errors/notices and journals outcomes. Passing those through creation or next would add agent-facing failure output. | Folded: isolate the automatic path, including provider loading and logging, from the maintenance command's result protocol. Explicit hidden update retains its behavior. AC-05 checks text/JSON and strict/non-strict output. |
| P2: Failure after publication is not a failed write | A journal append can fail after a scope record was atomically published. Reverting the record or reporting the old timestamp misrepresents committed state. | Folded: retain a published snapshot on journal failure; pre-publication failures preserve the previous snapshot. Do not add failure-journal writes or immediate retries. |
| P2: Silent first-registration failure can prevent later refresh | A later next call may have no token, or encounter partial registration state. Blindly calling the existing updater cannot recover initial participation. | Open under Q2/Q5: demonstrate safe automatic participation/recovery at the next ordinary eligible call without permission escalation, manual instructions, stealing ownership or retargeting another unit. |
| P2: Hidden Click command may remain in generated discovery | Click hiding addresses ordinary help only; this review did not demonstrate every generated command discovery path. | Open: AC-07 requires discovery inspection and explicit maintenance invocation tests. Expand boundaries before modifying any additional shared discovery owner. |
| P2: An accepted decision explicitly retains skill refresh | ADR-worktrees-branches-and-scope, section 4, assigns updates to skills and limits normal registry participation to linked worktrees. | Folded: proposal retirement criteria require a PADR replacing the refresh decision and, if chosen, the linked-only participation decision. Do not rewrite the accepted ADR in place. |

## Corrections incorporated before this review record

- Both direct creation and handoff already compose automatic initial registration. See
  `features/delivery/usecases/specs.py:54-58` and `features/delivery/usecases/handoff.py:53-57`.
  The proposal treats those as existing paths to retain and test, rather than missing features.
- The design no longer adds envelope or worker-inspect triggers. Only the three requested CLI operations collect.
- Query/history/compare stay read-only; the current source checkout is the only collection source.
- Automatic collection failures at creation, handoff and next are silent by default. This includes `--strict`;
  primary-operation errors and explicit maintenance commands retain their behavior. Only verbose diagnostics
  expose collector failures. The primary result never asserts collection freshness.
- The next ordinary eligible call attempts collection again. There is no immediate retry, agent recovery request
  or automatic permission escalation. A finite separate deadline bounds the remaining latency cost.
- OTel, hooks and remote registry transport remain outside the proposal. They do not resolve local trigger timing
  or ownership by themselves.

## Review judgment

The three-trigger direction is a reviewable hypothesis, not yet a demonstrated sufficient collection schedule.
Keep the proposal draft. Planning should first test dispatch timing and tokenless standalone ownership, then
finalize the extension and verify silent failure isolation, including initial registration recovery. If the timing
trace requires another trigger, bring that scope change back for a direction decision rather than embedding another agent instruction.

## Verification scope

This task validates document governance, intent records and the final diff. Runtime acceptance checks AC-01
through AC-08 belong to Planning experiments and Development; none are claimed as passed by this document.
Source paths above are relative to their owning packages: `features/` under `devkit_spec`, `workflow/` under
`devkit_agt/features`, and `bundle/` under `devkit_spec/bundles/spec`.
