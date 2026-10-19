---
id: PADR-effective-policy-digest
title: Effective policy digest
summary: The approval binds a digest of the parsed integration policy devkit owns (approvals, worktree and integration provider keys) instead of the raw config and receipt bytes, and refuses a managed path both sides changed.
proposal: PROP-integration-follow-ups
status: draft
created_at: 2026-10-19
---

# [PADR-effective-policy-digest] Effective policy digest

- **Status**: Draft
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

The request binds a digest of the raw bytes of `.devkit/config.toml` and `.devkit/installation.json`
(`integration/providers.py` `policy`, `service.py` `_post_policy`). The receipt lists every managed asset hash, so any
activity that edits a bundled skill invalidates every open confirmation though no integration policy changed
(`FB-integration-stale-on-base-advance`: target `fa6aa90` changed the receipt and four bundle files).

## 2. Decision Drivers

- The approval binds what changes the integration's authority and effects, nothing else.
- Fail closed when the merged result could be inconsistent.

## 3. Considered Options

- Keep the raw-byte digest (every asset edit is stale).
- Tolerate only base commits outside `.devkit/` (the feedback's suggestion; still stale on every sync).
- Digest parsed devkit-owned policy values, and refuse a receipt-recorded path both sides changed.

## 4. Decision Outcome

The digest covers `[workflow.approvals]` `dev-integration`, `[worktree]` `pull_request`, `delete_branch` and
`merge`, and `[integration] provider`, normalized after parsing. The base's digest must be equal at confirmation and
execution; the result commit's digest must equal the one prospected at confirmation. Provider, guard and cleanup
extension identities stay separate request fields. A path recorded in the receipt, or the receipt itself, changed on
both sides since the merge base is refused before anything lands.

## 5. Consequences

- Bundle syncs and asset edits on the target no longer invalidate confirmations.
- Provider-owned policy (such as `[tool.spec]`) is checked by the provider's re-run, not by this digest.
- A source and a target that both re-synced the same managed files must integrate the target into the source first.
