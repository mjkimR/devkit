---
id: ADR-namespace-steering-directories
title: Namespace steering directories listed by the working directory's namespace
summary: For a registered namespace that needs package background, we check docs/packages/<name>/steering/ under the root steering contract and list it in a context through a devkit-docs provider selected by the working directory, to keep background visible at bounded cost, accepting one more entry point.
proposal: SPEC-namespace-steering
supersedes: [ADR-steering-documents]
status: accepted
created_at: 2026-11-04
---

# [ADR-namespace-steering-directories] Namespace steering directories listed by the working directory's namespace

- **Status**: Accepted
- **Date**: 2026-11-04
- **Involved Components/Capabilities**: `docs/steering/`, `docs/packages/<name>/steering/`, `CAP-GOV-spec-rules`,
  `CAP-DIST-context-and-playbooks`, `CAP-DIST-manifest-spec`, `CAP-DIST-workspace-ownership`, `CAP-DOCS-namespaces`,
  `CAP-DOCS-document-model`, `ARCH-05-2-components`

---

## 1. Context & Problem Statement

`ADR-steering-documents` keeps project background in one flat `docs/steering/` directory, lists each file's `title`
and `summary` in every agent context through the `docs` bundle's `context_documents` declaration, and rejected a
per-namespace copy because no registered namespace needed one, recording the reopen condition: a registered namespace
needs package background its package glossary cannot hold. It also rejected an entry-point context provider as "beyond
the need" of listing one fixed directory.

The condition is met by a monorepo of independent products (g-sandbox: four games sharing one platform, each with
`docs/packages/<game>/steering/` holding product concept, world setting and art direction; nine files today). Nothing
checks these files and nothing lists them, so the writing guidance that depends on steering does not reach an agent
working on a game. Listing every package's background in every context is the cost the ADR refused; listing only the
background of the package an agent works in needs the namespace registry (`[[tool.docs.namespaces]]`), which
`devkit-docs` owns and `devkit-dist` may neither read (`[tool.*]` passes through unread,
`CAP-DIST-sync-and-transactions`) nor import (`ARCH-05-2-components`). It also needs the working directory, which
`devkit get-context` does not pass to its use case today: the CLI resolves the project root and hands over only that.

---

## 2. Decision Drivers

- Package background reaches the agent working in that package, with the same trigger as the root list.
- Inside a package, the always-loaded cost does not grow with the packages the agent does not work in; at the
  repository root it stays bounded by the rule caps.
- The root steering contract (shape, frontmatter, caps) stays one contract; no new document kind or ID.
- `devkit-dist` keeps no SDD or docs concept and reads no `[tool.*]` table; the registry is read by its owner.
- The list is current at run time, without a sync (`user`, `ADR-steering-documents`).
- A project document or an extension failure never fails a context load, and every failure the agent should know
  about carries a stable code (`ARCH-08-1-agent-output`).

---

## 3. Considered Options

### Directory

- **`docs/packages/<name>/steering/` of each registered namespace, under the root contract** (selected): the
  namespace layer already maps it (`living_path`, `docs_roots`); the rule checks it per directory with the same caps.
  Cons: one more directory per namespace to check; an unregistered package's directory stays unchecked.
- **A section of the package glossary** (rejected): keeps one file per package, but the glossary is a term table, not
  background prose, and nothing lists package glossaries in a context.
- **Root steering files per package** (`docs/steering/<name>-product.md`; rejected): listed today, but every context
  pays for every package and the root `max_files` cap is reached by the second package.

### Selection

- **The namespace of the working directory** (selected): inside a package (its source path or docs root) the context
  lists the global directory and that namespace's, the `CAP-DOCS-namespaces` 3.3 rule `devkit docs list` applies. The
  CLI passes the working directory (`--for <dir>`, else the cwd, else the `-w` root) to the use case beside the
  resolved project root.
- **At the repository root, the global directory plus a hint, with `--for <dir>` for a package's context** (selected
  by the `user`, q1): the other registered namespaces' steering directories appear as path and file count only, and
  an agent requests a package's full list with the option or reads the directory. Cons: a second call for package
  background; one option and one result key more.
- **At the repository root, every namespace's directory** (rejected, q1): the `devkit docs list` default there, but
  up to `max_files × (1 + N)` entries in the usual working directory.
