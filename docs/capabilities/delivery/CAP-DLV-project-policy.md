---
id: CAP-DLV-project-policy
title: Project Policy
summary: "Effective approval, stage, Git (auto or required worktree and pull request levels) and repository-first feedback policy reported by devkit spec policy, including Host conversational approval and retained-base automatic authority for lifecycle CLI operations."
area: delivery
status: active
created_at: 2026-10-13
usecases:
  - UC-route-development-intent
  - UC-run-parallel-work-safely
  - UC-drive-development-to-integration
entrypoints:
  - packages/devkit-spec/src/devkit_spec/features/policy/services/config.py
  - packages/devkit-spec/src/devkit_spec/features/policy/cli/commands.py
  - packages/devkit/src/devkit_agt/features/integration/cli.py
---

# [CAP-DLV-project-policy] Project Policy

## 1. Summary

A project decides how delivery runs: which approval gates wait for a person, which stages are switched off, whether
worktrees and pull requests are used when a task needs them or always, which integration readiness provider
`devkit_agt.features.integration` calls, and how repository-first feedback is recorded. Policy
devkit already models stays in devkit's tables
(`[workflow.approvals]`, `[workflow.stages]`, `[worktree]`, `[integration]`); devkit-spec adds only what is specific to spec-driven
development, under the `[tool.spec]` extension table that devkit passes through unread. Agents read the effective
policy with one command, `devkit spec policy`, before routing, gate and Git decisions. Rationale:
`ADR-spec-package-on-devkit`; the Git policy levels: `ADR-worktrees-branches-and-scope`; integration readiness and scoped cleanup: `SPEC-hook-driven-integration-cleanup`.

## 2. Scope & Boundary

- **In-Scope**: `devkit spec policy` (text and JSON), the `[tool.spec]` table and its validation
  (`devkit_spec.features.policy.services.config.read_spec_config`), the defaults the command reports, and the `[tool.spec]` tables of devkit's
  commented config template (`devkit_spec.features.policy.services.config.template`).
- **Out-of-Scope**:
  - The meaning of `[[tool.spec.namespaces]]`: `CAP-DOCS-namespaces`.
  - The meaning of `[tool.spec.scope]`: `CAP-COLL-work-scope-registry`. This capability owns their validation only.
  - How gates and stage switches act on a workflow: `CAP-DLV-delivery-workflows` and devkit's workflow engine.
  - Executing worktree and integration steps (`CAP-HARN-agent-guidance`): devkit's `devkit worktree`, `devkit_agt.features.integration` (`[integration] provider = "spec"`), and the `spec`
    skill's worktree procedure.
- **Non-Goals**:
  - **Scope Excluded**: writing policy. The command only reads; the project edits `.devkit/config.toml`.
  - **Scope Excluded**: granting commit, publication or host permission authority. Explicit retained-base auto grants only the verified local integration CLI and exact cleanup authority defined by `CAP-INT-mcp-services`.

## 3. Business Rules & Policies

1. **Read through the command**: agents MUST read policy through `devkit spec policy`, never by parsing
   `.devkit/config.toml`; a policy command error stops policy-dependent work.
2. **devkit tables first**: a policy devkit models (approvals, stage switches, pull requests, branch cleanup, merge method, worktree
   setup, integration readiness provider) MUST live in devkit's table; `[tool.spec]` holds only keys devkit has no table for.
3. **Defaults**: a gate the project does not set is `ask` with `source=default` (devkit's default for every gate);
   `[tool.spec] worktree` and `depth_escalation` default to `"auto"`; `[worktree]` values are devkit's defaults (`pull_request = "auto"`,
   `delete_branch = true`, `merge = "no-ff"`, no `setup`); `[integration] provider = "spec"` selects `devkit_spec.features.delivery.usecases.integration` for `IntegrationService`.
