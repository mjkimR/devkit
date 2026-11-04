---
id: SPEC-namespace-steering
title: Namespace steering documents checked and listed beside the global ones
summary: Recognizes docs/packages/<name>/steering/ as steering documents of a registered namespace, checked by the steering rule and listed in the context of the namespace an agent works in, within the bounded-context caps.
status: completed
created: 2026-11-04
namespace: global
related_capabilities:
  - CAP-GOV-spec-rules
  - CAP-DIST-context-and-playbooks
  - CAP-DIST-manifest-spec
  - CAP-DIST-workspace-ownership
  - CAP-DOCS-namespaces
  - CAP-DOCS-document-model
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-namespace-steering] Namespace steering documents checked and listed beside the global ones

## 1. Problem Statement & Motivation

Handed off from proposal PROP-namespace-steering on 2026-11-04; the direction is `ADR-namespace-steering-directories`
and the inventory, measurements and option tables are in
`docs/materials/2026-11/20261104-namespace-steering/namespace-steering-design.md`.

`ADR-steering-documents` keeps project background in one flat `docs/steering/` directory, listed by `title` and
`summary` in every agent context through the `docs` bundle's `context_documents` declaration, and rejected a
per-namespace copy until a registered namespace needs package background its package glossary cannot hold. That
condition is met by a monorepo of independent products keeping `docs/packages/<name>/steering/` per package. Today
`RULE-steering-documents` checks only the root directory, `RULE-document-reference` resolves the IDs cited in the root
files only, and `devkit get-context` lists one directory whatever the working directory, so package background passes
no shape check and never reaches the agent working on that package.

The namespace layer already supplies the selection rule (`CAP-DOCS-namespaces` 3.3: the namespace of the working
directory) and the path mapping (`living_path`, `docs_roots`). This spec applies them to the steering rule, the
reference rule and context assembly, through a `devkit.context_documents` provider so that `devkit-dist` reads no
`[tool.docs]` table and imports no application package (`ARCH-05-2-components`).

## 2. User Stories

- **US-1**: As an agent working inside a package of a monorepo, I want `devkit get-context docs` to list that
  package's steering files beside the global ones, so that the read-before-deciding trigger covers package background.
- **US-2**: As an agent at the repository root, I want the context to name the packages that keep steering
  directories and a way to request one package's context without changing directory, so that package background is
  discoverable at bounded cost.
- **US-3**: As a maintainer of a registered namespace, I want `devkit rules check` to hold my steering directory to
  the root contract and to resolve the IDs it cites, so that the always-loaded list stays short and current.
- **US-4**: As a maintainer of `devkit-dist`, I want a failing or misbehaving provider to degrade the context to the
  declared directory with a coded warning, so that a project document or extension never fails a context load.

## 3. Non-Goals

1. **Scope Excluded**: loading steering bodies by default; a steering directory for an unregistered
   `docs/packages/<name>/`; moving package glossaries from `docs/packages/<name>/glossary.md`; changing the root
   directory's contract or caps; a `--namespace` option on `devkit get-context` (the option takes a directory);
   titles or summaries in the `documents_elsewhere` hint; a namespace copy of `docs/steering/ux-objects.md`;
   namespace search synonyms (`glossary.yaml` is read from the root directory only); a mechanical citation of
   namespace goals from a namespace milestone (`SPEC-namespace-roadmap` owns the roadmap ADR).
2. **Scope Excluded**: a new feature edge in `.devkit/architecture.toml`. The provider lives in the `documents`
   feature of `devkit-docs`, which already depends on `devkit_dist.features.project`; `devkit-dist` loads it
   generically through the entry point.

## 4. Acceptance Criteria & Behavioral Contracts

The namespace steering directory of a registered namespace `<name>` is `docs/packages/<name>/steering/`, the mirror
of `docs/steering/` under `living_path`. "Registered" means listed in `[[tool.docs.namespaces]]` of
`.devkit/config.toml`. Fixtures below use the rule test harness (`check(RULE, root, files, targets=...)`) and
`devkit get-context` through the CLI or `GetContext.execute`.

### [AC-01] The steering rule checks a registered namespace directory under the root contract
- **Given** a workspace registering namespace `api` (source path `packages/api`) with `docs/packages/api/steering/`
  holding a well-formed `product.md` (`title`, English `summary`, no `id`) and a `README.md`