- **At the repository root, the global directory only, no hint** (rejected, q1): the smallest list, but an agent at
  the root does not learn that package background exists.
- **Every namespace always** (rejected): the cost the ADR refused, paid inside a package too.
- **A `--namespace <name>` option on `devkit get-context`** (rejected): a docs concept in the SDD-agnostic CLI, whose
  validation only the registry owner could perform; the option takes a directory instead.

### Mechanism

- **A `devkit.context_documents` provider entry point** (selected): `devkit-dist` asks the installed providers for the
  extra directories of a declared one, given the project root, the working directory and the declared directory, and
  lists each with the read rules it already has; `devkit-docs` registers the provider that applies the namespace
  selection. Cons: package code runs inside each context load; one more public entry-point group; the context result
  needs a `notices` channel for provider failures.
- **A glob in the manifest** (`docs/packages/*/steering`; rejected): lists unregistered directories the rule skips,
  and cannot select by a package's source path without the registry.
- **`devkit-dist` reads `[tool.docs]`** (rejected): breaks the `[tool.*]` pass-through and puts the docs registry
  into the SDD-agnostic package.
- **Sync renders the directories into a managed file** (rejected): stale after a registry edit until the next sync;
  the `user` chose run-time reading.

---

## 4. Decision Outcome

Steering documents of a registered namespace live in `docs/packages/<name>/steering/` under the root contract, and an
agent context lists them by the namespace the working directory selects, through a provider the document system
registers.

- A registered namespace MAY keep steering documents in `docs/packages/<name>/steering/`; `RULE-steering-documents`
  checks that directory as it checks `docs/steering/`: flat, Markdown files only, UTF-8, frontmatter closed within
  4096 bytes, no `id`, a `title`, an English `summary` within `max_summary_length`, a body within `max_body_bytes`,
  `max_files` Markdown files per directory, `README.md` neither checked nor counted. Each directory is checked, and
  its over-cap files reported, only when the run targets a file in it. → `CAP-GOV-spec-rules` 3.14 (MUST), `CAP-DOCS-namespaces` 3.4 (MUST)
- `glossary.yaml` is accepted in the root directory only; a `glossary.md` or `glossary.yaml` in a namespace steering
  directory is reported, the package glossary staying at `docs/packages/<name>/glossary.md` and search synonyms
  being read from the root file only. → `CAP-GOV-spec-rules` 3.14 (MUST)
- A `steering/` directory of an unregistered `docs/packages/<name>/` is neither checked nor listed, as its other
  documents are plain `docs/` files. → `CAP-GOV-spec-rules` 3.14 (MUST)
- `RULE-document-reference` checks the IDs cited in a namespace steering file as it checks those of the root
  directory. → `CAP-GOV-spec-rules` `RULE-document-reference` (MUST)
- The caps are per directory and stay rule settings; `devkit-dist` caps nothing itself. → `CAP-GOV-spec-rules` 3.14 (MUST)
- `devkit get-context <bundle>` passes the working directory to its use case beside the resolved project root: the
  `--for <dir>` option (an existing directory inside the project; otherwise `ARGUMENT_INVALID`), else the cwd, else the
  `-w` root. It lists, for a bundle declaring `context_documents`, the declared directory and the directories the
  installed `devkit.context_documents` providers return to list for the project root, the working directory and the
  declared directory, each with the existing read rules, de-duplicated and sorted by path; entries keep `path`,
  `title` and `summary`. The directories the providers return to mention appear under `documents_elsewhere`, each as
  the absolute `path` and `files` (the count of Markdown files other than `README.md`), existing directories only,
  sorted by path, `[]` when none. → `CAP-DIST-context-and-playbooks` 2 (MUST), `CAP-DIST-manifest-spec` Context documents (MAY)
- A provider that fails to load, raises or returns anything but safe workspace-relative directories never fails the
  context load: the context lists the declared directory alone, the JSON object carries the warning under `notices`
  and stderr carries the advisory block `CONTEXT_DOCUMENTS_EXTENSION_FAILED` naming the entry point; the exit code is
  `0`, `1` under `--strict`. `devkit-dist` reads no `[tool.docs]` and imports no application package for it. → `CAP-DIST-context-and-playbooks` 2 (MUST), `ARCH-05-2-components` entry-point groups
