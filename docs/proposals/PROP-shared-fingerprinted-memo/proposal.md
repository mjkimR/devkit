---
id: PROP-shared-fingerprinted-memo
title: One fingerprinted memo store for docs parse and rule facts
summary: Moves the safe memo path check and the memo envelope shape check of the devkit-docs parse memo and the devkit-agt rule facts memo into one devkit-core helper, so path safety and envelope validation live once.
status: accepted                     # draft | reviewing | accepted | rejected
created_at: 2026-11-11
target_area: capabilities/governance/
priority: low                         # critical | high | medium | low
size: S                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/governance/
    - capabilities/documents/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-shared-fingerprinted-memo] One fingerprinted memo store for docs parse and rule facts

## 1. Background & Hypothesis

Two fingerprinted memos (the docs parse memo and the agt rule facts cache) each implement path safety and envelope
validation. Every hardening must be repeated in both. Source: `docs/materials/2026-11/20261111-review-refactor-code-pass/report.md` X-9 (deferred: larger change; revisit with the
facts cache).

## 2. Technical Spike Questions

- **Q1**: Which layer can own the helper without a new forbidden edge (devkit-core is the candidate)?
  - **Answer**: `devkit_core.core`, as a new module beside `files.py` and `paths.py`. Both memos already import
    `devkit_core.core` (`atomic_write_bytes`), so no package or feature edge is added; `ARCH-05-2-components` gives
    that package generic filesystem primitives, and the helper needs only the standard library. The only other
    reachable home, `devkit_agt.features.rules`, would make the docs memo depend on a rule-engine internal for a
    storage concern. Evidence: `materials/memo-comparison.md` (Package placement).
- **Q2**: Do the two memos' invalidation and schema rules differ in ways a shared helper must keep apart?
  - **Answer**: yes. Fingerprint inputs and hash, entry shape and validation, serialization order, logging level,
    writer authority, pruning, directory creation and snapshot borrowing all differ and are each fixed by its
    contract (`CAP-DOCS-document-model` 3.4.3-3.4.5, `CAP-GOV-rules-engine` section 5); they stay local. What is
    the same is the envelope (`version`, `fingerprint`, `entries` under an existing `.devkit/transient/`), the atomic,
    unlocked, change-only write and the silent-miss failure policy. Path safety and the envelope shape check are each
    implemented twice with different strictness (symlinked components, extra top-level keys); one rule replaces
    both (Planning decision D1, decided by the user).

## 3. Proposed Design & Impact

### Shared helper (`devkit_core.core`)

The duplicated hardening is the path check (about 18 lines in each memo) and the envelope shape check (8-10 lines);
reads, serialization and writes differ in ordering, skip rule and logging and already share `atomic_write_bytes`, so
they stay local (`envelopes/challenger-01.yaml` finding 2).

- `safe_memo_path(root, parts, *, create)`: given the resolved root and the path parts below `.devkit/transient/`,
  return the memo path or the reason it is not used. It requires an existing `.devkit/transient/` directory, refuses a
  symbolic link, a non-directory or a resolve mismatch at every component from `.devkit/` down, creates missing
  directories below `.devkit/transient/` only when `create` is set, and refuses a non-regular file at the path. It
  never logs and never raises for these outcomes.
- `envelope_problem(loaded, version, fingerprint)`: a pure check of an already parsed object, returning `None` when
  it is a mapping of exactly `version`, `fingerprint` and `entries` with the expected integer version, the expected
  fingerprint and a mapping of entries, else the discard reason.

### Kept local

- docs: file name, JSON parse with its non-finite-constant refusal, parser fingerprint and module list, the tagged
  value codec, entry kinds, the writing-load rule and its entries-based change test, compact insertion-order
  serialization, the unusable-entry count and the `info` log lines.
- agt: per-rule file name and rule-ID check, JSON parse, `facts_fingerprint` with the descriptor schema version and
  source dependencies, per-entry validation and codec, pending/complete/prune, the byte-equality skip, canonical
  serialization, snapshot read-only borrowing and `debug` logging of exceptions.
- Each caller logs the helper's reason at its own level and wording; the docs memo passes `create` for a writing load
  (at open, or by rechecking the path at save as agt does), so a missing `docs/` directory is still created silently
  (`CAP-DOCS-document-model` 3.4.5).
- agt's `_FRAMEWORK` fingerprint sources add the new `devkit_core.core` module, since the moved checks count as
  framework source today through `facts.py`; the docs parser fingerprint does not (`CAP-DOCS-document-model` 3.4.3
  lists read, parse and codec inputs).

### Behavior and verification

- Outcomes change only for the cases decision D1 converges: a hand-made memo with extra top-level keys (agt) and a
  symbolic link at `.devkit/` or a resolve mismatch on a directory (docs). Neither writer produces either today.
- Both fingerprints change once because each covers source this change edits (`memo.py` lies in a fingerprinted
  package; `facts.py` is a framework source): the first run after the change is cold, which both contracts allow.
- Tests: the existing `test_memo.py`, `test_memo_index.py` and `test_file_facts.py` pass, with
  `test_file_facts.py`'s `_FRAMEWORK` patch still controlling the facts fingerprint; new unit tests of both helper
  functions in `packages/devkit-core/tests/unit/` cover each refusal reason.
- Differential evidence: a fixture harness drives only public entry points (`DocumentIndex.load`; `WorkspaceCache`
  with `get_file_facts` and `flush_file_facts`, `facts_writer=True`), creates `.devkit/transient/` itself, and records
  per fixture (malformed, foreign-version, extra-key, symlinked, non-regular and missing memo files) whether the memo
  was used, discarded or not used, written or not, and its log records as logger, level and message without
  `exc_info`. The Development worker commits the harness and its "before" table from its own worktree head before the
  first source edit; after the change the table matches except the D1 cases.
- Documentation: `CAP-DOCS-document-model` 3.4.3 and `CAP-GOV-rules-engine` 5.3 state the converged path rule; no ADR
  changes (storage location, format and writer policy are unchanged).

### Planning decisions

- Helper home `devkit_core.core` (Q1), settled by evidence: no new package or feature edge.
- Scope narrowed to the path check and the envelope shape check; size `S` (challenger finding 2). Fingerprints, JSON
  parsing, entry validation, serialization and writes stay in each memo.
- The non-finite-constant difference stays local with the JSON parse, so it is not changed.
- **D1 (one rule for both memos)**, decided by the user (`envelopes/answer-01.yaml`, q1 option a): both memos use the
  stricter agt path rule (every component from `.devkit/` down) and the stricter docs envelope shape (exactly
  `version`, `fingerprint` and `entries`), with no strictness parameters on the helper; the docs memo passes `create`
  for a writing load. Acceptance criteria: the differential table matches "before" except the D1 cases, and the path
  sentences of `CAP-DOCS-document-model` 3.4.3 and `CAP-GOV-rules-engine` 5.3 state the converged rule. No PADR: the
  choice is local to this refactor and changes no storage location, format or writer policy.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr shared-fingerprinted-memo "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept shared-fingerprinted-memo --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff shared-fingerprinted-memo.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