- **When** `RULE-steering-documents` runs targeting `docs/packages/api/steering/product.md`
- **Then** it reports no violation; a Korean `title` with an English `summary` also passes; and each of a nested
  file (`docs/packages/api/steering/sub/a.md`), a non-Markdown file, an `id` key, a missing `title`, a missing or
  non-Latin `summary`, an oversized body and an eleventh Markdown file at the default caps is reported with the same
  message as in the root directory, the message naming `docs/packages/api/steering/` where the root message names
  `docs/steering/` (for example `docs/packages/api/steering/ has 11 Markdown files; at most 10 are allowed`).

### [AC-02] Glossary files in a namespace steering directory are reported
- **Given** namespace `api` registered, `docs/packages/api/steering/glossary.md` and
  `docs/packages/api/steering/glossary.yaml`
- **When** the rule runs targeting both files
- **Then** `glossary.md` is reported at line 1 with a message naming `docs/packages/api/glossary.md` as the place of
  the package glossary, `glossary.yaml` is reported at line 1 as not allowed in a namespace steering directory
  (synonyms are read from `docs/steering/glossary.yaml` only), neither counts toward `max_files`, and a root
  `docs/steering/glossary.yaml` stays accepted.

### [AC-03] Caps and targeting apply per directory; an unregistered directory is skipped
- **Given** `docs/steering/` holding 11 Markdown files, namespace `api` registered with
  `docs/packages/api/steering/` holding 11 Markdown files, and `docs/packages/other/steering/` of an unregistered
  `other` holding a file without frontmatter
- **When** the rule runs targeting only `docs/steering/topic-00.md`
- **Then** exactly one violation is reported, the root over-cap file, and none under `docs/packages/api/steering/`;
  **and when** it runs targeting only `docs/packages/api/steering/topic-00.md`, exactly one violation is reported,
  under `docs/packages/api/steering/`; **and when** it runs targeting `docs/packages/other/steering/a.md` alone,
  nothing is reported.

### [AC-04] The reference rule resolves the IDs cited in a namespace steering file
- **Given** namespace `api` registered, a document with the fixture ID CAP-A-one and the alias CAP-A-old, and
  `docs/packages/api/steering/product.md` citing CAP-A-old and CAP-A-missing in code spans
- **When** `RULE-document-reference` runs targeting that steering file, then runs with `fix=True`
- **Then** the first run reports the alias as fixable ("CAP-A-old is an alias of CAP-A-one; name CAP-A-one") and the
  missing ID as not fixable, at their lines; the fix rewrites only the alias code span to CAP-A-one, leaves the
  missing ID, and a second fix changes no file. The steering file is not indexed as a document.

### [AC-05] The context lists provider directories merged with the declared one and names the mentioned ones
- **Given** a synchronized bundle declaring `context_documents = "docs/steering"`, `docs/steering/{a,b}.md`,
  `docs/packages/api/steering/z.md`, `docs/packages/web/steering/{c,d}.md` plus a `README.md`, and a registered
  `devkit.context_documents` provider returning `(["docs/packages/api/steering"], ["docs/packages/web/steering",
  "docs/packages/gone/steering"])` for the call
- **When** `devkit get-context <bundle>` runs
- **Then** exit code is `0`; `documents` holds `docs/packages/api/steering/z.md` first, then `a.md` and `b.md`,
  each with `path`, `title` and `summary` under the existing read rules and no duplicate; `documents_elsewhere`
  is `[{"path": "<abs>/docs/packages/web/steering", "files": 2}]` (`README.md` not counted; the absent
  `gone` directory dropped); and without any registered provider `documents` holds the declared directory's
  files only and `documents_elsewhere` is `[]`.

### [AC-06] The working directory reaches the provider: `--for`, the cwd, else the root
- **Given** the fixture of AC-05 and a provider that records its `(root, working, directory)` arguments
- **When** the CLI runs with `--for packages/api` from the project root, then from the subdirectory `packages/api`
  without `--for`, then with `-w <root>` from a directory outside the project
- **Then** the provider receives `(root, root/packages/api, "docs/steering")`, then `(root, root/packages/api,
  "docs/steering")`, then `(root, root, "docs/steering")`; `--for` naming a directory outside the project, a
  file, or a missing path exits `2` with `ARGUMENT_INVALID` targeting `--for` before any provider runs; and
  `GetContext.execute(start, bundle)` without a working directory behaves as `--for <root>`.

