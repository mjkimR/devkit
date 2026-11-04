---
id: PROP-namespace-steering
title: Namespace steering documents checked and listed beside the global ones
summary: "Recognizes docs/packages/<name>/steering/ as steering documents of a registered namespace, checked by the steering rule and listed in the context of the namespace an agent works in, within the bounded-context caps."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-11-04
target_area: governance/
namespace: global
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-monorepo-namespace-support
boundaries:
  owns:
    - packages/devkit-docs/src/devkit_docs/features/governance/usecases/
    - packages/devkit-docs/src/devkit_docs/features/documents/services/
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/
    - packages/devkit-docs/pyproject.toml
    - packages/devkit-docs/tests/
    - packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/
    - packages/devkit-dist/src/devkit_dist/features/distribution/usecases/
    - packages/devkit-dist/src/devkit_dist/features/distribution/models/
    - packages/devkit-dist/tests/
    - packages/devkit-spec/tests/integration/bundles/spec/test_steering_guidance.py
    - docs/capabilities/governance/
    - docs/capabilities/distribution/
    - docs/capabilities/documents/
    - docs/architecture/ARCH-05-2-components.md
    - docs/decisions/2026-11/20261102-steering-documents.md
  excludes:
    - .devkit/managed/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-namespace-steering] Namespace steering documents checked and listed beside the global ones

## 1. Background & Hypothesis

`ADR-steering-documents` chose one flat `docs/steering/` directory and rejected a per-namespace copy because "no
registered namespace needs it today", recording the reopen condition: a registered namespace needs package background
its package glossary cannot hold. `RULE-steering-documents` checks only the root directory ("there is no namespace
copy", `steering_documents.py`), and the `docs` bundle lists one directory in every context through its
`context_documents = "docs/steering"` manifest field (`CAP-DIST-context-and-playbooks`,
`devkit_dist.features.distribution.services.bundles.context_documents`).

The condition is met. g-sandbox keeps `docs/packages/<game>/steering/` for four games, two or three files each:
`product.md` plus world setting and art direction. Nothing rejects these files, but nothing reads them either: they
pass no shape check and never reach an agent's context, so the writing guidance that depends on steering (read the
body before a wording, naming or content decision its summary covers) does not apply to them.

Hypothesis: a namespace steering directory can follow the root contract unchanged (flat, ID-free, `title` and
`summary`, the size caps) and be listed with the same progressive loading, if the list is narrowed to the namespace the
agent works in. `living_path` already maps `docs/packages/<name>/steering/X` to `docs/steering/X`, and
`CAP-DOCS-namespaces` 3.3 already defines the namespace of the current directory, so the selection rule exists; what is
missing is applying it to the steering rule and to context assembly.

## 2. Technical Spike Questions

Settled in Planning; the inventory, measurements and option tables are in `materials/namespace-steering-design.md`,
the decision in `PADR-namespace-steering-directories`.

- **Q1**: How does the steering list stay bounded? The caps stay per directory (`max_files`, default 10, and the
  summary length), and the context lists only the directories the working directory selects by the
  `CAP-DOCS-namespaces` 3.3 default rule: inside a package, the global directory and that namespace's (at most
  `2 × max_files` entries); outside every package, the global directory and every namespace's (at most
  `max_files × (1 + N)`). g-sandbox measures 9 namespace entries, about 2.3 KB, at the root and 2 inside a game.
  `devkit get-context` gains no `--namespace` override: the selection follows the directory the command runs in, as
  `devkit docs list` does, and `-w` counts as the root. What the root lists is the open Planning question q1.
- **Q2**: What declares the namespace directories to `devkit-dist`? A `devkit.context_documents` provider entry
  point: `devkit-dist` asks the installed providers for the extra directories of a declared `context_documents`
  directory, given the project root and the start directory, and lists each with the read rules it already has;
  `devkit-docs` registers the provider that reads `[[tool.docs.namespaces]]` and applies `detect`. `devkit-dist`
  reads no `[tool.docs]` and imports no application package, so `ARCH-05-2-components` holds; the provider loader
  follows the `devkit.config_template` pattern (warn per failed entry, never fail). A manifest glob was rejected
  because it cannot select by a package's source path and would list unregistered directories; a registry read in
  `devkit-dist` because `[tool.*]` passes through unread; a sync-rendered list because the `user` chose run-time reading.
- **Q3**: A namespace steering file MAY hold the package's goals as prose (g-sandbox's `product.md` files already do);
  how a namespace milestone cites them is `PROP-namespace-roadmap`'s decision, which owns the roadmap ADR, and a
  namespace milestone may cite the global goals meanwhile, so neither proposal depends on the other. Package
  glossaries stay at `docs/packages/<name>/glossary.md`; the asymmetry with the root glossary is a recorded follow-up.

