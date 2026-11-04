---
id: FB-viewer-namespace-roadmap-roots
title: The local viewer reads docs/roadmap/ only and will mis-render namespace milestones and their edges
scope: repo
kind: change-request
category: missing-capability
target: packages/devkit-viewer/src/devkit_viewer/features/browse/repositories/worktree.py
origin: agent
severity: workaround
recurring: false
status: promoted
created_at: 2026-11-04
---

# [FB-viewer-namespace-roadmap-roots] The local viewer reads docs/roadmap/ only and will mis-render namespace milestones and their edges

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: the viewer's dashboard listing and roadmap tab enumerate milestones from `docs/roadmap` and
  `docs/roadmap/_archive` in the registered working tree (`CAP-VIEW-repository-viewer` 4.1 and §5), reading the Git
  tree without the `[tool.docs]` namespace registry. `SPEC-namespace-roadmap` (Planning question q1, answer-01) keeps
  the viewer out of its scope on the user's decision, so once namespace milestones exist under
  `docs/packages/<name>/roadmap/`: they are missing from the roadmap tab and the dashboard milestone count; a global
  milestone whose `depends_on` names a namespace milestone renders as an unknown dependency and is never `ready`, even
  after that milestone is done; a proposal whose `milestone` names a namespace milestone appears in no roadmap card.
  No rule reports the gap, so the viewer silently disagrees with `devkit docs list milestone --all-namespaces`.
- **Proposed Procedure**: the dashboard listing and the roadmap tab also enumerate
  `docs/packages/*/roadmap/MS-*.md` and `docs/packages/*/roadmap/_archive/MS-*.md` by path pattern from the Git tree
  (the viewer reads no registry; an unregistered package directory would then show a milestone the rules report as
  misplaced, which the card can flag), and `CAP-VIEW-repository-viewer` 4.1 and §5 restate the two roots. Readiness
  and membership then resolve across roots because IDs are repository-wide.
- **Expected Benefit**: the viewer agrees with the CLI and the rules for a monorepo whose packages own milestones;
  cross-root `depends_on` edges and memberships render correctly.
- **Cost & Risk**: a devkit-viewer backend and frontend change (Node, rebuilt committed page); the 30-second list
  cache and paging contract are unchanged.
- **Attempted**: hypothesis; the effects were derived from the viewer code during the Planning challenger review
  (`frontend/src/lib/api/roadmap.ts` readiness and member filters, `worktree.py` roots).

## Diagnostic Details

- **Reproduction**: unknown until a namespace milestone exists; derived from code reading at the Planning head.
- **Expected / Actual**: expected the roadmap tab to list a namespace milestone and resolve edges to it; actual
  (by code): the listing is limited to the two global roots, `unknown` dependencies never count as satisfied and
  members are filtered over loaded milestones only.
- **Versions**: the `plan-namespace-roadmap` worktree at the Planning head.
- **Conditions**: a repository with registered namespaces and milestones under a namespace docs root, after
  `SPEC-namespace-roadmap` lands.
- **Workarounds Attempted**: not attempted; `devkit docs list milestone --all-namespaces` shows every milestone.
- **Related Assets**: `CAP-VIEW-repository-viewer` 4.1 and §5; `packages/devkit-viewer/frontend/src/lib/api/roadmap.ts`;
  `SPEC-namespace-roadmap` envelopes `challenger-01.yaml` finding 1 and `answer-01.yaml`.

## Evidence

```text
worktree.py dashboard_headers: roots = ["docs/roadmap", "docs/roadmap/_archive"] if section == "milestones"
worktree.py: re.fullmatch(r"docs/roadmap/(?:_archive/)?MS-[^/]+\.md", item.path)
CAP-VIEW-repository-viewer 4.1: "it MUST list frontmatter only for docs/roadmap/MS-*.md and flat docs/roadmap/_archive/MS-*.md files"
CAP-VIEW-repository-viewer: "A depends_on naming no milestone is shown as unknown and never counts as satisfied"
challenger-01.yaml finding 1 (P2, Decision needed); answer-01.yaml q1 choice a (user)
```

## Disposition

- **Disposition**: `SPEC-viewer-namespace-roadmap` receives discovery, dependency and membership work as a standalone proposal without milestone membership. Implementation remains pending.
