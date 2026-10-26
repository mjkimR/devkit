---
id: PROP-merge-proposal-materials-at-handoff
title: Merge existing proposal materials during handoff
summary: "Allows proposal handoff to merge materials into an existing destination after a complete collision and path-safety preflight, preserving existing files and refusing conflicting content."
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: delivery/
priority: medium
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/features/proposals/
    - packages/devkit-spec/tests/
    - docs/capabilities/delivery/
    - docs/capabilities/governance/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-merge-proposal-materials-at-handoff] Merge existing proposal materials during handoff

## 1. Background & Hypothesis

The Development handoff of PROP-persistent-python-facts-cache created its worktree but refused to graduate the
proposal with `SPEC_PROPOSAL_TARGET_EXISTS`. Pre-existing measurements already occupied the destination directory
`docs/materials/2026-10/20261022-persistent-python-facts-cache/`, while the proposal held a different file,
`materials/design.md`. The preflight rejects the entire destination directory even when no leaf file collides.

Hypothesis: a recursive material merge plan can preserve the overwrite guard while accepting an existing directory
whose files do not conflict with proposal materials. The immediate recovery moves the measurements into the proposal
before handoff; this draft tracks the tool improvement separately.

## 2. Technical Spike Questions

- **Q1**: How should the merge plan represent directories, distinct files and byte-identical duplicate files while
  preserving target containment, non-symlink paths and existing document/ADR collision checks?
- **Q2**: How do preflight and execution detect concurrent target changes, distinguish file/directory collisions,
  and report a differing-content conflict before any proposal, ADR, spec or material mutation occurs?
- **Q3**: How should failure recovery preserve already-existing files without promising filesystem transactions
  for unrelated runtime I/O failures? Confirm the behavior in CLI and native handoff paths.

## 3. Proposed Design & Impact

- Extend material-destination preflight and relocation in the proposal handoff use case, shared by CLI and MCP.
- Permit existing directories and merge disjoint relative file paths recursively.
- Treat a regular file at the same path with byte-identical content as a duplicate; preserve the destination bytes.
- Refuse different-content files and file/directory type collisions with deterministic path information and the
  existing overwrite error code unless Planning establishes a concrete need for another code.
- Complete collision and path-safety checks for the whole handoff before moving anything. Preserve existing safe
  path and symbolic-link protections; directory merge must not broaden allowed roots.
- Add checks for a destination containing only measurements plus a proposal containing only design notes; nested
  disjoint files; identical duplicates; differing bytes; file/directory collisions; unsafe symlinks; and repeated
  handoff/recovery. For a preflight conflict, assert both source and destination trees remain unchanged and no spec
  or ADR was created.
- Reconcile the delivery handoff contract and affected governance references. Inspect tests under the nearest
  existing package test parent and add only required tiers.

Planning refinements (challenger-01 findings 1, 2, 4 and 6):

- **Per-leaf merge plan**: preflight builds one set of planned leaves from the `materials/` leaves and the carried
  extras, checked against the destination in one pass. An absent subtree is moved whole; an existing real directory
  is descended into; a file is a leaf move. Non-symlink `JUNK_FILES` are dropped on the source side and ignored on
  the destination side. The internal clash rule between extras and `materials/` paths stays unchanged.
- **Pre-existing paths are never handoff writes**: no pre-existing file or directory enters the roll-back's written
  or moved records, on the same file system or across file systems (`EXDEV`); `make_dirs` records only directories it
  created. A failure injected after some leaves moved leaves every pre-existing path byte-identical.
- **Per-file link origins**: in merge mode the relocation plan registers a file origin for each moved leaf and a
  directory origin only for a subtree the handoff created whole, so a pre-existing destination Markdown file keeps
  its bytes except links that pointed into the proposal.
- **Containment by `lstat` in preflight**: the destination and every existing directory on the way to a planned leaf
  must be a real directory; a symbolic link at or above a planned path is a collision refused before any write. The
  runtime re-check after writes started remains a guard, not the first detection.

Scope excluded: overwrite flags, automatic content conflict resolution, cross-filesystem transaction infrastructure,
changes to the facts-cache feature, and relaxation of ADR/ID or snapshot/receipt collision protections.

## 4. Lifecycle & Retirement Criteria

Acceptance requires an explicit merge/collision policy,
concurrency/recovery behavior and verifiable refusal criteria. Development completes when both handoff transports
use the same guarded merge plan and the success/refusal tests and Living Spec reflection pass.
