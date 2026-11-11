---
id: PROP-shared-fingerprinted-memo
title: One fingerprinted memo store for docs parse and rule facts
summary: Joins the devkit-docs parse memo and the devkit-agt rule facts memo on one fingerprinted, path-safe memo helper, so envelope validation and path safety live once.
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-11-11
target_area: capabilities/governance/
priority: low                         # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
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
    contract (`CAP-DOCS-document-model` 3.3-3.5, `CAP-GOV-rules-engine` section 5); they stay local. What is the same
    is the envelope (`version`, `fingerprint`, `entries` under an existing `.devkit/transient/`), the shape check,
    the atomic, unlocked, change-only write and the silent-miss failure policy. Path safety is implemented twice
    with different strictness; whether one policy replaces both is decision D1 below.

## 3. Proposed Design & Impact

### Shared helper (`devkit_core.core`)

- Safe memo path: given the root, the path parts below `.devkit/transient/` and whether a writer may create missing
  directories, return the memo path or the reason it is not used. It requires an existing, non-symlinked
  `.devkit/transient/` directory and refuses symbolic links and non-directories on the way, a non-regular file at
  the path and a path resolving outside the root.
- Envelope read: read the file, check the `{version, fingerprint, entries}` shape against the caller's format
  version and fingerprint, and return the raw `entries` mapping or a discard reason; a missing file is a distinct,
  silent outcome. It never logs: the caller logs the reason at its own level and wording.
- Envelope write: serialize `{version, fingerprint, entries}` with the caller's ordering choice (insertion order or
  sorted keys), skip the replacement when the bytes equal those read, and replace atomically through
  `atomic_write_bytes`; an `OSError` or `ValueError` is returned as a reason, never raised as an advisory.

### Kept local

- docs: file name, parser fingerprint and its module list, the tagged value codec, entry kinds, the "writing load"
  rule, the unusable-entry count and its single `info` line.
- agt: per-rule file name and rule-ID check, `facts_fingerprint` with the descriptor schema version and source
  dependencies, entry validation and codec, pending/complete/prune, snapshot read-only borrowing, `debug` logging.
- agt's framework fingerprint adds the new `devkit_core.core` module source, so a change to the envelope code
  invalidates facts memos as a change to `facts.py` does today; the docs parser fingerprint covers read, parse and
  codec modules only and does not add it (`CAP-DOCS-document-model` 3.3 lists its inputs).

### Behavior and verification

- Each memo's file bytes, hits, misses, discards and log lines stay as today except where decision D1 changes the
  docs memo's path policy. Both fingerprints change once, because each covers source files this change edits
  (`memo.py` lies in a fingerprinted package; `facts.py` is a framework source): the first run after the change is
  cold, which both contracts already allow (the memos are disposable derived state).
- Differential tests over both corpora: the existing `test_memo.py`, `test_memo_index.py` and `test_file_facts.py`
  pass unchanged, plus new unit tests of the helper in `packages/devkit-core/tests/unit/` covering each refusal
  reason. Differential evidence for each memo: over the repository corpus, the `entries` the code before and after
  the change writes are equal (the fingerprint aside), and over a fixture set of malformed, foreign-version,
  symlinked and non-regular memo files both versions reach the same outcome (used, discarded or not used, written or
  not) and log the same lines, except the cases D1 changes. The Development worker produces the "before" side from
  its own worktree head before the first source edit and keeps it in the spec's materials.
- Documentation: `CAP-GOV-rules-engine` section 5 and `CAP-DOCS-document-model` 3.3 name the shared helper for safe
  storage only where they state the path rule; no ADR changes (storage location, format and writer policy are
  unchanged).

### Planning decisions

- Helper home `devkit_core.core` (Q1), settled by evidence.
- Fingerprint computation stays in each memo: inputs and hashing differ by contract, and a shared hasher would move
  two short loops while coupling two independently versioned input lists.
- Entry validation and payload codecs stay in each memo (Q2).

### Open decision for the user

- **D1 (path policy)**: converge both memos on the stricter agt path rule (every component from `.devkit/` down
  checked) or keep each memo's current rule behind a helper parameter. See the `worker` envelope question `q1`.

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
