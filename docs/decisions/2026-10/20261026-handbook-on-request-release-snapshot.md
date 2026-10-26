---
id: ADR-handbook-on-request-release-snapshot
title: Handbook as an on-request release snapshot
summary: For a human entry point to devkit, we keep a tracked handbook/ derived from docs/, refreshed only when the user runs its playbook during release preparation and verified at release only then, to add no reconcile duty, accepting a handbook that may trail several releases.
proposal: SPEC-release-handbook
status: accepted
created_at: 2026-10-26
---

# [ADR-handbook-on-request-release-snapshot] Handbook as an on-request release snapshot

- **Status**: Accepted
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

`docs/` is written for agents and split by contract and ID; a person has no single entry point to what devkit is and
how to use it. A derived handbook gives one, but any derived copy that must stay current becomes a second reconcile
target. Releases are frequent (v0.1.0 to v0.1.3 within 11 days, 239 `docs/` files changed between two of them), so
a refresh bound to every tag means a near-full rewrite, translation and human review every few days.

## 2. Decision Drivers

- No new obligation for `spec-sync` or Living Spec reconcile.
- A handbook a reader can trust: it states which release it describes and matches that release's `docs/`.
- Refresh cost under the user's control, not the release cadence's.
- Releases that do not refresh stay independent of the handbook.

## 3. Considered Options

- **Delivery form**: a tracked `handbook/` on `main` (browsable in the tag, linkable from `README.md`); a GitHub
  Release asset built from the tag (nothing tracked, no browsable path); an untracked on-demand artifact (no release
  binding, no provenance a reader can check).
- **Refresh cadence**: every release tag (rewrite cost every few days); minor releases only (still a fixed cadence);
  only when the user explicitly runs the playbook (cost chosen per release).
- **Release gating**: a refreshing release fails on verification or a `docs/` mismatch; or it only warns.

## 4. Decision Outcome

- The handbook is a tracked `handbook/` directory on `main`, committed during release preparation before the tag,
  because a tag then carries a browsable handbook matching its own `docs/`.
- It is refreshed only when the user explicitly runs the handbook playbook; there is no cadence. A release that does
  not refresh keeps the previous handbook, whose provenance names its older tag, because cost then follows the user's
  choice.
- `handbook/manifest.json` names the release tag the refresh targets. `scripts/release.sh` treats a release as
  refreshing exactly when that tag equals the tag being built, a fact read from committed state; it runs no generation
  or refresh.
- A refreshing release fails its build on handbook verification failure or when `docs/` at the tagged commit differs
  from `docs/` at the manifest source commit. Every other release is unaffected.
- The handbook is a derived view: never a source of truth and never a reconcile target; the Living Spec prevails on
  any conflict.

## 5. Consequences

- Positive: no reconcile duty; each refreshed tag has a verified handbook matching its `docs/`; refresh cost is paid
  only when chosen.
- Negative: the handbook may trail several releases; readers rely on its provenance header to see how old it is.
- Risk: a refresh started for one version and released under another fails no check, because the manifest tag no
  longer matches; the release then counts as non-refreshing. The playbook writes the tag from `VERSION`.
- Follow-up: when no refresh has run for a minor release, the user decides whether to refresh; no automation
  triggers it.

## 6. Confirmation

- Release-script tests in Development: a manifest tag equal to the built tag with a differing `docs/` tree fails the
  build; a differing manifest tag skips the handbook checks and runs no handbook command that writes files.
- Handbook script fixture tests for the verification checks (proposal section 3.3 step 3).
- `RULE-cli-contract` excludes `handbook/**`; `just rules-check` stays clean after a cited command is renamed.
