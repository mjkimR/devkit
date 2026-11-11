---
id: SPEC-small-helper-consolidations
title: Consolidate the remaining duplicated runtime helpers
summary: 'Consolidates three deferred duplicates without changing behavior or projected bytes: a public devkit-cli UTF-8 output helper, subagent projection quoting through the shared frontmatter scalar, and shared Git tracked/ignored probes in devkit-core.'
status: planned
created: 2026-11-11
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-small-helper-consolidations] Consolidate the remaining duplicated runtime helpers

## 1. Problem Statement & Motivation

Handed off from proposal PROP-small-helper-consolidations on 2026-11-11.
- **Preserved Materials**: `docs/materials/2026-11/20261111-small-helper-consolidations`

### 1. Background & Hypothesis

Three small duplicates were deferred by the code pass (`docs/materials/2026-11/20261111-review-refactor-code-pass/report.md`):
- X-13: `_utf8_output` is copied from devkit-cli (`devkit_cli.boundary`) into devkit-dist (`devkit_dist.features.host.cli`, the hidden `devkit host hook` command, which bypasses `@boundary` because its stdout follows the host's native protocol).
- DS-09: subagent projection hand-rolls YAML quoting (`_yaml_quote`, `_yaml_scalar`, `_yaml_value` in `devkit_dist.features.distribution.services.bundles.subagents`) beside the shared `devkit_core.core.frontmatter.scalar`.
- DS-10: devkit-dist asks Git whether paths are tracked or ignored in four places (host registrations, shared storage, the local render check and projection Git notices), plus a tracked-only check in sync.

Hypothesis: each duplicate can have one owner with every caller's options kept, so no behavior, contract or projected byte changes. Evidence: `docs/materials/2026-11/20261111-small-helper-consolidations/planning-evidence.md`.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Consolidate the remaining duplicated runtime helpers so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- **Q1** (settled): devkit-dist depends on a new public devkit-cli helper. devkit-dist already pins and imports devkit-cli; moving the helper to devkit-core would add a devkit-cli -> devkit-core dependency, which `CAP-CLI-agent-cli-toolkit` excludes (devkit-cli depends on click and devkit-advisory only).
- **Q2** (settled): no projected byte change. Using `scalar` as it is would turn every `description` plain (11 of 11 Claude Code projections here) and `"off"` into `'off'` (devkit-adaptive `swarm-planner`), and a plain description breaks the `CAP-DIST-agent-projections` rule that it is a quoted scalar. A double-quote option on `scalar` reproduces today's bytes for every shipped contract.
- **Q3** (settled): the probes differ in ignore mode (index-aware in host registrations and shared storage, `--no-index` in the local render check and projection notices), in the deadline (shared storage) and in failure mapping (each caller's own). These stay per caller; the shared helpers take them as arguments or leave them to the caller.

### 3. Proposed Design & Impact

#### Planning decisions

1. **X-13**: `devkit_cli` exports a public `utf8_output()` (the current `_utf8_output` body and docstring); `Boundary` calls it, and `devkit_dist.adapters.cli` re-exports it beside the other `devkit_cli` names, where `devkit host hook` imports it. The devkit-dist copy is removed. The new name is added to the public-name pin in `packages/devkit-cli/tests/integration/test_lazy_and_package.py`; an added name changes the shipped payload, so devkit-cli takes the shared release version (`CAP-CLI-agent-cli-toolkit` rule 10), with no minor bump of its own.
2. **DS-09**: `devkit_core.core.frontmatter.scalar` gains keyword-only options for the quote character used when quoting is needed (`'` by default, `"` for projections) and for always quoting; its current default output is unchanged. Subagent projection renders `description` always double-quoted and `name`, settings and list items with the double quote when quoting is needed; `_yaml_quote`, `_yaml_scalar` and `_YAML_PLAIN`/`_YAML_RESERVED` are removed. Projected bytes stay identical for every shipped role contract; the only new output is that NEL, LS, PS and other non-printable characters in a description are escaped (PyYAML double style), where the hand-rolled quoter wrote them raw. The Codex TOML quoter (`_toml_string`) is out of scope.
3. **DS-10**: `devkit_core.core.git` gains `tracked_paths(cwd, paths, *, deadline=None) -> set[str]` (the given paths that are tracked or hold tracked files, one `ls-files -z` call with literal pathspecs) and `ignored_paths(cwd, paths, *, no_index=False, deadline=None) -> set[str]` (one `check-ignore --stdin -z` call; exit 1 is the empty set, any other failure raises `GitError`). The five sites use them and keep their own ignore mode, deadline and failure mapping (host registrations: a failure means not ignored; shared storage: `ExclusionError`; local render: `GitError` raised; projection notices: the exit-128 skip and the failure notice). Shared storage's `ls-files --others --exclude-standard` query is a different question and stays. Shared storage's trailing-slash directory check keeps passing `.devkit/.shared/`.
4. No feature edge and no package dependency is added: the helpers live in `devkit_cli` (already a devkit-dist dependency) and `devkit_core.core` (imported by every site already). No PADR: none of the three decisions meets the decision-writing admission criteria.

#### Acceptance outline

- A test of `devkit_cli.utf8_output` covers the UTF-8 `backslashreplace` reconfiguration and a closed stream; the `devkit host hook` and boundary tests pass unchanged.
- A projection test renders every shipped role contract (or the repository's `devkit sync --dry-run`) with no byte change; `scalar` keeps its current output by default; a description with a line break, a control character and `off` as a setting value keep today's bytes.
- `tracked_paths`/`ignored_paths` tests cover tracked directories, index-aware versus `--no-index` on a tracked ignored path, exit 1, a non-repository failure and a glob character in a path; the existing tests of the five sites pass unchanged.

#### Living Spec impact

- `CAP-CLI-agent-cli-toolkit` section 4 (the `devkit_cli` public-name table) and `packages/devkit-cli/README.md` list `utf8_output()`.
- `docs/development/reference/core.md`: the `devkit_core.core.frontmatter` (`scalar` options), `devkit_core.core.git` (the two helpers) and `devkit_dist.adapters.cli` (re-export) rows.
- `CAP-DIST-agent-projections` is unchanged: its quoted-description rule keeps holding.

### 4. Lifecycle & Retirement Criteria

<!--
- Preliminary decisions: devkit spec proposal padr small-helper-consolidations "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept small-helper-consolidations --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff small-helper-consolidations.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->