- The `devkit-docs` provider, for a `docs/`-rooted declared directory, returns to list the namespace mirror of the
  namespace the working directory selects (`CAP-DOCS-namespaces` 3.3, rule 3) and to mention the other registered
  namespaces' mirrors; when the working directory selects none, nothing to list and every registered namespace's
  mirror to mention; nothing without registered namespaces or for another directory. → `CAP-DOCS-namespaces` 3.3 and 4.5 (MUST)
- A declared context document directory and a provider directory alike may list seeded and project files.
  → `CAP-DIST-workspace-ownership` 7 (MAY)
- The `docs` bundle's constitution line names both directories with the same read-before-deciding trigger and tells
  the agent to request a package's context with `--for <dir>` when `documents_elsewhere` names it; the glossary row
  **Steering document** and `CAP-DOCS-document-model` rule 9 name both directories. → `CAP-DOCS-document-model` 9
- A namespace steering file MAY hold the package's goals as prose; how a namespace milestone cites them is
  `SPEC-namespace-roadmap`'s decision. Package glossaries stay at `docs/packages/<name>/glossary.md`.
- Replaces in `ADR-steering-documents`: the Directory clause "no subdirectories and no namespace copy" and its
  rejected option "A per-namespace copy as well" (a registered namespace may now keep one); the Listing mechanism's
  rejection of an entry-point provider as beyond the need (a provider now supplies the namespace directories beside
  the manifest-declared one, which stays). Every other clause stands.
- The provider is selected over the glob and the registry read because only the registry owner can select by a
  package's source path, and the pattern already exists for `devkit.config_template` and `devkit.docs.status_overlay`.

---

## 5. Consequences

- **Positive**:
  - Package background reaches the agent working in that package at about 260 bytes per file; the root list is unchanged.
  - One contract and one rule for every steering directory; a project tunes `max_files` once.
  - A generic way for any bundle's context documents to gain namespace-selected directories.
- **Negative / Risks**:
  - Every context lists at most `2 × max_files` entries plus one hint line per other registered namespace; package
    background at the repository root costs a second call (`--for <dir>`), which the hint and the constitution line
    trigger. Both bounds are asserted by tests.
  - Provider code runs in every context load; a `DOCS_CONFIG_INVALID` registry degrades the list to the root directory
    with a `CONTEXT_DOCUMENTS_EXTENSION_FAILED` warning instead of failing; `devkit rules check` reports the registry itself.
  - Steering files of an unregistered package are silently plain files until the package is registered.
  - `GetContext.execute` gains a parameter and `devkit get-context` an option and a result key; the use case's only
    production caller is the CLI.
- **Follow-ups**:
  - A namespace copy of `docs/steering/ux-objects.md` for the UX rules work of `MS-monorepo-namespace-support`.
  - The asymmetry between the root glossary (`docs/steering/glossary.md`) and package glossaries
    (`docs/packages/<name>/glossary.md`); namespace search synonyms.

---

## 6. Confirmation

`RULE-steering-documents` fixtures with a registered namespace directory (clean, nested file, over cap, missing
summary, non-Latin title with an English summary, a `glossary.md`, an over-cap root with an untargeted namespace
directory) and an unregistered one; `RULE-document-reference` fixtures with an alias ID cited in a namespace steering
file; `devkit-dist` tests for the provider contract with a test double (a nested working directory and `--for <dir>`
reach the provider, `--for` outside the project or a non-directory is `ARGUMENT_INVALID`, listed directories merged
and sorted, mentioned directories under `documents_elsewhere` with their counts, a failing provider yields `notices`
and exit `0`, an unsafe path is dropped, no provider lists the declared directory only with `documents_elsewhere`
empty, the `documents` payload at the default caps stays within `2 × 4096` bytes and `documents_elsewhere` within `N`
entries for a fixture of `N` namespaces), passing without `devkit-docs` and `devkit-agt` (`just test-dist`);
`devkit-docs` tests for the provider from a package source directory, its docs root, the repository root, a directory
outside every package, with `--for` and a workspace without namespaces; the `spec` bundle guidance test keeps one
constitution line naming `docs/steering/`; a monorepo fixture whose `devkit get-context docs` from a package directory
(and from the root with `--for`) lists that package's steering files beside the global ones and no other package's,
names the others under `documents_elsewhere`, and from the root without `--for` lists the global ones only.