## 3. Proposed Design & Impact

- **Rule**: `RULE-steering-documents` checks `docs/packages/<name>/steering/` of each registered namespace as it checks
  `docs/steering/`, one directory at a time: flat, Markdown or `glossary.yaml` only, UTF-8, closed frontmatter within
  4096 bytes, no `id`, `title` and Latin-script `summary`, `max_body_bytes`, `max_files` per directory, `README.md`
  neither checked nor counted; messages name the directory checked. A file under an unregistered
  `docs/packages/<name>/steering/` is not checked, as its other documents are not. The rule iterates
  `docs_roots(registered)` (`devkit_docs.features.documents.services.namespaces`).
- **Listing**: `devkit get-context <bundle>` lists, under `documents`, the files of the declared directory and of the
  directories the `devkit.context_documents` providers return (Q2), each with `path`, `title` and `summary`, merged
  and sorted by path (a namespace file sorts before the root ones). The `devkit-docs` provider lives in
  `devkit_docs.features.documents.services` and is registered in `packages/devkit-docs/pyproject.toml`; it returns the
  namespace mirror of a `docs/`-rooted directory for the namespace `detect` selects, or for every registered namespace
  when it selects none (Q1), and nothing without registered namespaces. A provider failure, `DOCS_CONFIG_INVALID`
  included, is a warning notice and the context lists the declared directory alone.
- **Guidance**: the `docs` bundle's constitution line that names `docs/steering/` also names the namespace
  directory with the same trigger; `living-spec-writing` sends package background there and keeps package glossaries
  where they are; the rule guide names both directories. The `spec` bundle guidance test keeps asserting one
  constitution line naming `docs/steering/`.
- **Decision record**: the "no namespace copy" clause and the rejected namespace-copy option of
  `ADR-steering-documents`, and its rejection of an entry-point provider, are superseded in part by
  `PADR-namespace-steering-directories`; Development writes the pointer. `ARCH-05-2-components` adds the new group to
  the public entry-point names. No new feature edge in `.devkit/architecture.toml`: the provider uses the documents
  feature's existing dependency on `devkit_dist.features.project`, and `devkit-dist` loads it generically.
- **Tests**: rule fixtures with a registered namespace directory (clean, nested file, over cap, missing summary,
  non-Latin title with an English summary) and an unregistered one; `devkit-dist` tests with a provider test double
  (directories merged and sorted, a failing provider warns, an unsafe path is dropped, no provider lists the declared
  directory only), passing without `devkit-docs` and `devkit-agt`; `devkit-docs` provider tests from a package source
  directory, its docs root, the repository root, a directory outside every package, with `-w`, without registered
  namespaces and with a malformed registry.

Expected affected contracts: `CAP-GOV-spec-rules` (3.14), `CAP-DIST-context-and-playbooks` (context documents),
`CAP-DIST-manifest-spec` (Context documents), `CAP-DOCS-namespaces` (3.4, 4.5), `ARCH-05-2-components` (entry-point
groups), `ADR-steering-documents` (superseded in part).

## Planning decisions

- Root steering contract reused unchanged for the namespace directories; caps per directory (Host, within scope).
- Selection by the start directory with no `get-context` option; `-w` counts as the root (Host; the root's list is q1).
- Mechanism: the `devkit.context_documents` provider entry point (`PADR-namespace-steering-directories`).
- Goals as prose in a namespace steering file; citation and the roadmap ADR pointer left to `PROP-namespace-roadmap`;
  package glossaries unchanged (Host, within scope and non-goals).
- The acceptance fixture is a monorepo fixture in this repository: g-sandbox has no `.devkit/config.toml` yet, so no
  namespace is registered there today (assumption recorded for `plan-accept`).
- `dev_effort` stays `medium`: two packages and one new entry-point contract, each covered by existing patterns.

## 4. Lifecycle & Retirement Criteria

Planning settled Q1 to Q3; acceptance and handoff create one feature spec. Completion requires the rule, provider
and context tests above, the synchronized guidance and a monorepo fixture whose `devkit get-context docs` from a
package directory lists that package's steering files beside the global ones and no other package's.

Non-goals: loading steering bodies by default; a steering directory for an unregistered package; moving package
glossaries; changing the root directory's contract or caps; a `--namespace` option on `devkit get-context`; a
namespace copy of `docs/steering/ux-objects.md`.
