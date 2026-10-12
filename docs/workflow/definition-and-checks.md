# Workflow Definitions, Checks, Envelopes and Output Signals

**Status**: Architecture Specification & Reference Implementation  
**Package**: `agent-workflow-engine`  
**Related Documents**:
- [Workflow Engine Overview](overview.md)
- [Rule Authoring Guide](../rule-engine/rule-authoring.md)

---

## 1. Workflow Definition File

A definition is a Markdown file in `definitions_dir` (default `.devkit/workflows/`). Only the YAML frontmatter is parsed; the body holds prose gate rules.

```markdown
---
id: direct-delivery
title: "Direct delivery"
status: active
schema_version: 1
checks:                       # optional: runner/human checks this workflow declares
  - { name: ci-passed, class: runner, description: "repository CI is green" }
stages:
  - id: intent
    name: Intent
    human_gate: direction
    entry: []
    exit: [anchor-exists]
    artifacts: [task.md]
    skills: [wf-intent]
    role: developer
    isolation: none
    returns: []
  - id: build-verify
    name: Build and verify
    human_gate: false
    entry: [tasks-exists]
    exit: [tasks-all-checked, lint-clean]
    artifacts: [code, tests, tasks.md]
    skills: [wf-build]
    role: developer
    isolation: none
    returns:
      - { to: intent, when: new requirements }
  - id: review
    name: Review loop
    human_gate: false
    entry: [tasks-all-checked]
    exit: [envelope-review-passed]
    artifacts: [envelopes/review-NN.yaml]
    skills: [wf-review]
    role: reviewer
    isolation: preferred
    returns:
      - { to: build-verify, when: defects }
  - id: integrate
    name: Integrate
    human_gate: integration
    entry: [envelope-review-passed]
    exit: [anchor-status-completed, ci-passed]
    artifacts: []
    skills: [wf-integrate]
    role: developer
    isolation: none
    returns: []
---

## Gate rules

Prose for humans and agents. Not parsed.
```

