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
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/
    - packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/
    - packages/devkit-dist/src/devkit_dist/features/distribution/usecases/
    - docs/capabilities/governance/
    - docs/capabilities/distribution/
    - docs/capabilities/documents/
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

- **Q1**: How does the steering list stay bounded? The root cap is `max_files` 10 so that every context carries at most
  ten lines. Candidates: list the global directory plus the current directory's namespace (the `docs list` default
  selection), with the same caps per directory; or list every namespace and raise the cap. Planning weighs the
  per-context cost against an agent working across packages, and whether `devkit get-context` needs a
  `--namespace`-like override or derives the namespace from the working directory only.
- **Q2**: What declares the namespace directories to devkit-dist, which imports no application package and reads no
  `[tool.docs]` registry? Candidates: the `context_documents` field accepts a namespace-aware pattern resolved against
  the registry devkit-docs exposes; or devkit-docs contributes the directories through an existing extension point.
  Planning confirms the `devkit-dist` layering rule (`ARCH-05-2-components`) is kept.
- **Q3**: Does a namespace steering directory hold the package's goals for `PROP-namespace-roadmap` (a namespace
  milestone cites a goal), and does the glossary split (`docs/packages/<name>/glossary.md` stays where it is) change?

## 3. Proposed Design & Impact

- **Rule**: `RULE-steering-documents` checks `docs/packages/<name>/steering/` of each registered namespace as it checks
  `docs/steering/`: flat, Markdown or `glossary.yaml` only, UTF-8, closed frontmatter within 4096 bytes, no `id`,
  `title` and Latin-script `summary`, `max_body_bytes`, `max_files` per directory, `README.md` neither checked nor
  counted. A file under an unregistered `docs/packages/<name>/steering/` is not checked, as its other documents are not.
- **Listing**: `devkit get-context <bundle>` lists, under `documents`, the global steering files and those of the
  namespace the working directory selects (Q1), each with `title` and `summary`; the constitution line that names
  `docs/steering/` also names the namespace directory.
- **Decision record**: the "no namespace copy" clause and the rejected option of `ADR-steering-documents` are
  superseded in part by the PADR this proposal records; Development writes the pointer.
- **Tests**: rule fixtures with a registered namespace directory (clean, nested file, over cap, missing summary) and an
  unregistered one; context tests for the selection from a package directory, from the repository root and from a
  directory outside every package.

Expected affected contracts: `CAP-GOV-spec-rules` (3.14), `CAP-DIST-context-and-playbooks` (context documents),
`CAP-DOCS-namespaces` (what a namespace mirrors), `ADR-steering-documents` (superseded in part).

## 4. Lifecycle & Retirement Criteria

Planning settles Q1 to Q3; acceptance and handoff create one feature spec. Completion requires the rule and context
tests, the synchronized guidance and a monorepo fixture whose `devkit get-context docs` from a package directory lists
that package's steering files beside the global ones and no other package's.

Non-goals: loading steering bodies by default; a steering directory for an unregistered package; moving package
glossaries; changing the root directory's contract or caps.
