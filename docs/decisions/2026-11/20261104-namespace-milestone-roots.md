---
id: ADR-namespace-milestone-roots
title: Per-namespace milestones under the namespace docs root
summary: For a monorepo whose packages run on their own cadence, we let a registered namespace keep MS milestones under docs/packages/<name>/roadmap/ with the global lifecycle, identity and selection, to keep the global roadmap readable, accepting one more roadmap root per namespace to check.
proposal: SPEC-namespace-roadmap
supersedes: [ADR-roadmap-and-milestones-ledger]
status: accepted
created_at: 2026-11-04
---

# [ADR-namespace-milestone-roots] Per-namespace milestones under the namespace docs root

- **Status**: Accepted
- **Date**: 2026-11-04

---

## 1. Context & Problem Statement

`ADR-roadmap-and-milestones-ledger` keeps milestones global ("Milestones are global; per-namespace roadmaps are
deferred until a repository needs them") and the code enforces it: `milestone_path_valid` accepts only
`docs/roadmap/(_archive/)?MS-<slug>.md`, `RULE-id-convention` reports every file under a namespace `roadmap/`
directory as misplaced, `RULE-spec-format` scans the global root only (`FormatScope.GLOBAL`) and `devkit spec
proposal new --milestone` refuses a milestone outside the global root. A monorepo whose registered namespaces are
independent products (several games sharing one platform, each with its own release cadence) has milestones that
belong to one package. Today they either crowd the global roadmap with unrelated themes or stay outside the document
system, while `CAP-DOCS-namespaces` already mirrors every other Living Spec directory under `docs/packages/<name>/`.

---

## 2. Decision Drivers

- The global roadmap stays readable when packages evolve on their own cadence.
- Identity stays repository-wide (`CAP-DOCS-namespaces` 3.3 rule 5): no namespaced IDs, no per-package ID space.
- The milestone lifecycle (placement, flat `_archive/`, closure, membership through direct proposals) has one
  definition, not one per root.
- The change rides the existing namespace layer (`namespace_of`, `living_path`, `docs_roots`, the `docs list`
  selection) instead of adding a discovery command or a registry field.

---

## 3. Considered Options

- **Namespace roadmap root under the namespace docs root** (selected): `docs/packages/<name>/roadmap/MS-<slug>.md` and
  `docs/packages/<name>/roadmap/_archive/MS-<slug>.md` for a registered namespace, validated by mapping the path
  through `living_path` onto the global layout; the smallest change, and the layout every other mirrored kind uses.
- **Keep the current state**: one global roadmap; a package's milestones carry their package in the title or summary.
  Viable for a repository with one product, which is why the ADR deferred; fails the readability driver for a
  monorepo of independent products and leaves their milestones outside the document system.
- **Namespace field on a global milestone**: `docs/roadmap/MS-<slug>.md` with `namespace: <name>` in frontmatter. Keeps
  one directory but contradicts `CAP-DOCS-namespaces` 3.2 (membership by path for documents under `docs/`, by anchor
  field only for bundles), so selection and the rules would need a milestone-only membership exception.
- **Roadmap per package source directory** (`<package path>/docs/roadmap/`): outside the document system's source
  directories (`docs/`, `specs/`), so indexing, rules and lookup would all need a new root.

---

## 4. Decision Outcome

The namespace roadmap root, because it completes the mirror `CAP-DOCS-namespaces` already defines and leaves
identity, lifecycle and selection as they are.

- A milestone of a registered namespace lives at `docs/packages/<name>/roadmap/MS-<slug>.md` when planned or active and
  at `docs/packages/<name>/roadmap/_archive/MS-<slug>.md` when done or dropped; the global roots keep their meaning.
  → `CAP-GOV-spec-rules` Milestone validation contract (MUST); `CAP-DOCS-namespaces` 3.4 (the rules treat the
  namespace `roadmap/` like `docs/roadmap/`).
- Placement is validated by mapping the path through `living_path` with the registered namespaces onto the global
  layout; a file under an unregistered `docs/packages/<name>/roadmap/` stays misplaced, as any document of an
  unregistered directory does. → `CAP-GOV-spec-rules` (`RULE-id-convention`, `RULE-spec-format`).
- IDs, aliases and the `MS-` prefix stay repository-wide; a namespace milestone belongs to its namespace by path
  (`CAP-DOCS-namespaces` 3.2 rule 1) and is selected by `devkit docs list` and `search` as the other kinds are
  (3.3). → `CAP-DOCS-namespaces` 3.2, 3.3 (MUST, unchanged rules).
- A direct proposal of any namespace declares membership through `milestone` naming a milestone at either root;
  `devkit spec proposal new --milestone` accepts both. → `CAP-DLV-proposal-planning` (`--milestone`).
- Milestone `depends_on` edges resolve across namespaces as any repository-wide reference does; the lifecycle
  guidance (activate, close, drop, reopen, merge) gains no namespace clause and names "the milestone's roadmap root"
  where it named `docs/roadmap/`.
- A namespace milestone names the goal it advances as a global milestone does: in prose, citing
  `ARCH-01-introduction-and-goals` or an architecture document under its namespace docs root by ID; a namespace
  steering file (`SPEC-namespace-steering`), which carries no ID, may be named by path once it exists. The citation
  stays a recommendation checked in review only, as today.
- This replaces, in part, the clause of `ADR-roadmap-and-milestones-ledger` "Milestones are global; per-namespace
  roadmaps are deferred until a repository needs them" (ADR-milestone-documents) and the global-root wording of
  "live milestones remain at the global roadmap root `docs/roadmap/`" (ADR-archive-terminal-milestones-in-roadmap);
  every other clause of that ledger stands. Goals stay prose without IDs (ADR-roadmap-in-repository is not reopened).

---

- Supersedes in part `ADR-roadmap-and-milestones-ledger`: the global-only milestone and deferred per-namespace roadmap clause and the global-root wording for live milestones. Other clauses remain in force; goals remain prose without IDs.

## 5. Consequences

- **Positive**: a monorepo keeps each package's roadmap beside that package's capabilities and use cases; the global
  roadmap holds the cross-package themes only; `devkit docs list milestone` from a package directory shows that
  package's milestones with the global ones.
- **Negative / Risks**: one more directory per namespace for `RULE-id-convention` and `RULE-spec-format` to walk;
  guidance that says `docs/roadmap/` in several references must say "the milestone's roadmap root". A reader of the
  global roadmap no longer sees every milestone without `--all-namespaces`.
- **Follow-ups**: the local viewer's dashboard and roadmap tab read `docs/roadmap/` only (`CAP-VIEW-repository-viewer`
  4.1 and §5) and stay out of this decision on the user's choice in Planning. While the viewer does not know the
  namespace roots, it omits namespace milestones, renders a global milestone that depends on one as an unknown
  dependency that is never ready, and shows a proposal that belongs to one in no roadmap card; the follow-up is
  `FB-viewer-namespace-roadmap-roots`, triggered when a repository with namespace milestones uses the viewer.

---

## 6. Confirmation

- `RULE-id-convention` tests: a registered namespace milestone at each lifecycle location passes, an unregistered
  `docs/packages/<name>/roadmap/` file is reported, a namespace `_archive/` move is accepted; `RULE-spec-format` tests
  a namespace milestone's status and `created_at`; `test_roadmap.py` accepts `--milestone` naming a namespace
  milestone.
- `CAP-GOV-spec-rules` (Milestone validation contract), `CAP-DOCS-namespaces` 3.4 and `CAP-DLV-proposal-planning`
  restate the clauses above.
