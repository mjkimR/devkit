---
id: PLAN-proposal-scaffold-and-handoff-pointers
spec: SPEC-proposal-scaffold-and-handoff-pointers
---

# Technical Plan: `SPEC-proposal-scaffold-and-handoff-pointers` Lean proposal scaffold and handoff supersession pointers

## 1. Constitution & Invariant Review

- `CAP-DLV-proposal-planning` 4.5 step 4 currently states that handoff edits no ADR a `supersedes` names and that
  the pointer is written in Development. That sentence is a capability contract without an ADR behind it
  (`ADR-decision-ledger` defines the pointer format and `RULE-decision-supersession`, not who writes the line), so
  this spec rewrites it at `living-spec-draft`; no ADR is needed.
- `CAP-DOCS-document-model` (Decision supersession) allows the pointer "below its heading or at the affected
  statement"; the handoff uses the heading placement. `RULE-decision-supersession` is unchanged.
- Rule 5 of `CAP-DLV-proposal-planning` (roll back a failed write) extends to the edited ADR: its original text is
  restored on failure.
- Layering: `handoff.py` already imports `devkit_docs.features.documents` (`DocumentIndex`, `visible_lines`); the
  pointer planner uses the same imports and nothing from `devkit_docs.features.governance`.

## 2. Architecture Overview & Impact

- `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py`: `CreateProposalUseCase.execute`
  creates the bundle directory only (`bundle.mkdir(parents=True)`), no `decisions/` or `materials/`; the module
  docstring and the proposal template's lifecycle comment say the directories are created on demand.
- `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py`: a preflight `_plan_pointers` and a
  write step for the planned pointers inside the existing transaction; `HandoffResult.pointers`; roll-back of edited
  files.
- `packages/devkit-spec/src/devkit_spec/features/delivery/cli/proposals.py`: one `[SUPERSEDED_IN_PART: ...]` line per
  pointer in text output (JSON comes from `to_dict`); the module docstring lists it.
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/planning.md`: `materials/` is
  created with its first file. `uv run devkit sync` regenerates the managed and projected copies.
- `docs/capabilities/delivery/CAP-DLV-proposal-planning.md`: 4.1 bundle layout, 4.5 step 4, 4.10 output and the
  `handoff` output bullet (at `living-spec-draft`).

No new dependency.

## 3. Component & Interface Design

```python
@dataclass(frozen=True)
class SupersessionPointer:        # handoff.py, exported with HandoffResult
    adr: str                      # the target ADR's ID (canonical)
    path: str                     # workspace-relative path of the target ADR
    line: int                     # 1-based line of the pointer in the written file
    by: str                       # the promoted ADR's ID

@dataclass(frozen=True)
class _Pointer:                   # preflight plan, absolute paths
    target: Path
    adr_id: str
    by: str
    original: str                 # text before the handoff, restored on roll-back
    text: str                     # text after this and earlier pointers of the same file
    line: int
```

- `_plan_pointers(root, index, decisions) -> list[_Pointer]`: for each `_Decision` in order, parse the promoted
  text's `supersedes` (a string or a list of strings; anything else is left to the rule), and for each written ID
  that starts with `ADR-`: `index.canonical(written)`; skip when it resolves to nothing, to several documents or to a
  non-`ADR-` document, or when the document's `status` is `superseded`. Read the target text (the in-memory text of an
  earlier pointer to the same file when there is one); skip when a visible line already matches
  ``Superseded in part by `<ID>` `` whose ID canonicalizes to the promoted ADR's ID. Otherwise insert
  `"Superseded in part by `{by}`: {clause}"` after the first visible H1 line following the frontmatter (after the
  frontmatter block when there is none), with a blank line on each side (collapsing an existing blank line), and
  record the pointer with its line number.
- `clause` is the promoted document's `summary` when it is a non-empty string, else its `title`, else the ADR slug;
  whitespace runs collapse to one space, and a period is appended unless the text ends in `.`, `!` or `?`.
- Write step: after the promoted ADRs are written, each pointer target is written with its final text (the last
  `_Pointer` of each file) and recorded in `edited: list[tuple[Path, str]]`. The `except` branch restores every
  edited file before `roll_back(written, moved)`; a restore failure is appended to the `ProposalHandoffError`
  details like any other roll-back problem.
- `HandoffResult.pointers: list[SupersessionPointer]`, serialized as `pointers` in `to_dict`; the CLI prints
  `[SUPERSEDED_IN_PART: <adr> path=<path> line=<n> by=<by>]` after the `[PROMOTED_ADR: ...]` lines and before
  `[DROPPED_RECORD: ...]`.
- The composed handoff (`native_handoff._commit_handoff`) stages with `git add -A`, so the edited ADR is part of the
  transaction without a change there.

## 5. Error Handling & Edge Cases

- Two promoted PADRs superseding the same ADR: two lines, in decision order, each checked for presence separately.
- A target named through an alias: the pointer names the canonical ID of the promoted ADR; presence is checked
  through `index.canonical_id` so a line naming an alias of the promoted ADR counts (AC-04).
- A `supersedes` naming a PADR promoted in the same handoff: not in the index, skipped (Non-Goal 4).
- A target outside `docs/decisions/` is still an ADR document when its `id` starts with `ADR-`; the pointer is written
  wherever the index found it.
- A target whose text cannot be read is an advisory `ProposalInvalidError` before the first write, like a PADR that
  does not parse.
- Nothing in preflight depends on the directories existing: a bundle without `decisions/` has no decisions and no
  pointers.

## 6. Verification & Test Plan

- Unit path tests (`packages/devkit-spec/tests/integration/features/proposals/`):
  - `test_proposal_scaffold.py`: `new` writes no directory (AC-01); `padr` creates `decisions/` (AC-02, already
    covered by `test_create_padr` once the scaffold assertion flips).
  - `test_proposal_handoff.py`: the pointer fixture (AC-03, AC-04, AC-05, AC-06), the roll-back (AC-07, with the
    existing `_fail_on` write patch pattern), a bundle without directories (AC-02).
  - `test_proposal_cli.py`: the text line and the JSON key (AC-03).
  - `test_proposal_handoff_worktree.py`: the plain handoff on `dev-<slug>` leaves the edited ADR in `git status`
    (AC-08) and `devkit rules check` on both ADRs passes.
  - `tests/integration/bundles/spec/test_writing_guidance.py` or the existing planning guidance test: the
    `materials/` sentence (AC-09).
- `just lint devkit-spec`, `just check devkit-spec`, `just test devkit-spec`, then `just test-affected`.
- `uv run devkit sync` after the bundle text change; `uv run devkit rules check --staged` before each commit.