### Document Fields

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Identifier used by `new --workflow`, `bind` and the binding record. Lowercase letters, digits, hyphens. |
| `title` | no | Display title. |
| `status` | no | `active` or `draft`; informational. |
| `schema_version` | yes | Must be `1`. |
| `checks` | no | Extra `runner` or `human` checks the workflow declares. Each has `name`, `class`, `description`. Names must not collide with built-in checks. |
| `stages` | yes | Ordered stage list, at least one. |
| `next` | no | Workflows this one may hand a completed unit to. See [Handoff Candidates](#handoff-candidates). |
| `layout` | no | Mapping with any of `work_dir`, `unit_path`, `anchor`; each overrides the `[workflow]` default for this workflow's units. Validated like the configuration keys. See [Overview, Per-Definition Layout](overview.md#per-definition-layout). |

### Stage Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Unique within the document; matches `[a-z][a-z0-9-]*`. |
| `name` | string | Display name. |
| `human_gate` | `false`, `true` or string | `true` names the gate after the stage id; a string names a shared gate. See [Overview, section 4](overview.md#4-approval-gates). |
| `optional` | bool | When unmet, the stage is passed over instead of becoming current. |
| `exception` | bool | Never evaluated; documents an out-of-band path. |
| `entry` | list of checks | Preconditions. Informational: `next` reports them but evaluates `exit` only. |
| `exit` | list of checks | The stage is done when every exit check is satisfied. |
| `artifacts` | list of strings | Files or things the stage produces. Informational. |
| `skills` | list of strings | Skills that perform this stage; the first is `[NEXT_SKILL]`. |
| `role` | string | `developer`, `-`, or a subagent role name. A role name must exist in the project's role vocabulary when one is known: receipt `subagent` assets or `[workflow] roles_dir`; see [Overview, section 6](overview.md#6-integration-with-the-rule-engine-and-distribution). |
| `isolation` | string | `none`, `preferred`, `required`. A non-developer role with isolation other than `none` yields `[DELEGATE]`. |
| `returns` | list of `{to, when}` | Stages this stage may return to and why. `to` must name a stage in the same document. |

Unknown stage keys, malformed or duplicate ids, unregistered checks, malformed check invocations, unknown `returns.to` targets, invalid `isolation` values and unknown roles (`unknown role '<role>' (no subagent contract found)`) are validation errors. `agent-workflow validate` reports every problem with the stage id and field. A malformed `layout` mapping is a structural error reported with the file.

### Shared Stages

A stage id is shared vocabulary across definitions: `[workflow.stages]` turns it off by id everywhere, and skills, runners and people recognize it by name. `agent-workflow validate` with no arguments therefore also compares every stage id that appears in more than one discovered definition and reports `shared stage '<id>' differs between <a> and <b>: <field>` for each of `exit`, `gate`, `role`, `isolation`, `skills` and `artifacts` that differ, against the first definition (in discovery order) that declared the id. This is a validation problem with exit code `1`. Validating explicit paths does not run the comparison.

### Handoff Candidates

A workflow is one segment of delivery. When a unit completes every stage, the definition's `next` list says which workflows may continue the same unit:

```yaml
next:
  - { workflow: spec-driven, when: [file-exists(spec.md)], recommended: true }
  - { workflow: hotfix, when: [frontmatter(task.md kind hotfix)] }
  - { workflow: direct-delivery }
```

| Field | Type | Meaning |
| --- | --- | --- |
| `workflow` | string | Id of the candidate definition. Must not be this workflow; must exist in the workspace (`validate` and `show` report an unknown id). |
| `when` | list of checks | Preconditions evaluated against the unit, in the same syntax as `exit`. A candidate is *eligible* when every check holds; an empty list is always eligible. |
| `recommended` | bool | Shown to the person choosing; informational. |

Eligibility is computed from checks so that an automatic handoff is deterministic. Whether a person chooses or the engine does is project policy: the reserved gate name `handoff` in `[workflow.approvals]` (see [Overview, section 4](overview.md#4-approval-gates)); a stage may not use `handoff` as its `human_gate`. The candidate's own first stage then evaluates the unit's existing files, so a candidate whose entry checks require earlier artifacts is naturally filtered by `when`.

### Schema Hash

`sha256:<hex>` of the canonical JSON (`sort_keys=True`, compact separators) of the `stages` list after normalization. Title, status, body, comments, the `checks` declaration, the `next` list and the `layout` mapping do not affect it. `show` prints it; `bind` records it in the anchor.

---

## 2. Checks

### Syntax

A check reference is `name` or `name(arg1 arg2 ...)`. Arguments are whitespace-separated tokens; nesting and an empty argument list are malformed. Aliases take no arguments.

### Classes

| Class | Who evaluates | Satisfied when |
| --- | --- | --- |
| `disk` | the engine, from files in the unit directory and Git | the primitive holds |
| `lint` | the engine, by running `agent-rule-engine` | no violation in the unit's files |
| `runner` | an external runner (CI); declared only | named in `--given` |
| `human` | a person; declared only | named in `--given` |
| `plugin` | the engine, by calling a loaded plugin check | the plugin's `evaluate` returns a satisfied result |

### Primitives

| Name | Parameters | Description |
| --- | --- | --- |
| `file-exists` | `file` | the file exists in the unit directory |
| `frontmatter` | `file field value` | the file's top-level frontmatter field equals the value |
| `tasks-checked` | `file` | the file has at least one `- [ ]`/`- [x]` task and none unchecked; items inside YAML frontmatter or fenced code are not tasks (the counter is `agent_rule_engine.count_tasks`, shared with rules) |
| `not-skeleton` | `file` | the file is missing or has no line equal to `<!-- devkit:skeleton -->` |
| `envelope-completed` | `kind` | the deciding `envelopes/<kind>-NN.yaml` has `status: completed` and no open finding |
| `envelope-check-pass` | `kind key` | the deciding envelope is completed and `checks.<key>` starts with `PASS` |
| `revision-ancestor` | `ancestor-kind descendant-kind` | `diff_scope.head` of the latest ancestor-kind envelope is a Git ancestor of, or equal to, that of the latest descendant-kind envelope |
| `lint-clean` | none | `agent-rule-engine` reports no violation for files under the unit directory |

### Aliases

Aliases are resolved against the anchor name in force for the workflow (its own `layout.anchor`, else the configured one), both in validation and at evaluation time.

| Alias | Expands to |
| --- | --- |
| `anchor-exists` | `file-exists(<anchor>)` |
| `anchor-status-planned` | `frontmatter(<anchor> status planned)` |
| `anchor-status-in-progress` | `frontmatter(<anchor> status in-progress)` |
| `anchor-status-completed` | `frontmatter(<anchor> status completed)` |
| `tasks-exists` | `file-exists(tasks.md)` |
| `tasks-all-checked` | `tasks-checked(tasks.md)` |
| `envelope-review-passed` | `envelope-completed(review)` |

### Plugin Checks

Checks beyond the primitives come from Python files, loaded in this order: every `.py` path recorded in the installation receipt under a `kind = "workflow-check"` asset, then every `*.py` under `[workflow] checks_dir` (default `.devkit/workflow-checks`). A file defines one or more `BaseCheck` subclasses:

```python
from agent_workflow_engine import BaseCheck, CheckContext, CheckResult


class HasWord(BaseCheck):
    name = "has-word"                       # [a-z][a-z0-9-]*; must not collide with a built-in or alias
    description = "the file contains the word"
    params = ("file", "word")               # positional argument names, as `checks` prints them

    def evaluate(self, ctx: CheckContext) -> CheckResult:
        text = ctx.read(ctx.args[0])        # text of a file in the unit directory, or None
        if text is None:
            return ctx.failed(f"{ctx.args[0]} missing")
        return ctx.passed() if ctx.args[1] in text else ctx.failed("word not found")
```

`CheckContext` carries `workspace_root`, `unit_dir`, `anchor`, the reference as written (`ref`), `name`, `args` and the unit's loaded `envelopes`; `ctx.passed(detail)` and `ctx.failed(detail)` build results with the right name and class. A loaded check is listed by `agent-workflow checks` with class `plugin`, resolved by `validate` like a primitive (argument count must match `params`), and evaluated by `next`. A check that raises yields an unsatisfied, evaluated result whose detail starts with `check failed:`; a result the plugin builds with another name or class is normalized. Files whose name starts with `_` or `.` are skipped. A file that fails to import, a check with an invalid `name` or `params`, a name defined twice, or a receipt path that is missing from disk is `CHECK_LOAD_FAILED` (`MAINTENANCE`), never a silent skip. A definition's declared `runner`/`human` check may not reuse a plugin's name.

A bundle declares such files as `kind = "workflow-check"` assets in `bundle.toml`; `devkit sync` deploys them under `.devkit/managed/<bundle>/` and records their paths in the receipt, exactly as for `kind = "rule"`.

### Implicit Gate Check

A stage with `human_gate` carries an implicit `human` check named `gate:<gate>`. It is listed under `[UNMET]` like any other check, satisfied by `--given <gate>` or by the `auto` policy, and the whole stage is skipped under `off`.

### Stage Policy

`[workflow.stages] <id> = "off"` skips a stage by id, gated or not, before any check or gate is evaluated. The skip is reported as `[SKIPPED: <id> reason=stages.<id>=off]` and never blocks completion. See [Overview, Stage Policy](overview.md#stage-policy).

---

## 3. Envelopes

Delegated roles and reviews return a YAML envelope written to `<unit>/envelopes/<kind>-<NN>.yaml`. `kind` matches `[a-z][a-z0-9-]*`; `NN` is a two-digit sequence per kind. The highest sequence is current and earlier files are history. Files are never overwritten; `agent-workflow envelope new` writes the next number.

```yaml
kind: review
stage: review
created_at: 2026-10-12T10:00:00Z
status: completed            # completed | needs_input | failed
summary: "1-3 line judgment"
findings:
  - issue: "What was found"
    evidence: "path:line"
    failure_condition: "Under which input it fails"
    suggested_action: "Recommended next step"
    resolution: open         # open | resolved | waived (default open)
assumptions: ["what the judgment rests on"]        # optional
unverified_areas: ["what was not checked"]        # optional
checks:                      # free-form keys; a value starting with PASS satisfies envelope-check-pass
  tests: "PASS 14/14"
diff_scope: { base: "main", head: "<sha>" }
review: review-01.yaml       # reverify only: the review round it closes
```

- `kind` and `status` are required; `kind` must match the file name.
- A `reverify` envelope must name the `review-NN.yaml` it closes. The deciding review state is the latest review round, or the last reverify that references it.
- `completed` with no findings is a valid pass. `needs_input` and `failed` never satisfy a check.
- `assumptions` and `unverified_areas` are lists of strings; `checks` is a mapping; `findings` is a list of mappings. Other keys are ignored.
- Malformed envelopes are reported as `[ENVELOPE_ERROR: file reason]` and are not loaded; evaluation continues.

### Authoring

`agent-workflow envelope new --unit DIR --kind KIND [--stage ID]` with no other flag writes a `needs_input` skeleton for the author to fill in. Any further flag switches to authoring, where the file is written complete so that no agent edits YAML by hand:

| Flag | Effect |
| --- | --- |
| `--status` | `completed` (default when authoring), `needs_input` or `failed`. |
| `--summary TEXT` | The judgment. |
| `--assume TEXT`, `--unverified TEXT` | Repeatable; fill `assumptions` and `unverified_areas`. |
| `--check NAME=VERDICT[ detail]` | Repeatable; `VERDICT` is `PASS`, `FAIL` or `SKIP` and may carry a detail such as `PASS 14/14`. |
| `--base REV`, `--head REV` | `diff_scope`; `--head` is what `revision-ancestor` compares. |
| `--findings-file PATH` (or `-` for stdin) | A YAML list of findings; `issue` and `evidence` are required, `resolution` defaults to `open`. A `review` records findings as found, so a resolution other than `open` is refused. |
| `--from latest` (or a review/reverify file) | Carries the findings of the round being closed into a `reverify` and sets its `review`. `latest` is the deciding review state. Refused for `review`; required for `reverify`. |
| `--resolve N` (repeatable) or `--resolve all` | Marks carried finding `N` (1-based) resolved; `all` resolves every open one. |
| `--waive N=REASON` (repeatable) | Marks carried finding `N` waived, recording the reason in `suggested_action` as `waived: REASON`. |

Findings from `--findings-file` are appended after any carried findings. The written key order is `kind, stage, created_at, status, review, summary, findings, assumptions, unverified_areas, checks, diff_scope`, omitting empty optional keys. The confirmation line is `[ENVELOPE: <file> kind=K seq=NN status=S open_findings=N]`.

`agent-workflow envelope check --unit DIR` loads every file under `envelopes/`, prints one `[ENVELOPE: file kind seq status open_findings]` line per valid file and one `[ENVELOPE_ERROR: file reason]` per malformed one, then `[OK: N envelopes]` when nothing is malformed. Any malformed file raises `ENVELOPE_INVALID` (exit `1`) whose `[DETAIL]` lines repeat file and reason. `--format json` emits `{"envelopes": [...], "errors": [...]}`.

---

## 4. Binding and Drift

`new` and `bind` write `workflow: <id>` and `workflow_hash: <hash>` into the anchor's frontmatter, replacing existing values and preserving every other line. `handoff` rebinds the unit to the chosen candidate and appends the finished segment to `workflow_history`, one flow-style line:

```yaml
workflow: spec-driven
workflow_hash: sha256:74bc...
workflow_history: [{workflow: triage, hash: 'sha256:a017...', completed: '2026-10-13'}]
```

After a handoff, `next` evaluates the new workflow from its first stage against the unit's files; finished segments are history and are never re-evaluated, and drift applies to the current binding only.

On `next`:

- Unbound anchor: evaluated against `--workflow` or the configured default; output says `bound=no`.
- Bound, hash matches: normal evaluation.
- Bound, hash differs, unit not complete: refused with a `WORKFLOW_DRIFT` advisory (`BLOCKED`) on stderr whose `[DETAIL]` lines carry the recorded and current hashes, exit `1`. Run `bind` to accept the reviewed change.
- Bound, hash differs, unit complete (`status: completed` in the anchor): evaluated against the current definition and reported as `[DRIFT: ...]`; history is never blocked.

---

## 5. Output Signals

`next --format text` prints one tagged line per fact. Agents read the tags; the order is stable.

```text
[WORKFLOW: direct-delivery unit=.devkit/transient/work/login status=in-progress bound=yes]
[DONE: intent specify]
[SKIPPED: collect-feedback reason=stages.collect-feedback=off]
[STAGE: review human_gate=no role=reviewer isolation=preferred]
[UNMET: envelope-review-passed]
[CHECK: envelope-review-passed class=disk evaluated=true detail="no review envelope"]
[NEXT_SKILL: wf-review]
[DELEGATE: role=reviewer isolation=preferred contract=.devkit/managed/team/subagents/reviewer.md]
[RETURNS: build-verify when=defects]
[GATE: integration policy=ask given=no]
[WAITING: human gate:integration]
[ENVELOPE_ERROR: envelopes/review-01.yaml missing required key status]
```

- `[STAGE: - complete=true]` when every stage is done or skipped.
- `[SKIPPED: <id> reason=...]` names the policy entry that skipped the stage: `stages.<id>=off` or `approvals.<gate>=off`.
- `[WAITING]` appears when the current stage is gated, or when every unmet check is `runner` or `human`. Its class is `human` when any unmet check is human.
- `[GATE]` appears only for a gated current stage.
- `[DELEGATE]` carries `contract=<path>` when the role is in the project's vocabulary (receipt `subagent` asset or `roles_dir` file); otherwise the key is absent.

When the workflow is complete and declares `next` candidates (and `approvals.handoff` is not `off`), the handoff block follows:

```text
[STAGE: - complete=true]
[HANDOFF: policy=ask candidates=spec-driven hotfix direct-delivery eligible=hotfix direct-delivery recommended=- chosen=-]
[CANDIDATE: spec-driven eligible=no recommended=yes when=file-exists(spec.md)=false]
[CANDIDATE: hotfix eligible=yes recommended=no when=frontmatter(task.md kind hotfix)=true]
[CANDIDATE: direct-delivery eligible=yes recommended=no when=-]
[WAITING: human handoff]
```

- `recommended=` lists only candidates that are both recommended and eligible.
- Under `policy=auto`, `chosen=` names the first eligible candidate and no `[WAITING]` line appears; with no eligible candidate the engine falls back to waiting for a person.
- A recorded choice (`decisions/NN-handoff.yaml`, see [Human Interaction Contract](human-interaction.md)) sets `chosen=` under either policy and adds `decision=<file>`.
- No `[HANDOFF]` line means the unit is finished.

Whenever a person must act, one `[REQUEST: ...]` line per open request follows the stage block, with `[DECLINED: ...]` for a request that was refused and is still open, and `[DECISION_ERROR: ...]` for a malformed record. The JSON object carries them as `requests` and `decision_errors`. Formats are in [Human Interaction Contract](human-interaction.md).

`--format json` emits one object:

```json
{
  "workflow": "direct-delivery",
  "unit": ".devkit/transient/work/login",
  "status": "in-progress",
  "bound": true,
  "done": ["intent", "specify"],
  "skipped": [{"id": "collect-feedback", "reason": "stages.collect-feedback=off"}],
  "stage": {"id": "review", "name": "Review loop", "human_gate": null, "role": "reviewer", "isolation": "preferred", "skills": ["wf-review"], "entry": [], "exit": [], "artifacts": [], "returns": []},
  "unmet": [{"name": "envelope-review-passed", "class": "disk", "satisfied": false, "evaluated": true, "detail": "no review envelope"}],
  "next_skill": "wf-review",
  "delegate": {"role": "reviewer", "isolation": "preferred", "contract": ".devkit/managed/team/subagents/reviewer.md"},
  "gate": null,
  "waiting": null,
  "complete": false,
  "envelope_errors": [],
  "drift": null,
  "handoff": null,
  "requests": [],
  "decision_errors": []
}
```

`handoff` is `null` until the workflow is complete; then it is `{"policy", "candidates": [{"workflow", "recommended", "eligible", "checks": [...]}], "eligible": [...], "recommended": [...], "chosen"}`.

`show --format json` emits the parsed document plus `hash`, `layout`, the effective `anchor`, `approvals` and `stages_off`; `show --unit <dir>` adds `binding` (`workflow`, `workflow_hash`, `workflow_history`, `drift`) and, in text, a `[BINDING: workflow=W hash=H drift=true|false]` line after the document. `checks --format json` emits the registry, plugin checks included. `list --format json` emits `[{"unit", "anchor", "status", "workflow", "workflow_hash", "history"}]` across every layout in use; the text form is `[UNIT: <dir> status=S workflow=W anchor=A]`. `list --status <value>` keeps units whose anchor `status` equals a given value (repeatable) and `--exclude-status <value>` drops them; both are exact matches, so active units are `--exclude-status completed`. `handoff --format json` emits `{"unit", "from", "to", "workflow_hash", "policy", "history"}`. `requests --format json` emits the `requests` array alone; `answer --format json` emits the written record with its `file`.