4. **Decision boundaries and task intent**: `plan-accept`, `proposal-handoff`, and `dev-integration` are the three
   main decision boundaries, followed in policy output by `plan-intent` and configured custom gates. Each boundary
   and task intent permits `ask` or `auto`, default `ask`; `off` is `SPEC_CONFIG_INVALID`. `proposal-handoff` is
   declared by no workflow stage: `devkit spec proposal accept --mode accept_and_handoff` and
   `devkit spec proposal handoff --effort` read it (`CAP-DLV-proposal-incubation`).
   `plan-intent` records an already instructed task without another confirmation. An uninstructed Backlog item does
   not become authorized merely because an agent discovers it. Main boundaries are independent: direction acceptance
   may wait in Backlog before Development starts. The Host may carry one conversational decision across acceptance and handoff when the exact effects are presented together.
   Owning base auto, also retained by the prospective source, delegates only that boundary's verified local effects.
   A task branch cannot authorize itself; revocation stops remaining effects. Authority is reported as `policy`, never
   as a human approval. The Planning acceptance merge belongs to `plan-accept`, not Development's `dev-integration`.
   Host permissions, required PR policy and publication authority remain separate (`ADR-delivery-decision-boundaries`).
   `exception` is a resolution stage, not a gate: its key emits `SPEC_APPROVAL_KEY_IGNORED` and is not listed.
5. **Strict table**: `[tool.spec]` MUST be a table with only the keys `worktree`, `depth_escalation`, `namespaces`,
   `scope` and `feedback`; anything else is `SPEC_CONFIG_INVALID`, raised by every command that reads the table.
   `worktree` is `"auto"` or `"required"`, `depth_escalation` `"auto"` or `"ask"`; a boolean is `SPEC_CONFIG_INVALID`, with no mapping (devkit rejects a boolean `pull_request` the
   same way, `WORKTREE_CONFIG_INVALID`).
