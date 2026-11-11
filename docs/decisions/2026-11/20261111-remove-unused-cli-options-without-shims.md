---
id: ADR-remove-unused-cli-options-without-shims
title: Remove unused CLI options without compatibility shims
summary: "For CLI options no documented workflow or caller uses, we remove them outright so they become unknown options, to keep help, references and tests limited to options that change behavior, accepting that an undocumented caller passing one now gets a usage error."
proposal: SPEC-remove-unused-cli-options
supersedes:
  - ADR-single-local-landing-route
status: accepted
created_at: 2026-11-11
---

# [ADR-remove-unused-cli-options-without-shims] Remove unused CLI options without compatibility shims

- **Status**: Accepted
- **Date**: 2026-11-11
- **Deciders**: user
- **Involved Components/Capabilities**: `CAP-WT-task-worktrees`, `CAP-DLV-cli-and-output`,
  `CAP-DLV-workflow-definitions`, `CAP-DOCS-document-lookup`, `devkit_agt.features.worktree`,
  `devkit_agt.features.rules`, `devkit_agt.features.workflow`, `devkit_dist.features.host`,
  `devkit_docs.features.documents`

---

## 1. Context & Problem Statement

Six options are accepted but unused by any documented workflow, bundle guidance, script or caller:
`worktree finish --local-only` (a no-op since `finish --merge` was retired), `host status --host` (one supported
value), `rules check|fix --summary-only`, `workflow next --workflow` (evaluation against another definition than the
binding), `workflow handoff --date` (a back-dated history entry) and `docs list --query` (what `docs search` does).
Each one costs help text an agent reads, reference and contract text and tests. `ADR-single-local-landing-route` kept
`--local-only` accepted only because guidance still named it.

devkit's only external consumers are `devkit.advisory` and the `devkit-cli` package; neither passes these options.

---

## 2. Decision Drivers

- The command surface an agent reads holds only options that change behavior.
- No published compatibility contract is broken.
- No dormant code path is kept for a caller that does not exist.

---

## 3. Considered Options

### Option 1: Remove the options outright (Selected)
- **Overview**: the options, their parameters and their documentation go; passing one is a click usage error.
- **Pros**: smallest surface; nothing left to maintain.
- **Cons**: an undocumented script passing one fails with exit `2` instead of continuing.

### Option 2: Hide the options and warn for one release
- **Cons**: keeps the code and tests for callers that do not exist.

### Option 3: Keep the options
- **Cons**: keeps no-op and duplicate options in help and references.

---

## 4. Decision Outcome

We decided to adopt **Option 1**.

- Unused CLI options are removed without a shim, hidden alias or deprecation period when no external consumer
  passes them; a removed option is an unknown option (exit `2`).
- `devkit worktree finish` has no `--local-only` option and makes no fetch, push or `ls-remote` call.
  → `CAP-WT-task-worktrees` §3 (MUST)
- `devkit host status` inspects the one supported host and has no `--host` option; the hidden `host hook --host`
  stays because generated hook commands pass it.
- `devkit rules check` and `fix` have no `--summary-only` option.
- `devkit workflow next` evaluates the unit against its binding (or the configured default) and has no `--workflow`
  option; `bind --workflow` changes the binding. → `CAP-DLV-workflow-definitions` binding (MUST)
- `devkit workflow handoff` records the day it runs in the history and has no `--date` option.
  → `CAP-DLV-cli-and-output` §1
- `devkit docs list` has no `--query` filter; ID and title lookup is `devkit docs search`.
  → `CAP-DOCS-document-lookup` list filters
- Option 1 best satisfies all three drivers because no external consumer passes any of the options.

Supersedes in part `ADR-single-local-landing-route`: the clause that `--local-only` stays accepted, and the follow-up to retire the no-op `--local-only` flag. All other decisions remain in force.

---

## 5. Consequences

- **Positive**: help, references and tests carry six fewer options; guidance names one cleanup command.
- **Negative / Risks**: a caller outside the repository passing a removed option gets a usage error.
- **Follow-ups**: none.

---

## 6. Confirmation

- `packages/devkit/tests/integration/features/worktree/test_cli.py`,
  `packages/devkit-dist/tests/integration/features/host/test_hooks.py`,
  `packages/devkit/tests/integration/features/rules/cli/test_commands.py`,
  `packages/devkit/tests/integration/features/workflow/test_handoff.py`,
  `packages/devkit/tests/integration/features/workflow/test_layouts_and_authoring.py` and
  `packages/devkit-docs/tests/integration/features/documents/test_cli_documents.py`: each removed option is refused
  with exit `2`.
- Restating documents: `CAP-WT-task-worktrees`, `CAP-DLV-workflow-definitions`, `CAP-DLV-cli-and-output`,
  `CAP-DOCS-document-lookup`.