### [AC-07] A provider failure degrades the context to the declared directory with a coded warning
- **Given** the fixture of AC-05 and a provider that raises, or one that returns `(["../up"], [])`, or one whose
  entry point does not load
- **When** `devkit get-context <bundle>` runs, then runs with `--strict`
- **Then** stdout is one JSON object whose `documents` holds the declared directory's files only,
  `documents_elsewhere` is `[]` and `notices` holds one entry per failed provider with code
  `CONTEXT_DOCUMENTS_EXTENSION_FAILED` naming the entry point, with its directive text (the command is JSON-only, so
  stderr carries no advisory, `ARCH-08-1-agent-output`); the exit code is `0`, and `1` under `--strict`. A working provider beside a failing one is still listed. The
  `devkit-dist` tests of AC-05 to AC-07 pass with `devkit-docs` and `devkit-agt` absent (`just test-dist`).

### [AC-08] The `devkit-docs` provider selects by the working directory's namespace
- **Given** `[[tool.docs.namespaces]]` registering `api` (`packages/api`) and `web` (`apps/web`), with
  `docs/packages/api/steering/` and `docs/packages/web/steering/` present
- **When** the provider is called for `docs/steering` with the working directory `packages/api/src`, then
  `docs/packages/api`, then the repository root, then `tools/other`
- **Then** it returns `(["docs/packages/api/steering"], ["docs/packages/web/steering"])` for the first two calls and
  `([], ["docs/packages/api/steering", "docs/packages/web/steering"])` for the last two; for a declared directory
  not under `docs/` or in a workspace without registered namespaces it returns `([], [])`; and a malformed registry
  raises `DOCS_CONFIG_INVALID`, which `devkit get-context` reports as the AC-07 warning with exit code `0`.

### [AC-09] A monorepo fixture is listed end to end through the installed provider
- **Given** a project synchronized with the `docs` bundle, `N = 2` registered namespaces `api` and `web` each with
  10 steering files at the default caps (60-character titles, 300-character summaries) and `docs/steering/` with 10
- **When** `devkit get-context docs` runs from `packages/api`, then from the root with `--for packages/api`, then
  from the root without `--for`
- **Then** the first two runs list the 10 `api` files before the 10 root files and no `web` file, with
  `documents_elsewhere` naming `docs/packages/web/steering` with `files: 10`; the third lists the 10 root files only
  with `documents_elsewhere` naming both namespace directories; in every run the `documents` payload without its
  `path` values is at most `2 × 4096` bytes and `documents_elsewhere` has at most `N` entries.

### [AC-10] The guidance names both directories and the `--for` request
- **Given** the `docs` bundle sources
- **When** the bundle guidance tests run
- **Then** the constitution holds exactly one list item naming `docs/steering/`, and that item also names
  `docs/packages/<name>/steering/`, `documents_elsewhere` and `--for`; `living-spec-writing` sends package
  background to the namespace steering directory and keeps package glossaries at
  `docs/packages/<name>/glossary.md`; the `RULE-steering-documents` guide names both directories and the glossary
  findings of AC-02; and the `spec` bundle test asserting one constitution line naming `docs/steering/` passes.

## 5. Assumptions

- A provider's whole result is rejected, with one `CONTEXT_DOCUMENTS_EXTENSION_FAILED` warning, when any returned
  item is not a safe workspace-relative directory in the seeded `target` grammar; the declared directory is still
  listed (the decision's "returns anything but safe workspace-relative directories").
- The provider contract: a callable registered under `devkit.context_documents`, called with the project root, the
  working directory (both absolute `Path`s) and the declared directory (workspace-relative), returning a pair of
  sequences of workspace-relative directories, the first to list and the second to mention. The exact signature and
  the result types are fixed in `PLAN-namespace-steering`.
- The default working directory is computed by the CLI: the cwd when it lies inside the resolved project root, else
  the root; the use case validates only an explicit `--for` value. `GetContext.execute` keeps its two positional
  parameters and gains an optional third, so the MCP and test callers are unchanged.
- The acceptance fixture is a monorepo fixture in this repository's tests (g-sandbox registers no namespace yet).
- `ADR-namespace-steering-directories` and the "Superseded in part" pointer in `ADR-steering-documents` were written
  by the handoff; Development changes neither decision and adds the `ARCH-05-2-components` entry-point group name.
