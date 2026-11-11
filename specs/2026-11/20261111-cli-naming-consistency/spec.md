---
id: SPEC-cli-naming-consistency
title: Consistent CLI option naming
summary: 'Aligns CLI naming: bundle refresh previews without digests instead of a --check flag, workflow envelope new is listed in help, and spec new accepts --task-kind like proposal new.'
status: in-progress
created: 2026-11-11
related_capabilities:
  - CAP-DIST-in-repo-bundles
  - CAP-DLV-cli-and-output
  - CAP-DLV-spec-bundles
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-cli-naming-consistency] Consistent CLI option naming

## 1. Problem Statement & Motivation

Three commands name the same idea differently from their neighbours, so an agent that learns one command misreads
another:

- `devkit bundle refresh --check` means "preview, write nothing" (exit 0), while `devkit sync --check` is a CI gate
  that exits 1 on drift. The apply form already needs both reviewed digests, so the flag adds nothing but the clash.
- `devkit workflow envelope new` is hidden from `devkit workflow envelope --help` as an authoring command, yet it is
  the only writer of the scout, challenger, final-report, reconcile-check, ux-review and red envelopes the spec
  bundle tells agents to write.
- `devkit spec proposal new` selects the task kind with `--task-kind feature|bugfix`; `devkit spec new` only with
  `--workflow sdd-spec-feature|sdd-spec-bugfix`, so the guidance restates the mapping at every call site.

The user agreed this contract change in the review-refactor run rr-20261111-guidance-cli. The commands have no
external consumers beyond `devkit.advisory` and `devkit-cli`, which this change does not touch, so no
compatibility shim is kept.

## 2. User Stories

- **US-1**: As an agent refreshing a bundle snapshot, I want the preview to be the form without digests so that
  `--check` keeps one meaning (a CI gate) across devkit.
- **US-2**: As an agent writing a scout, challenger or final-report envelope, I want `envelope new` listed in the
  envelope group help so that I can discover the command the guidance tells me to use.
- **US-3**: As an agent creating a spec for a defect, I want `devkit spec new --task-kind bugfix` so that I name the
  task kind the same way as for `devkit spec proposal new`.

## 3. Non-Goals

1. **Scope Excluded**: no other option, output or error code changes; `devkit sync --check` is unchanged;
   `devkit workflow new`, `bind`, `checks` and `validate` stay hidden; `--workflow` on `spec new` stays.
2. **Scope Excluded**: the release handbook, use case documents and the `sdd-spec-bugfix` workflow description keep
   their `--workflow sdd-spec-bugfix` examples, which remain valid.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Refresh without digests previews
- **Given** an existing bundle snapshot and an accessible source checkout
- **When** the agent runs `devkit bundle refresh DEST --source SOURCE` without `--expect` and `--candidate`
- **Then** it exits 0 with one JSON object whose status is `preview` and code `BUNDLE_SNAPSHOT_PREVIEW`, carrying
  `current_digest` and `candidate_digest`, and no file under `DEST` changes

### [AC-02] Refresh with both digests applies
- **Given** the digests a preview returned
- **When** the agent runs `devkit bundle refresh DEST --source SOURCE --expect CURRENT --candidate REVIEWED`
- **Then** the snapshot is replaced (status `updated`, or `unchanged` when nothing differs); a digest that does not
  match the current snapshot or prepared source is still refused with `BUNDLE_SNAPSHOT_CONFLICT` (exit 2) and
  nothing is written

### [AC-03] One digest alone is an argument error
- **Given** an existing bundle snapshot
- **When** the agent gives only one of `--expect` and `--candidate`
- **Then** the command exits 2 with `ARGUMENT_INVALID`, `[TARGET]` the missing flag, and writes nothing

### [AC-04] Refresh has no `--check` option
- **Given** any snapshot destination
- **When** the agent passes `--check` to `devkit bundle refresh`
- **Then** the parser rejects the unknown option with exit 2, and `devkit bundle refresh --help` lists no `--check`

### [AC-05] `envelope new` is listed in the envelope help
- **Given** the installed `devkit` command
- **When** the agent runs `devkit workflow envelope --help`
- **Then** the command list includes `new`, while `devkit workflow --help` still omits `new`, `bind`, `checks` and
  `validate`, each of which stays callable with its own `--help` (exit 0)

### [AC-06] `spec new --task-kind` selects the spec workflow
- **Given** a Development branch `dev-<slug>` where `sdd-spec-feature` and `sdd-spec-bugfix` are available
- **When** the agent runs `devkit spec new <slug> --task-kind bugfix`
- **Then** `spec.md` is bound to `sdd-spec-bugfix` and the bundle holds `spec.md` only; `--task-kind feature` binds
  like no option (`sdd-spec-feature`, or an unbound spec with the `SPEC_UNBOUND` notice when that workflow is not
  available)

### [AC-07] `--task-kind` and `--workflow` exclude each other
- **Given** a Development branch `dev-<slug>`
- **When** the agent gives both `--task-kind` and `--workflow`, or a `--task-kind` other than `feature` or `bugfix`
- **Then** the command exits 2 with `ARGUMENT_INVALID`, `[TARGET] --task-kind`, and writes nothing

### [AC-08] Guidance and contracts name the new forms
- **Given** the capability contracts, reference documents, the installation guide and the bundle guidance
- **When** they show a refresh preview, the hidden workflow commands or a defect spec creation
- **Then** the refresh preview is the form without digests, `envelope new` is not listed as hidden, and the spec
  bundle's `spec`, `worktree` and `spec-specify` guidance says `--task-kind bugfix`

## 5. Assumptions

- `--task-kind feature` binds exactly as no option does, as a proposal handoff treats the default task kind
  (`sdd-spec-feature` when available, else unbound with a notice). Recorded because an explicit feature could have
  been made strict instead; consistency with handoff was preferred.
- The one-digest refusal is checked in `RefreshBundleSnapshot`, so the library and the CLI refuse alike, and uses
  the shared `ARGUMENT_INVALID` code rather than `BUNDLE_SNAPSHOT_CONFLICT`, since the input is malformed rather
  than stale.
- No decision record changes: `ADR-bundle-source-snapshots` requires explicit refresh with matching digests but
  names no flag, and `ADR-delivery-classification` lists `spec new --workflow`, which stays; the hidden-command list
  is stated only in `CAP-DLV-cli-and-output`.
