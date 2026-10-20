---
id: PLAN-draft-direct-acceptance
spec: SPEC-draft-direct-acceptance
---

# Technical Plan: `SPEC-draft-direct-acceptance` Direct acceptance of drafts that need no Planning

## 1. Constitution & Invariant Review

Conforms to `ADR-direct-acceptance-command-and-handoff-guard`, `ADR-eligibility-for-direct-acceptance` and
`ADR-session-reclassification-of-a-queued-draft`; the lowering rule's `MUST`-level statements gain the exception
the last one decides. Layering holds: the new module lives in `devkit_spec.proposals` and uses only `devkit.core`,
`devkit.advisory` and `devkit.workflow` (`record_answer`, `Workspace`, `load_envelopes`), as `handoff.py` already
does. The library never prints; the CLI writes through `devkit.core.cli`. The `sdd-proposal` stage schema is
unchanged; only its `direction-handoff` comment and body change. No new dependency.

## 2. Architecture Overview & Impact

- **Impacted Components**:
  - `packages/devkit-spec/src/devkit_spec/proposals/accept.py` (new): `accept_proposal` and `AcceptResult`.
  - `packages/devkit-spec/src/devkit_spec/branches.py`: `base_checkout_problem`, the positive base-checkout check.
  - `packages/devkit-spec/src/devkit_spec/proposals/handoff.py`: the guard for bound bundles; the carried note keeps
    the proposal's note after `PROP-<slug>`.
  - `packages/devkit-spec/src/devkit_spec/errors.py`: `ProposalAcceptRefusedError`, `ProposalNotEligibleError`,
    `ProposalGateNotOpenError`, `ProposalAcceptanceUnrecordedError`; `ProposalNotApprovedError` names the command;
    `ProposalWrongWorktreeError` covers the Planning form.
  - `packages/devkit-spec/src/devkit_spec/cli/proposals.py`: `devkit spec proposal accept`.
  - `packages/devkit-spec/src/devkit_spec/proposals/scaffold.py` and `bundle/templates/proposal.md`: the lifecycle
    line.
  - Bundle guidance: `bundle/workflows/sdd-proposal.md`, `bundle/AGENTS.md`, `bundle/skills/spec/SKILL.md` and its
    references (`backlog.md`, `classification.md`, `effort.md`, `feedback-retirement.md`, `worktree.md`),
    `bundle/skills/spec-next/` (`SKILL.md`, `references/next-work.md`, `references/workflow-signals.md`),
    `bundle/skills/spec-orchestrate/SKILL.md`, `bundle/seed/docs/proposals/README.md`.
  - Living Spec (reconcile): `CAP-DLV-proposal-incubation`, `CAP-DLV-delivery-workflows`, `CAP-HARN-command-mount`,
    `CAP-HARN-agent-guidance`, `US-incubate-and-hand-off-a-proposal`, the devkit-spec README and its development
    reference when they list the proposal commands.
- **New Dependencies**: none.

## 3. Component & Interface Design

```python
FORMS = ("planning", "direct", "repair")

@dataclass(frozen=True)
class AcceptResult:
    proposal: str          # PROP-<slug>
    path: str              # proposal.md, workspace-relative
    form: str              # planning | direct | repair
    status: str            # accepted (written or already), or the current status under check
    checked: bool          # --check: nothing written
    decision: str | None   # the gate:plan-accept record, workspace-relative; None under check
    pending: tuple[str, ...] = ()  # gate:plan-intent under --check when not recorded

def accept_proposal(root: Path, slug: str, *, by: str, note: str = "", direct: bool = False,
                    check: bool = False) -> AcceptResult: ...
```

Order (each refusal before any write):

1. Arguments: `by == "user"` (the CLI restricts the choice; the library raises `ArgumentError`), a non-blank
   `note` with `direct` (`ArgumentError`, target `--note`).
