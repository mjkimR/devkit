---
id: PROP-namespace-roadmap
title: Per-namespace milestones under the namespace docs root
summary: "Lets a registered namespace keep its own MS milestones under docs/packages/<name>/roadmap/ with the global lifecycle and selection, so packages on their own cadence stop crowding the global roadmap."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-04
target_area: documents/
namespace: global
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-monorepo-namespace-support
boundaries:
  owns:
    - packages/devkit-docs/src/devkit_docs/features/documents/models/
    - packages/devkit-docs/src/devkit_docs/features/documents/services/
    - packages/devkit-docs/src/devkit_docs/features/governance/usecases/
    - packages/devkit-spec/src/devkit_spec/features/proposals/usecases/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/
    - docs/capabilities/documents/
    - docs/roadmap/README.md
    - docs/architecture/ARCH-01-introduction-and-goals.md
    - docs/decisions/2026-11/20261102-roadmap-and-milestones-ledger.md
  excludes:
    - .devkit/managed/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-namespace-roadmap] Per-namespace milestones under the namespace docs root

## 1. Background & Hypothesis

`CAP-DOCS-namespaces` mirrors `docs/` under `docs/packages/<name>/` for capabilities, use cases, UX and architecture
documents, but milestones are global only. `ADR-roadmap-and-milestones-ledger` §4 deferred per-namespace roadmaps
"until a repository needs them", and the code enforces the deferral: `milestone_path_valid` accepts only
`docs/roadmap/(_archive/)?MS-<slug>.md`, and `RULE-id-convention` walks every namespace `roadmap/` directory and
reports each file there as misplaced (`id_convention.py`, the `docs_root == "docs"` condition). The `MILESTONE` kind
row is `FormatScope.GLOBAL`, and the Backlog references state that milestones are global.

A monorepo whose packages are independent products now needs them: g-sandbox (`playground/g-sandbox`) holds four games
sharing one platform, each with its own release cadence and its own background under `docs/packages/<game>/`. Its
milestones would either crowd one global roadmap with unrelated themes or stay outside the document system.

Hypothesis: the namespace layer already supplies what per-namespace milestones need. Membership of a document under
`docs/packages/<name>/` is `<name>` (`CAP-DOCS-namespaces` 3.2), `devkit docs list` already selects namespaces, and
`living_path` already maps `docs/packages/<name>/roadmap/X` to `docs/roadmap/X` for the rules. Allowing the placement
and making the lifecycle checks namespace-aware is therefore a contained change; no new discovery command or ID scheme
is needed. This is the first direct member of `MS-monorepo-namespace-support`.

## 2. Technical Spike Questions

- **Q1**: Which checks and commands hard-code the global roadmap root, and does each need the namespace root or only
  `living_path`? Known today: `milestone_path_valid` and its callers in `RULE-id-convention` and the proposal
  `--milestone` validation (`devkit_spec.features.proposals.usecases.roadmap`); the `FormatScope.GLOBAL` row of the
  kind table; the roadmap and Backlog references and the roadmap README.
- **Q2**: Where does a namespace milestone cite its goal? `ADR-roadmap-and-milestones-ledger` keeps goals as prose in
  `ARCH-01-introduction-and-goals` and names "goals per namespace" as its own reopen condition. The candidate is a
  namespace steering file (`PROP-namespace-steering`), which does not exist yet; Planning decides whether a namespace
  milestone may cite the global goals meanwhile and whether the two proposals share one Planning round.
- **Q3**: What does a cross-namespace milestone edge mean? IDs are repository-wide, so `depends_on: [MS-<other>]`
  across namespaces resolves; Planning confirms the lifecycle rules (activate shows dependencies not done or dropped)
  need no namespace clause, and how `devkit docs list milestone` without `--namespace` behaves from a package directory
  (`CAP-DOCS-namespaces` 3.3 default selection).

## 3. Proposed Design & Impact

- **Placement**: a milestone of a registered namespace lives at `docs/packages/<name>/roadmap/MS-<slug>.md`
  (planned/active) or `docs/packages/<name>/roadmap/_archive/MS-<slug>.md` (done/dropped), the global layout under the
  namespace docs root. `milestone_path_valid` takes the docs root it validates against; `RULE-id-convention` passes the
  namespace root it is walking. An unregistered `docs/packages/<name>/` stays a plain `docs/` directory, as today.
- **Identity and membership**: IDs, aliases and the `MS-` prefix stay repository-wide; a namespace milestone is a
  member of its namespace by path (3.2) and a proposal declares membership through `milestone` as before, whatever
  its own namespace. `devkit spec proposal new --milestone` accepts a milestone at either root.
- **Selection**: `devkit docs list milestone --namespace <name>` and `--all-namespaces` follow the existing rules; the
  roadmap and Backlog references replace "milestones are global" with the two roots, and the roadmap README names the
  namespace root.
- **Decision record**: the "Milestones are global; per-namespace roadmaps are deferred" clause of
  `ADR-roadmap-and-milestones-ledger` is superseded in part by the PADR this proposal records; Development writes the
  pointer. `.devkit/managed/` copies are regenerated, never edited.
- **Tests**: `RULE-id-convention` fixtures with a registered namespace milestone at each lifecycle location, an
  unregistered `docs/packages/<name>/roadmap/` file still reported, a namespace `_archive/` move, and `proposal new
  --milestone` naming a namespace milestone.

Expected affected contracts: `CAP-DOCS-namespaces` (3.2, 3.4, the kinds a namespace mirrors), `CAP-GOV-spec-rules`
(`RULE-id-convention`), the roadmap section of `ARCH-01-introduction-and-goals`, `ADR-roadmap-and-milestones-ledger`
(superseded in part).

## 4. Lifecycle & Retirement Criteria

Planning settles Q1 to Q3; acceptance and handoff create one feature spec. Completion requires the rule and command
tests above, synchronized references and a monorepo fixture in which `devkit rules check` reports no finding for a
namespace milestone at each lifecycle location.

Non-goals: namespaced IDs or per-package ID spaces; per-namespace goals as ID-bearing documents; a namespace copy of
`_archive/` semantics beyond the path; external tracker synchronization of namespace roadmaps.
