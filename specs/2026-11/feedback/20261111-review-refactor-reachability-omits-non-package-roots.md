---
id: FB-review-refactor-reachability-omits-non-package-roots
title: Review-refactor reachability does not name non-package code roots such as scripts/
scope: repo
kind: change-request
category: missing-capability
target: packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor/references/criteria.md
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-11-11
---

# [FB-review-refactor-reachability-omits-non-package-roots] Review-refactor reachability does not name non-package code roots such as scripts/

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `criteria.md` §4 asks reachability to cover "static references and the repository's dynamic
  reach (entry points, plugin registries, configuration, documentation, string dispatch)". The searches the run made
  were scoped to package sources and tests.
- **Proposed Procedure**: Name the repository's non-package code roots as part of static reach: scripts, tools, task
  runner recipes and CI workflow files. Also ask that a moved or renamed name be searched over the whole tracked tree
  (for example `git grep`), not only over the selected surface.
- **Expected Benefit**: A move no longer breaks a release or maintenance script that imports the old location.
- **Cost & Risk**: One wider search per removal or move. There is some extra noise from documentation hits.
- **Attempted**: Tested in this session. A whole-tree search found the importer after the failure.

## Diagnostic Details

- **Reproduction**: The code-surface run moved `IGNORED_NAMES` out of the distribution manifest module.
- **Expected / Actual**: Expected reachability to list every importer. Actually,
  `scripts/releases/prepare.py` still imported the old location, and only a later check exposed it.
- **Versions**: work item branch during phase 2 (before 869b8f19).
- **Conditions**: The searches were run per package by the surface's subagents.
- **Workarounds Attempted**: Changed the import to `devkit_dist.features.distribution.models.content`. This worked.
- **Related Assets**: `criteria.md` §4 Reachability.

## Evidence

```text
scripts/releases/prepare.py: from <old manifest module> import IGNORED_NAMES  -> ImportError after the move
per-package reachability searches: no hit outside packages/
```

- **Disposition**: review-refactor references/criteria.md §4 Reachability names the non-package code roots and a whole-tree search for moved or renamed names.
