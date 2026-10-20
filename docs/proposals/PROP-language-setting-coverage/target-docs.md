---
id: PROP-language-setting-coverage-target
title: Language preference Living Spec targets
summary: "Maps shared language resolution, response-style inheritance and bounded approval-content coverage to Development reconciliation targets."
status: draft
proposal: PROP-language-setting-coverage
created_at: 2026-10-20
---

# [PROP-language-setting-coverage-target] Language preference reconciliation targets

- `CAP-DIST-workspace-ownership` and `CAP-DIST-sync-and-transactions`: presentation local allowlist, effective
  provenance, canonical/effective inventory resolution and existing receipt restrictions.
- `CAP-DIST-manifest-spec`: the single string-variable default_from binding and unchanged vars-only template API.
- `CAP-DIST-content-packages`: response-style inheritance, explicit override precedence and auto semantics.
- `CAP-INT-mcp-services`: owned language coverage, preserved evidence, authorization invariants and per-host evidence.
- `CAP-DLV-human-interaction` and `CAP-DLV-proposal-incubation`: handoff language and canonical effort values.
- `CAP-HOST-lifecycle-observation`: link bounded supplied-content coverage and explicit client-owned UI limitations;
  do not change registration, environment enforcement or host support.
- `docs/development/reference/distribution.md`, `docs/development/reference/host.md`,
  `docs/development/reference/integration.md` and relevant existing `guides/install/` pages: short configuration
  examples and links to the contracts, without duplicating the approval contract.

Promote this proposal's PADR through normal handoff. No existing ADR is superseded: the manifest/config extension
changes capability behavior while keeping established ownership, scalar template isolation and approval policy.
No current Living Spec is edited during Planning. If prerequisite reconciliation changes the target IDs, Host
refreshes the Planning/Development worktree before dependent edits rather than resolving IDs from another branch.