6. **Git policy levels**: `[tool.spec] worktree` applies to `direct` mode only (`local-orchestrated` always runs each
   worker in a worktree, `cloud-pr` uses the runner's checkout): `"required"` runs every `spec` and `proposal`
   activity on its activity branch in a separate worktree; `session` depth is never required to. `"auto"` leaves the choice to the agent: a worktree when the
   checkout holds changes unrelated to the task (the user's uncommitted work must stay put), another task is in flight
   in the checkout, or the user asks; otherwise the current checkout, on the activity branch started with
   `devkit worktree start <branch> --no-worktree`.
   Switching branches in that checkout changes the branch seen by every session using its directory; another
   session can commit to the checked-out task branch. The direct user coordinates shared sessions and may choose
   a separate worktree for a session task. The local orchestration Host coordinates workers, which still run
   in their own worktrees.
   `pull_request = "required"` integrates every task, `session` depth included, through a pull request (`devkit worktree
   finish --merge` and `IntegrationService.prepare` are refused with `WORKTREE_PR_POLICY`); `"auto"` uses one when the task needs platform review or CI, the base branch refuses
   direct pushes, or the user asks, otherwise a local merge. The integration path does not choose the worktree: a task integrating
   through a pull request may run on its branch in the current checkout. Each `auto` choice and its reason are reported in the final change report's
   assumptions; an explicit user request naming the checkout or the integration path overrides the policy for that
   task only, recorded there too.
7. **Template at the defaults**: `template()` MUST describe every `[tool.spec]` key at the default
   `read_spec_config` applies (an example for a key unset by default and for the namespaces), so the commented
   tables `devkit config template` writes read back as the defaults once uncommented.

8. **Feedback defaults**: `[tool.spec.feedback]` defaults to `capture = "observed"`, `coverage = "repo"`,
   `detail = "standard"` and `reminder = "contextual"`. Repository-owned rules, skills, instructions, workflows,
   tools, templates, overrides and documents are the base targets; `repo-and-upstream` adds upstream tools used
   during work. Explicit feedback requests override autonomous capture, coverage and stage restrictions.
9. **Feedback consumption**: agents read effective feedback settings through `devkit spec policy`. Capture,
   detail and reminder behavior is defined by `CAP-HARN-agent-guidance`; a workflow stage switch remains in
   devkit's `[workflow.stages]` rather than a second feedback enable flag.

## 4. Interfaces & Data Contracts

### 4.1 Command

```bash
uv run devkit spec policy [-w/--workspace-root DIR] [--format text|json] [-q] [-v] [--strict]
```

```text
[GATE_POLICY: plan-accept policy=ask source=default]
[GATE_POLICY: proposal-handoff policy=ask source=default]
[GATE_POLICY: dev-integration policy=auto source=config]
[GATE_POLICY: plan-intent policy=ask source=default]
[STAGE_POLICY: collect-feedback state=off]
[GIT_POLICY: worktree=required pull_request=auto delete_branch=yes setup="uv sync"]
[ROUTING_POLICY: depth_escalation=auto]
[FEEDBACK_POLICY: capture=observed coverage=repo detail=standard reminder=contextual]
```

- `GATE_POLICY`: one line per gate; `policy` is `ask` or `auto` for the three boundaries and `plan-intent` (rule 4),
  and `ask`, `auto` or `off` for a configured custom gate (`CAP-DLV-workflow-orchestration`);
  `source` is `config` when `.devkit/config.toml` sets it, else
  `default`.
- `STAGE_POLICY`: one line per stage the project switched off (`state=off`), sorted.
- `GIT_POLICY`: `worktree` (`[tool.spec] worktree`, `auto` or `required`), then devkit's `[worktree]` settings
  `pull_request` (`auto` or `required`), `delete_branch` and `setup` (`-` when unset).

- `ROUTING_POLICY`: `depth_escalation` (`auto`: the Host raises `planning-depth` on its own judgment; `ask`: the user
  confirms each raise; a worker never raises it).
- `FEEDBACK_POLICY`: one line with effective `capture`, `coverage`, `detail` and `reminder`, including defaults.

JSON: `{"approvals": {<gate>: {"policy", "source"}}, "stages_off": [...], "git": {"worktree", "pull_request",
"delete_branch", "setup"}, "routing": {"depth_escalation"}, "feedback": {"capture", "coverage", "detail",
"reminder"}}` (`worktree` and `pull_request`
are the level strings, `setup` is `null` when unset).

### 4.2 Configuration

```toml
# .devkit/config.toml
[workflow.approvals]
dev-integration = "ask"     # one approval per integration unit (PR); "auto" after review, checks and reconcile
plan-accept = "ask"         # proposal direction; auto delegates checked acceptance and Planning merge
proposal-handoff = "ask"    # start Development; auto uses the accepted dev_effort hint
plan-intent = "ask"         # record instructed task intent without repeating the same consent

[workflow.stages]
collect-feedback = "off"    # switch a stage off by id

[worktree]
pull_request = "required"   # always integrate through pull requests (default "auto": as the task needs)
delete_branch = true        # delete the merged local branch; also select leased remote deletion on the native PR route
merge = "no-ff"             # a merge commit per task (default); "ff-only" keeps linear history
setup = "uv sync"           # run in each new worktree

[integration]
provider = "spec"           # devkit_agt.features.integration.readiness entry point for approval-bound local integration

[tool.spec]
worktree = "required"       # direct mode: spec and proposal activities always run in a worktree (default "auto")
depth_escalation = "ask"    # the user confirms each planning-depth raise (default "auto")

[[tool.spec.namespaces]]    # monorepo packages with their own Living Spec under docs/packages/<name>/
name = "api"
path = "services/api"

[tool.spec.feedback]
capture = "observed"        # observed | requested-only
coverage = "repo"           # repo | repo-and-upstream
detail = "standard"         # brief | standard | detailed
reminder = "contextual"     # contextual | off

[tool.spec.scope]           # the work-scope registry (devkit spec scope); every key is optional
shared_path = "/srv/scope"  # absolute or starting with ~; default: devkit-spec-scope/ in the Git common directory
namespace = "team"          # default: a hash of the Git common directory
timeout = 10                # whole seconds per registry command, 1 to 300
```

| Key | Type | Default | Validation |
| --- | --- | --- | --- |
| `tool.spec.worktree` | string | `"auto"` | `auto` or `required`; a boolean is rejected. |
| `tool.spec.depth_escalation` | string | `"auto"` | `auto` or `ask`. |
| `tool.spec.namespaces` | array of tables | `[]` | Each entry exactly `name` and `path`; `name` lowercase words joined by `-`, not `global`; `path` a safe workspace-relative directory in canonical form (no `./`, `//` or trailing `/`); no name or path registered twice. |
| `tool.spec.scope.shared_path` | string | Git common dir `devkit-spec-scope/` | Absolute after `~` expansion. |
| `tool.spec.scope.namespace` | string | common-dir hash | Letters, digits, `.`, `_`, `-`, not starting with `.`. |
| `tool.spec.scope.timeout` | integer | `10` | Whole seconds from 1 to 300 (a boolean is rejected). |
| `tool.spec.feedback.capture` | string | `"observed"` | `observed` or `requested-only`. |
| `tool.spec.feedback.coverage` | string | `"repo"` | `repo` or `repo-and-upstream`. |
| `tool.spec.feedback.detail` | string | `"standard"` | `brief`, `standard` or `detailed`. |
| `tool.spec.feedback.reminder` | string | `"contextual"` | `contextual` or `off`. |

`devkit config template` writes the `[tool.spec]` tables into `.devkit/config.toml` as comments, from
`devkit_spec.features.policy.services.config.template`, the `devkit.config_template` entry point `spec`: every key at its default, an example
for `shared_path`, `namespace` and the namespaces, uncommented in place to change a value. devkit adds only the
tables the file does not mention yet and never changes a line.

`collect-feedback = "off"` makes the delivery workflows skip the feedback sweep; the
executor reports it as skipped.

### 4.3 Library

```python
from devkit_spec.features.policy.services.config import read_spec_config

config = read_spec_config(root)  # SpecConfig with worktree, namespaces, scope and feedback
tables = template()  # list[devkit_dist.features.project.services.config_template.TemplateTable]: [tool.spec], its namespaces, scope and feedback tables
```

`Namespace` has `name`, `path` and `docs` (`docs/packages/<name>`); `ScopeConfig` has `shared_path` (`Path` or
`None`), `namespace` (`str` or `None`) and `timeout`. `FeedbackConfig` has the four validated string choices
`capture`, `coverage`, `detail` and `reminder`.

### 4.4 Codes

| Code | Level | Class | Condition |
| --- | --- | --- | --- |
| `SPEC_CONFIG_INVALID` | `ERROR` (`INPUT_ERROR`) | `SpecConfigError` | `[tool.spec]` is not a table, has an unknown key, `worktree` is not `auto` or `required`, or a namespace entry is malformed (keys other than `name` and `path`, an invalid or `global` name, an unsafe or non-canonical path, a name or path registered twice), or `[tool.spec.feedback]` has an invalid table, unknown key, type or choice, or `[tool.spec.scope]` is not a table, has an unknown key, a relative `shared_path`, a `namespace` that is not a plain name, or a `timeout` outside 1 to 300 whole seconds. |

devkit's own errors pass through: `CONFIG_INVALID` (an unreadable file), `WORKFLOW_CONFIG_INVALID`,
`WORKTREE_CONFIG_INVALID`.

On the pull-request route (`CAP-INT-mcp-services`), `delete_branch` selects local and remote branch deletion in the
report the Host presents before conversational approval; it grants no authority. GitHub automatic branch deletion
is separately disclosed. Required PR policy restricts route selection without granting push, merge or cleanup
permission.
