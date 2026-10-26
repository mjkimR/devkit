---
id: PLAN-merge-proposal-materials-at-handoff
spec: SPEC-merge-proposal-materials-at-handoff
---

# Technical Plan: `SPEC-merge-proposal-materials-at-handoff` Merge existing proposal materials during handoff

## 1. Constitution & Invariant Review

`CAP-DLV-proposal-incubation` rule 4 ("validate everything before writing") and rule 5 (roll-back) hold and get
stricter: every merge conflict is refused in preflight, and no pre-existing path enters the roll-back records.
`ADR-merge-proposal-materials-per-leaf-at-handoff` authorizes the change of the contract that refused an existing
materials directory; no other `MUST` changes. Output follows `ARCH-08-1-agent-output`: the merge is a result field,
not a notice.

## 2. Architecture Overview & Impact

- Target Area: `delivery/`
- **`features/proposals/usecases/handoff.py`**:
  - A `_MaterialsPlan` (moves, whole-moved subtrees, dropped duplicates, merged flag) built by `_plan_materials`
    after `_plan_extras`. Without a pre-existing destination it keeps today's plan (`materials/` moved whole, extras
    per file). With one, `lstat` must show a real directory; the walk over `materials/` moves an absent subtree that
    holds material whole, descends into a real directory present on both sides, drops non-symlink junk, and classifies
    every same-path pair (`different-content`, `file-directory`, `symbolic-link`, `non-regular`, or a byte-identical
    regular-file duplicate). Each carried extra is checked the same way, with every existing directory on its way
    checked by `lstat`.
  - Merge mode drops the destination from `_check_targets` (only that path may pre-exist) and raises one
    `ProposalTargetExistsError` listing all conflicts, with a fix naming the first one.
  - Writes: each planned move runs `make_dirs` (records only created directories) and `move_path` (records only the
    absent destination), so roll-back never names a pre-existing path.
  - Relocation plan: `prefixes[materials/] = <dest>` stays; in merge mode a directory origin is registered per
    whole-moved subtree and a file origin per moved leaf, instead of one origin for `<dest>`. A dropped duplicate
    extra maps its links to the kept destination file (`exact`) without an origin.
  - `HandoffResult` gains `materials_merged` and `dropped_duplicates` (JSON through `to_dict`, shared by the CLI and
    the native `HandoffUseCase`).
- **`base/errors.py`**: the `ProposalTargetExistsError` docstring names the merge conflict; the code and class stay.
- **`features/delivery/cli/proposals.py`**: `merged=yes` on `[MATERIALS: ...]` and `[DROPPED_DUPLICATE: <path>]`
  lines; the module docstring lists them.
- **Living Spec**: `CAP-DLV-proposal-incubation` rule 4, rule 5, section 4.5 step 5 and the roll-back paragraph,
  4.7 (link origins), 4.10 output and JSON keys, and the error table. `docs/capabilities/governance/` needs no change
  (it names no handoff collision).
- **New Dependencies**: none.

## 3. Verification & Test Plan

- `packages/devkit-spec/tests/integration/features/proposals/test_proposal_handoff_merge.py`: AC-01 to AC-06
  (disjoint and nested merge, duplicates of materials and extras, each conflict kind with both trees unchanged and no
  spec or ADR, junk on both sides, a failure injected at the second move on one file system and with `EXDEV`, link
  origins, a rerun after recovery).
- `test_proposal_cli.py`: AC-07 text and JSON fields; the composed `--effort` path reuses `HandoffResult.to_dict`.
- Commands: `just lint devkit-spec`, `just check devkit-spec`, `just test-affected`, `just rules-check`.
