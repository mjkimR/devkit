# Workflow Definitions and Checks

**Package**: `devkit.workflow`. Review envelopes: [Review Envelopes](envelopes.md); what `next` prints: [CLI and Output Contract](cli-and-output.md).  
**Related**: [Workflow Engine Overview](overview.md), [Rule Authoring Guide](../rules/rule-authoring.md).

## 1. Workflow Definition File

A definition is a Markdown file in `definitions_dir` (default `.devkit/workflows/`) or a synchronized `kind = "workflow"` asset. Only the YAML frontmatter is parsed; the body holds prose gate rules.

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
| `schema_version` | yes | Must be the integer `1`. |
| `checks` | no | Extra `runner` or `human` checks the workflow declares. Each has `name` (`[a-z][a-z0-9-]*`), `class` and `description`, and nothing else. Names must be unique, and must not collide with built-in or plugin checks, nor with a gate of the workflow (so `--given` stays unambiguous). |
| `stages` | yes | Ordered stage list, at least one. |
| `next` | no | Workflows this one may hand a completed unit to. See [Handoff Candidates](#handoff-candidates). |
| `layout` | no | Mapping with any of `work_dir`, `unit_path`, `anchor`; each overrides the `[workflow]` default for this workflow's units and is validated like the configuration key. See [Per-Definition Layout](overview.md#per-definition-layout). |

### Stage Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Unique within the document; matches `[a-z][a-z0-9-]*`. Shared across definitions (see [Shared Stages](#shared-stages)). |
| `name` | string | Display name. Changing it never causes drift. |
| `human_gate` | `false`, `true` or string | `true` names the gate after the stage id; a string names a shared gate (`[a-z][a-z0-9-]*`, so `[workflow.approvals]` can name it). `handoff` is reserved. See [Approval Gates](overview.md#3-approval-gates). |
| `optional` | `true` or `false` | When unmet, the stage is passed over instead of becoming current. |
| `exception` | `true` or `false` | Never evaluated; documents an out-of-band path. |
| `entry` | list of checks | Preconditions. Informational: listed by `show` and in the JSON `stage` object, never evaluated. |
| `exit` | list of checks | The stage is done when every exit check is satisfied. |
| `artifacts` | list of strings | Files or things the stage produces. Informational. |
| `skills` | list of strings | Skills that perform this stage; the first is `[NEXT_SKILL]`. |
| `role` | string | `developer`, `-`, or a subagent role name, which must be in the project's [role vocabulary](overview.md#4-integration-with-the-rule-engine-and-distribution) when one is known. |
| `isolation` | string | `none`, `preferred`, `required`. A non-developer role with isolation other than `none` yields `[DELEGATE]`. |
| `returns` | list of `{to, when}` | Stages this stage may return to and why. `to` must name a stage in the same document. Taking a return is `devkit workflow return --to <stage>` ([How the Engine Applies Answers](human-interaction.md#5-how-the-engine-applies-answers)). |

Unknown document or stage keys, malformed or duplicate ids, malformed gate names, duplicate or colliding declared checks (each reported once; the other declared checks stay usable), unregistered checks, `runner` or `human` checks in a `next` candidate's `when`, malformed check invocations, a `file` argument outside the unit directory (absolute or with `..`), unknown `returns.to` targets, invalid `isolation` values and unknown roles are validation problems, which `devkit workflow validate` reports with the stage id and field. A value of the wrong type (`optional: "false"`, `role: 3`), an unknown key inside a `returns`, `checks` or `next` item, and a malformed `layout` mapping are structural errors reported with the file.

### Shared Stages

A stage id is shared vocabulary across definitions: `[workflow.stages]` turns it off by id everywhere, and skills, runners and people recognize it by name. `devkit workflow validate` with no arguments therefore also compares every stage id that appears in more than one discovered definition and reports `shared stage '<id>' differs between <a> and <b>: <field>` (`SHARED_STAGE_MISMATCH`, exit `1`) for each of `exit`, `gate`, `role`, `isolation`, `skills` and `artifacts` that differs from the first definition (in discovery order) that declared the id. Validating explicit paths does not run the comparison.

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
| `when` | list of checks | Preconditions evaluated against the unit, in the same syntax as `exit`. A candidate is *eligible* when every check holds; an empty list is always eligible. Only checks the engine evaluates (`disk`, `lint`, `plugin`) are allowed: a `runner` or `human` check is a validation problem, since nothing can satisfy it while a handoff is chosen. |
| `recommended` | bool | Shown to the person choosing; informational. |

Eligibility is computed from checks so that an automatic handoff is deterministic; whether a person or the engine chooses is the [`handoff` gate](overview.md#the-handoff-gate) policy. The candidate's own first stage then evaluates the unit's existing files, so a candidate whose entry checks require earlier artifacts is naturally filtered by `when`.

### Schema Hash

`sha256:<hex>` of the canonical JSON (`sort_keys=True`, compact separators) of the `stages` list after normalization, without each stage's display `name`. Title, status, body, comments, stage names, the `checks` declaration, the `next` list and the `layout` mapping do not affect it. `show` prints it; `bind` records it in the anchor.

## 2. Checks

A check reference is `name` or `name(arg1 arg2 ...)`. Arguments are whitespace-separated tokens; nesting and an empty argument list are malformed. Aliases take no arguments. `devkit workflow checks` lists every registered check.

| Class | Who evaluates | Satisfied when |
| --- | --- | --- |
| `disk` | the engine, from files in the unit directory and Git | the primitive holds |
| `lint` | the engine, by running `devkit.rules` | no violation in the unit's files |
| `runner` | an external runner (CI); declared only | named in `--given` |
| `human` | a person; declared only | an accepted `check:<name>` decision record of the current segment for the stage being evaluated, or named in `--given` |
| `plugin` | the engine, by calling a loaded plugin check | the plugin's `evaluate` returns a satisfied result |

### Primitives

| Name | Parameters | Description |
| --- | --- | --- |
| `file-exists` | `file` | the file exists in the unit directory (every `file` argument is a relative path inside the unit) |
| `frontmatter` | `file field value` | the file's top-level frontmatter field equals the value |
| `tasks-checked` | `file` | the file has at least one `- [ ]`/`- [x]` task and none unchecked; items inside YAML frontmatter or fenced code are not tasks (the counter is `devkit.rules.count_tasks`, shared with rules) |
| `not-skeleton` | `file` | the file is missing or has no line equal to `<!-- devkit:skeleton -->` |
| `envelope-completed` | `kind` | the deciding `envelopes/<kind>-NN.yaml` ([Review Envelopes](envelopes.md)) has `status: completed` and no open finding |
| `envelope-check-pass` | `kind key` | the deciding envelope is completed and `checks.<key>` starts with `PASS` |
| `revision-ancestor` | `ancestor-kind descendant-kind` | `diff_scope.head` of the latest ancestor-kind envelope is a Git ancestor of, or equal to, that of the latest descendant-kind envelope; both must be hexadecimal commit ids. When Git cannot answer (not a repository, an unknown commit as in a shallow clone, a timeout) the check is unsatisfied and `evaluated=false`, with Git's error in the detail |
| `lint-clean` | none | `devkit.rules` reports no violation for files under the unit directory ([Integration](overview.md#4-integration-with-the-rule-engine-and-distribution)); the detail quotes the first three violations and counts the rest, naming `devkit rules check <unit>`. A unit directory that resolves outside the workspace root (an absolute `--unit`, or a symbolic link leaving the root) cannot be linted: the check fails with a `PATH_UNSAFE` lint error |

### Aliases

Aliases resolve against the anchor name in force for the workflow (its own `layout.anchor`, else the configured one), in validation and at evaluation time.

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

Checks beyond the primitives come from **plugin packages**, directories of Python modules loaded in this order: every `kind = "workflow-check"` asset recorded in the installation receipt (one package per asset, whose modules are its listed `.py` files), then each immediate subdirectory of `[workflow] checks_dir` (default `.devkit/workflow-checks`). A bundle declares such an asset in `bundle.toml` with a directory `source`; `devkit sync` deploys and records it exactly as a `kind = "rule"` asset. Every `.py` file of a package is a module (files under `tests/`, `test_*.py` and `*_test.py` excepted, so tests live beside the code), `__init__.py` is optional, and modules import each other relatively (`from .words import contains`), also lazily inside `evaluate`. Plugin packages are executable Python and must come from a trusted source. A package's modules define one or more `BaseCheck` subclasses, for example `.devkit/workflow-checks/words/check.py`:

```python
from devkit.workflow import BaseCheck, CheckContext, CheckResult


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

- `CheckContext` carries `workspace_root`, `unit_dir`, `anchor`, the reference as written (`ref`), `name`, `args` and the unit's loaded `envelopes`; `ctx.passed(detail)` and `ctx.failed(detail)` build results with the right name and class.
- A loaded check is listed by `checks` with class `plugin`, resolved by `validate` like a primitive (argument count must match `params`), and evaluated by `next`. A check that raises yields an unsatisfied, evaluated result whose detail starts with `check failed:`; a result built with another name or class is normalized.
- Subdirectories of `checks_dir` whose name starts with `_` or `.` are skipped; a `.py` file directly in `checks_dir` is `WORKFLOW_CHECK_LOAD_FAILED` with a fix that moves it into `<checks_dir>/<name>/`. A receipt-listed module is loaded whatever its name.
- Loading is atomic per package: a package any module of which fails to import, that defines a check with an invalid `name` or `params`, or that defines a name an earlier package (or another of its own classes) already defined contributes none of its checks and is `WORKFLOW_CHECK_LOAD_FAILED` (`PluginError`, `MAINTENANCE`) naming the package, never a silent skip.
- Receipt-listed packages are found and their files verified first with `devkit.core.receipt.verified_asset_packages`, as rules and gates are: a file that is missing, resolves outside the project or differs from the SHA-256 the receipt records is `WORKFLOW_CHECK_LOAD_FAILED` with the fix `devkit sync` (restore) or `devkit override create <bundle>:<asset>` (keep the edit); only a project override under `.devkit/overrides/` may lack a record and then loads as it is; any other file without one is refused the same way, and a package with a refused file is not loaded.
- A definition's declared `runner`/`human` check may not reuse a plugin's name.

### Implicit Gate Check

A stage with `human_gate` carries an implicit `human` check named `gate:<gate>`. It is asked only once every exit check of the stage holds: until then it is not listed under `[UNMET]`, no request is emitted, `[WAITING]` does not name it and `[GATE]` shows it as `satisfied=no`. Then it is listed under `[UNMET]` like any other check. It is satisfied by an accepted `gate:<gate>` decision record of the current segment, by `--given <gate>`, or by the `auto` policy; the whole stage is skipped under `off`, and any stage is skipped by `[workflow.stages] <id> = "off"` before its checks are evaluated ([Stage Policy](overview.md#stage-policy)).

## 3. Binding and Drift

`new` and `bind` write `workflow: <id>` and `workflow_hash: <hash>` into the anchor's frontmatter. The binding records only the id, which every unit command looks up among the discovered definitions, so `--workflow <path>` binds only the file discovered for its id (for example `.devkit/workflows/<id>.md`); any other definition file is refused with `WORKFLOW_NOT_BINDABLE` before anything is written. `next --workflow <path>` still evaluates a unit against such a file without binding it. `handoff` rebinds the unit to the chosen candidate and appends the finished segment to `workflow_history`, one flow-style line:

```yaml
workflow: spec-driven
workflow_hash: sha256:74bc...
workflow_history: [{workflow: triage, hash: 'sha256:a017...', completed: '2026-10-13', last_decision: 2}]
```

Binding updates replace the whole value of the keys they write, including every line of a block-style value, and keep every other frontmatter line and the body. An anchor without frontmatter (read as unbound) gets a block holding the binding. The anchor is replaced atomically (a temporary file in its directory, with its permission bits), so a failed write leaves it intact; a `handoff` whose anchor cannot be rewritten removes the decision record it wrote for `--workflow`. `last_decision` is the highest decision sequence number when the segment ended; decision records up to it belong to finished segments. After a handoff, `next` evaluates the new workflow from its first stage against the unit's files; finished segments are never re-evaluated, and drift applies to the current binding only.

On `next` (the policy lives in the library, `Workspace.evaluate_unit`):

- Unbound anchor: evaluated against `--workflow` or the configured default; output says `bound=no`.
- Bound, hash matches: normal evaluation.
- Bound to another workflow than the one evaluated (`--workflow`): no drift; `[BOUND_ELSEWHERE: workflow=<bound id>]` and JSON `bound_elsewhere` name the binding.
- Bound, hash differs, a stage is current: refused with a `WORKFLOW_DRIFT` advisory (`BLOCKED`) on stderr whose `[DETAIL]` lines carry the recorded and current hashes, exit `1`. Run `bind` to accept the reviewed change. The anchor's `status` field does not change this.
- Bound, hash differs, no stage is current (`[STAGE: - complete=true]`): evaluated against the current definition and reported as `[DRIFT: ...]`; a finished unit is never blocked.
