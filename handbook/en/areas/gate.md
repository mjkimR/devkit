---
sources:
  CAP-GATE-commit-gates: 83c1bd822d3330dab5eed84e7b8f13a552e5f638
  UC-keep-the-living-spec-consistent: 7ebdf1e2f7ae6581fa9140d1898d755de57b5667
title: Commit gates
---

# Commit gates

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `c94b6a08710e`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Incubate and hand off a proposal](../journeys/incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
- [Advisories](advisory.md)
- [Agent-first CLI toolkit](cli.md)
- [Collaboration](collaboration.md)
- [Compact command output](compact.md)
- [Delivery](delivery.md)
- [Distribution](distribution.md)
- [Documents](documents.md)
- [Generated Files](generated.md)
- [Governance rules](governance.md)
- [Harness](harness.md)
- [Host](host.md)
- [Integration](integration.md)
- [MCP](mcp.md)
- [Search](search.md)
- [Traceability](traceability.md)
- [Viewer](viewer.md)
- [Worktree](worktree.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

Commit gates run policy at Git's `pre-commit`, `commit-msg` and `post-commit` hooks. devkit owns the system (hook
dispatchers, configuration layers, discovery, the stage runner); the policy itself ships in bundles as
`kind = "gate"` assets, the same way rules do. Selecting a bundle and running `devkit sync` adds its gates; no
per-gate install step exists. Gates are one of the checks that keep work honest without relying on the agent's
memory; see [Concepts](../concepts.md).

## Get the hooks in place

You usually do nothing: every writing `devkit sync` installs the dispatchers through its `gate-hooks` post-sync
extension. To install or inspect by hand:

| You want to | Run |
| --- | --- |
| Install or repair the hooks and the settings template | `devkit gate install` |
| See every gate, its effective state and what would fail a commit | `devkit gate status` |
| Remove devkit's hook entries and restore moved hooks | `devkit gate uninstall` |
| Run one stage by hand, as the hook does | `devkit gate run pre-commit` |

Hooks live in the common Git directory, so every worktree of a clone shares them. Each stage gets a small
dispatcher that runs the executable files in `<hook>.d/` in name order; devkit's entry is `20-devkit`, and your own
scripts can sit before or after it (`10-custom-check`, `30-custom-check`). An existing hook is moved to
`<hook>.legacy` and chained through `00-legacy`, with a `GATE_HOOK_PRESERVED` warning.

If `core.hooksPath` points elsewhere, devkit leaves it alone and `devkit gate status` warns with
`GATE_HOOKS_PATH_SET` that your enabled gates do not run. After enabling a gate in a stage with no entry yet, run
`devkit sync` again; until then status reports `GATE_HOOK_ENTRY_MISSING`.

## What runs on every commit

Three gates are built in, all on by default:

| Gate | Stage | What it does |
| --- | --- | --- |
| `rules-check` | `pre-commit` | Runs `devkit rules check --staged` on the commit and refuses on error-severity violations (`GATE_RULES_FAILED`) |
| `verify-commands` | `pre-commit` | Runs the project's own verification commands and refuses when one fails (`GATE_VERIFY_FAILED`) |
| `message-nonempty` | `commit-msg` | Refuses a blank message |

`rules-check` evaluates exactly what is being committed, so unstaged edits cannot hide or cause a finding. Tune the
rules it evaluates in `[rules]`, not the gate; see [Governance rules](governance.md).

`verify-commands` needs your commands:

```toml
# .devkit/config.toml
[gates.settings.verify-commands]
commands = ["just lint-check", "just check"]
```

Hooks run with Git's environment, where `.venv/bin` is usually not on `PATH`, so call tools through `uv run` or
`just`. Every command runs even after a failure, through devkit's bounded runner, so one refusal lists every failing
command with its log path (see [Compact command output](compact.md)). The commands see the working tree, not the
index; when they could differ, a `GATE_VERIFY_UNSTAGED` note says so. Keep the list to quick checks and leave slow
suites to CI.

## Read a refusal

Every refusal is an Agent Advisory Protocol error ([Advisories](advisory.md)), so the code tells you and your agent
what kind of problem it is:

- `BLOCKED` (exit `1`): a gate ran and refused. Fix the cause, then commit again; changing the policy is the user's
  decision.
- `AUTO` (exit `2`): the gates could not judge, and one fix covers it, usually `devkit sync` in a fresh worktree or
  clone whose managed rule files are missing (`RULES_RUN_FAILED`, `GATE_VERIFY_NOT_RUN`).
- Setup errors (exit `2`): the gate setup itself is broken and the error's `[FIX]` names the repair, for example
  `GATE_CONFIG_INVALID` (a bad `[gates]` table), `ASSET_FILE_INVALID` (a drifted gate file: `devkit sync`),
  `GATE_LOAD_FAILED` (a gate package that does not import) or `GATE_INTERPRETER_UNAVAILABLE` (the hook's Python
  cannot import devkit).

`pre-commit` and `commit-msg` fail closed: refusals, configuration errors and drifted gate files block the commit.
`post-commit` runs after the commit exists, so it only reports warnings and always exits `0`. A failing gate does
not stop the rest of its stage, so one attempt reports every refusal. `git commit --no-verify` skips the blocking
stages, as Git defines.

## Configure gates for the team and for yourself

Two layers contribute a `[gates]` table; the later one wins:

| Layer | Tracked | Use it for |
| --- | --- | --- |
| `.devkit/config.toml` | yes | Team policy shared by every clone |
| `<common-git-dir>/devkit.config` | no | Personal overrides for this clone and its worktrees |

`devkit gate install` writes every installed gate into `devkit.config` as a commented table. To change a setting
for your clone, uncomment the table header and only the keys you change; keys the team already sets are shown
without their value so you do not copy them by accident. The file is append-only: new gates get new tables, your
lines are never rewritten.

`enabled` works in every gate table. An entry for a gate that is not installed fails blocking stages, so a typo or a
forgotten `devkit sync` cannot silently switch policy off.

## Ship your own gate

A gate is a plugin package directory like a rule: a `gate.py` with a `BaseGate` subclass (`id`, `stage`, `order`,
`enabled_by_default`, typed `settings`, `run(ctx)`), helper modules imported relatively and `tests/` beside them.
Return `GateResult.passed()` or `GateResult.skipped()`, and raise `GateRefusedError` with a code and a `fix` to
refuse. Declare it in your bundle:

```toml
[[assets]]
id = "staged-file-limit"
kind = "gate"
source = "gates/staged_file_limit"

[presets.commit]
assets = ["staged-file-limit"]
```

Gates in a stage run by `order` then `id`: message transforms below `100`, checks at `100`, and `message-nonempty`
at `900` so it sees the final message.

## Sources

- [CAP-GATE-commit-gates](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/gate/CAP-GATE-commit-gates.md):
  hook wrappers, built-in gates, the gate contract, distribution and configuration layers.
- [Gate reference](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/development/reference/gate.md): commands, exit
  codes and error codes.
- Gates are part of the everyday loop in
  [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md).
