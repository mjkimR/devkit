---
reconcile_id: REC-proposal-scaffold-and-handoff-pointers
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
    resolution: modified
  - file: docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md
    resolution: modified
---

# Reconciliation: `SPEC-proposal-scaffold-and-handoff-pointers`

## Contract comparison

`CAP-DLV-proposal-planning` 4.1 now states that `new` writes only `proposal.md` (and `target-docs.md` with
`--with-target-docs`) and names the command that creates each directory on demand; `CreateProposalUseCase.execute`
in `usecases/scaffold.py` creates the bundle directory only, `padr` keeps its `mkdir(parents=True, exist_ok=True)`,
and devkit's record writers create `decisions/` and `envelopes/` themselves (AC-01, AC-02; `test_proposal_scaffold.py`
asserts the layout after `new` and after `padr`).

4.5 step 4 replaces the sentence "handoff edits no ADR a `supersedes` names" with the pointer contract: one
"Superseded in part by `ADR-<new>`: <clause>" line per `supersedes` entry that resolves to one ADR whose status is
not `superseded`, below the first H1 (after the frontmatter without one), in promotion order, never when a visible
line already names the promoted ADR by ID or alias, with the PADR `summary` (else `title`) as the clause, no
`superseded`/`superseded_by` written, unresolved and non-ADR entries left to `RULE-document-reference`. The
implementation in `usecases/handoff.py` (`_plan_pointers`, `_insert_pointer`, `_clause`, `_pointer_names`) does
exactly that against the same regex, `canonical` resolution and status test `RULE-decision-supersession` uses
(AC-03 to AC-06; `test_proposal_handoff.py`), and the end-to-end test `test_handoff_pointer.py` runs the deployed rule
on the result (AC-08). Rule 5 now names the restored ADRs: `_restore(edited)` runs before `roll_back(written, moved)`,
and the edited file is never recorded as written or moved (AC-07).

4.10 lists `[SUPERSEDED_IN_PART: <adr> path= line= by=]` and the JSON `pointers` key, as
`features/delivery/cli/proposals.py` prints them after `[PROMOTED_ADR: ...]` (AC-03; `test_proposal_cli.py`). The
CLI module docstring and the handoff module docstring restate the same; the spec skill's `references/planning.md`
says `materials/` is created with its first file (AC-09; `test_writing_guidance.py`), and `.devkit/installation.json`
is the regenerated receipt of that bundle text.

`CAP-DOCS-document-model` (Decision supersession) and `RULE-decision-supersession` are unchanged: the handoff
chooses the "below its heading" placement the capability already allows, and the rule's regex is satisfied by the
written line. `SPEC-partial-adr-supersession` AC-03 ("handoff leaves the named ADR unchanged") is completed history
and stays in place; the current contract is this spec's. `UC-plan-and-hand-off-a-proposal` step 8
now names the pointer among the handoff's effects (its Scenario 1 has no partially superseding PADR and stays as it
is; the handoff tests cover that path). No architecture or steering document changes, and no screen was drafted (the
change has no interface a person operates).

## Deferred work and source feedback

Both sources, `FB-proposal-scaffold-dirs-vanish-in-worktree` and `FB-handoff-writes-no-partial-supersession-pointer`,
are `promoted` (terminal): their references stay for traceability and no disposition is written. Nothing in the agreed
scope is deferred; Non-Goal 4 (a `supersedes` naming a PADR promoted in the same handoff) names its reconsideration
trigger and is not concrete work.

## Verification and retained work

`just test devkit-spec` 1648 passed at build; the independent code review (`review-01`, effort medium) reran
`just test-affected --base 5aecaef7` (1651 passed), `just lint-check devkit-spec`, `just check devkit-spec` (pyright 0
errors), `uv run devkit rules check --ci --base 5aecaef7` (errors=0) and `uv run devkit sync --check` (clean), and
found one P3 (a commented `# ` line taken as the heading), fixed with a regression test and closed in `reverify-01`.

## Entrypoints

`devkit spec entrypoints derive` proposed nine new paths for `CAP-DLV-proposal-planning`; applied
`packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py`, the module where reading the handoff
starts (beside the already listed `scaffold.py` and `delivery/cli/proposals.py`). Rejected: the test files, the
package `__init__.py`, the bundle's `references/planning.md` and `.devkit/installation.json`, which are content and
receipt support, not doorways. The capability's `entrypoints` field changed, so it is a `modified` target above.
