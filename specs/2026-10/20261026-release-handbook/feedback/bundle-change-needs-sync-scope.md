---
id: FB-bundle-change-needs-sync-scope
title: A delegated bundle change needs write scope for the sync it implies
scope: repo
kind: friction
category: instruction-conflict
target: development-worker role contract and spec-delegate write scope
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-26
---

# [FB-bundle-change-needs-sync-scope] A delegated bundle change needs write scope for the sync it implies

## 1. Friction / Question (friction, question)

- **Context**: A Development worker added a playbook asset and preset to a repository bundle and selected the preset
  in `.devkit/config.toml`, within the delegated write scope.
- **Expectation**: The delegated scope covers every file the agreed change needs, so the worker leaves a consistent
  repository.
- **Actual**: Deploying the asset is a `devkit sync` that writes `.devkit/managed/<bundle>/` and
  `.devkit/installation.json`; the scope denied `.devkit/managed/`. The reconcile check also found a Living Spec page
  (`docs/development/ci-cd.md`) describing the changed release script outside the scope.
- **Workaround (or Interpretation Chosen)**: Left the sync and the one-sentence page update undone and handed both to
  the Host in `reconcile.md` and the worker envelope.
- **Suggestion**: When a task boundary includes a bundle source that the project selects, `spec-delegate` adds the
  sync outputs (`.devkit/managed/<bundle>/`, `.devkit/installation.json`) to the write scope; and the scope includes
  the documents `devkit spec search` finds for changed scripts, or the contract tells the worker to raise them before
  the reconcile stage.

## Evidence

```text
devkit sync --check: [CHANGE: update .devkit/managed/<bundle>/bundle.toml] [CHANGE: create .devkit/managed/<bundle>/playbooks/handbook.md] [CHANGE: update .devkit/installation.json]
devkit playbook get <bundle>/handbook: SELECTION_INVALID (playbook is not synchronized)
reconcile-check-01 finding 1 (P2): docs/development/ci-cd.md section 3 not updated for the release-script check
```

## Disposition

Resolved by `SPEC-delegation-sandbox-guidance`: `spec-delegate`'s `references/payload.md` tells the Host to add the
tracked files `devkit sync --check` lists for a selected-bundle change (for example `.devkit/installation.json` and the
managed `AGENTS.md` block) to the worker's write scope; `.devkit/managed/` is ignored and never a write path. The
`development-worker` contract runs `devkit sync` after such an edit, commits those files and raises a tracked output
the scope omits as a problem. The second suggestion was already covered: the worker's write scope includes the Living
Spec paths the reconcile record targets. Verified by
`packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py`.