2. The proposal: a bundle bound to a workflow (`SPEC_PROPOSAL_ACCEPT_REFUSED` for a single file or unbound bundle),
   readable frontmatter (`SPEC_PROPOSAL_INVALID`).
3. The form from status and `direct`: `reviewing` without `direct` is `planning`; `draft` with `direct` is `direct`;
   `accepted` with `direct` and no effective `gate:plan-accept` is `repair`. Every other combination, `rejected`
   included, is `SPEC_PROPOSAL_ACCEPT_REFUSED` with a fix naming the right form.
4. Planning form: the checkout is on `plan-<slug>` (`SPEC_PROPOSAL_WRONG_WORKTREE`; outside Git not checked).
   Direct and repair: every condition is collected (blocking: `needs_decompose`, `supersedes`, a Planning branch,
   `task_kind`, the envelope hold, the base checkout, and for the repair a `worker` envelope; pending: no accepted
   `gate:plan-intent`, by the handoff's carry rule `_proposal_gates`). Any blocking one, or a pending one outside
   `--check`, is `SPEC_PROPOSAL_NOT_ELIGIBLE` with one detail per condition (`blocking: ...`, `pending: ...`).
5. `--check` returns here.
6. Write `status: accepted` (not for a repair; the regex keeps a trailing comment), then `record_answer(...,
   "gate:plan-accept", "accept", note=..., by=by, lint=False)`. Any `AdvisoryError` there: evaluate the unit,
   restore the original bytes, raise `SPEC_PROPOSAL_GATE_NOT_OPEN` with the unmet checks, the hold reasons and the
   engine's code in its details.

`base_checkout_problem(root) -> str | None`: `None` outside Git; otherwise a reason when the checkout is a linked
worktree, on a detached `HEAD`, on a `plan-*` or `dev-*` branch, or, when `refs/remotes/origin/HEAD` resolves, on a
branch other than its target.

Handoff: after the status check, a bundle whose `workflow` is set and whose `_proposal_gates` lacks an accepted
`gate:plan-accept` raises `SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED` (`INTERACTION`) before any write. `_record_gates`
writes the note `PROP-<slug>: <note>` when the proposal's record has a note, else `PROP-<slug>`.

CLI: `devkit spec proposal accept SLUG --by user [--note TEXT] [--direct] [--check]`; text
`[ACCEPTED: PROP-<slug> form= path= status=accepted decision=]` or
`[ACCEPT_CHECK: PROP-<slug> form= path= eligible=yes pending=<requests>|-]`; JSON `AcceptResult.to_dict()`.

## 4. Error Handling & Edge Cases

- A refusal leaves nothing behind; the status is restored byte-for-byte when the engine refuses after the write.
- The engine decides the sweep: `collect-feedback` off by policy, or passed, lets `gate:plan-accept` open; the command
  never writes a feedback envelope.
- The repair applies every direct check except the status and refuses a proposal with a `worker` envelope (a Planning
  ran); with an effective `gate:plan-accept` there is nothing to repair.
- A fetched `plan-<slug>` counts, as for `devkit spec proposal check`; devkit fetches nothing.

## 5. Verification & Test Plan

- `packages/devkit-spec/tests/proposals/test_proposal_accept.py`: AC-01 to AC-08 against a temporary Git repository
  with a test `sdd-proposal` definition carrying the real gates and the `collect-feedback` stage.
- `test_proposal_handoff_records.py`: AC-09 (guard; unbound and single-file still hand off) and AC-10 (note).
- `test_proposal_handoff.py` or the CLI tests: AC-11 (the `[FIX]` text).
- A guidance test (AC-12) over the bundled files and the scaffold, kept to the stated contract phrases.
- `test_documented_codes.py` keeps every new code documented in `CAP-DLV-proposal-incubation`.
- Commands: `just lint devkit-spec`, `just check devkit-spec`, `just test-affected`, the commit gate
  (`devkit rules check --staged`).
