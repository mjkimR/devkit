---
id: CAP-DLV-workflow-definitions
title: "Workflow Definitions and Checks"
summary: "Workflow schema, stage definitions, entry and exit checks, and workflow ID bindings."
area: delivery
status: active
created_at: 2026-10-17
---

# [CAP-DLV-workflow-definitions] Workflow Definitions and Checks

**Package**: `devkit.workflow`. Review envelopes: `CAP-DLV-workflow-envelopes`; what `next` prints: `CAP-DLV-cli-and-output`.
**Related**: `CAP-DLV-workflow-orchestration`, `CAP-GOV-rule-authoring`.

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
| `checks` | no | Extra `runner` or `human` checks the workflow declares. Each has `name` (`[a-z][a-z0-9-]*`), `class` and `description`, and nothing else. Names must be unique, and must not collide with built-in checks, nor with a gate of the workflow (so `--given` stays unambiguous). |
| `stages` | yes | Ordered stage list, at least one. |
| `next` | no | Workflows this one may hand a completed unit to. See [Handoff Candidates](#handoff-candidates). |
| `layout` | no | Mapping with any of `work_dir`, `unit_path`, `anchor`; each overrides the `[workflow]` default for this workflow's units and is validated like the configuration key. See `CAP-DLV-workflow-orchestration`. |
| `gates` | no | Mapping of a gate name (the `human_gate` of a stage) to `{answer: record \| given, policies: [...]}`. `answer` defaults to `record`. `given` means a person's approval reaches the engine as `next --given <gate>` and the executor writes no decision record: use it for a gate asked after the work is final, where a record would need one more commit. Evaluation does not change (a record still satisfies the gate); the gate's `[REQUEST]` and `show`'s `[GATE]` line end with `answer=given`. `policies` narrows the `[workflow.approvals]` policies the gate accepts to a non-empty list of distinct values of `ask`, `auto` and `off` that includes `ask` (the policy of an unset gate); a methodology fixes a gate to a person with `[ask]`. A configured policy outside it stops every command that evaluates the unit with `WORKFLOW_GATE_POLICY` (`CAP-DLV-workflow-orchestration`), and `show`'s `[GATE]` line ends with `policies=...`. A name that is no stage's gate, or another key or value, is an error. |

### Stage Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Unique within the document; matches `[a-z][a-z0-9-]*`. Shared across definitions (see [Shared Stages](#shared-stages)). |
| `name` | string | Display name. |
| `human_gate` | `false`, `true` or string | `true` names the gate after the stage id; a string names a shared gate (`[a-z][a-z0-9-]*`, so `[workflow.approvals]` can name it). `handoff` is reserved. See `CAP-DLV-workflow-orchestration`. |
| `optional` | `true` or `false` | When unmet, the stage is passed over instead of becoming current. Since it never becomes current, nothing lists its requests: a `human_gate` is satisfied only by `approvals.<gate>=auto`, `--given <gate>` or a record a host writes, a `human` exit check only by `--given` or such a record. `validate` reports either as a `WORKFLOW_OPTIONAL_STAGE_UNASKED` warning; the definition stays valid and usable. |
| `exception` | `true` or `false` | Never evaluated; documents an out-of-band path. |
| `entry` | list of checks | Preconditions. Informational: listed by `show` and in the JSON `stage` object, never evaluated. |
| `exit` | list of checks | The stage is done when every exit check is satisfied. |
| `artifacts` | list of strings | Files or things the stage produces. Informational. |
| `skills` | list of strings | Skills that perform this stage; the first is `[NEXT_SKILL]`. |
| `role` | string | `developer`, `-`, or a subagent role name, which must be in the project's `CAP-DLV-workflow-orchestration` when one is known. |
| `isolation` | string | `none`, `preferred`, `required`. A non-developer role with isolation other than `none` yields `[DELEGATE]`. It asks for a subagent's separate context, not a Git worktree; the worktree and pull request policy is `[worktree]` (`CAP-WT-task-worktrees`). |
| `returns` | list of `{to, when}` | Stages this stage may return to and why. `to` must name a stage in the same document. Taking a return is `devkit workflow return --to <stage>` (`CAP-DLV-human-interaction`). |

Unknown document or stage keys, malformed or duplicate ids, malformed gate names, duplicate or colliding declared checks (each reported once; the other declared checks stay usable), unregistered checks, `runner` or `human` checks in a `next` candidate's `when`, malformed check invocations, a `file` argument outside the unit directory (absolute or with `..`), unknown `returns.to` targets, invalid `isolation` values and unknown roles are validation problems, which `devkit workflow validate` reports with the stage id and field. An `optional` stage with a `human_gate` or a `human` exit check is not a problem but a warning (`WORKFLOW_OPTIONAL_STAGE_UNASKED`, `OptionalStageWarning`, from `definition_warnings`): `validate` lists it under `notices` (text: a `[WARN]` block on stderr), exits `0` for it, and `1` only under `--strict`; every other command uses the definition as usual. A value of the wrong type (`optional: "false"`, `role: 3`), an unknown key inside a `returns`, `checks` or `next` item, and a malformed `layout` mapping are structural errors reported with the file.

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

Eligibility is computed from checks so that an automatic handoff is deterministic; whether a person or the engine chooses is the `CAP-DLV-workflow-orchestration` policy. The candidate's own first stage then evaluates the unit's existing files, so a candidate whose entry checks require earlier artifacts is naturally filtered by `when`.

## 2. Checks

A check reference is `name` or `name(arg1 arg2 ...)`. Arguments are whitespace-separated tokens; nesting and an empty argument list are malformed. Aliases take no arguments. `devkit workflow checks` lists every registered check.

| Class | Who evaluates | Satisfied when |
| --- | --- | --- |
| `disk` | the engine, from files in the unit directory and Git | the primitive holds |
| `lint` | the engine, by running `devkit.rules` | no violation in the unit's files |
| `runner` | an external runner (CI); declared only | named in `--given` |
| `human` | a person; declared only | an accepted `check:<name>` decision record of the current segment for the stage being evaluated, or named in `--given` |

### Primitives

| Name | Parameters | Description |
| --- | --- | --- |
| `file-exists` | `file` | the file exists in the unit directory (every `file` argument is a relative path inside the unit) |
| `frontmatter` | `file field value` | the file's top-level frontmatter field equals the value, or one of the values `value` joins with `\|` (`frontmatter(proposal.md status reviewing\|accepted)`) |
| `tasks-checked` | `file` | the file has at least one `- [ ]`/`- [x]` task and none unchecked; items inside YAML frontmatter or fenced code are not tasks (the counter is `devkit.rules.count_tasks`, shared with rules) |
| `not-skeleton` | `file` | the file is missing or has no line equal to `<!-- devkit:skeleton -->` |
| `envelope-completed` | `kind` | the deciding `envelopes/<kind>-NN.yaml` of the current segment (`CAP-DLV-workflow-envelopes`) has `status: completed` and no open finding |
| `envelope-check-pass` | `kind key` | the deciding envelope is completed and `checks.<key>` starts with `PASS` |
| `revision-ancestor` | `ancestor-kind descendant-kind` | `diff_scope.head` of the latest ancestor-kind envelope is a Git ancestor of, or equal to, that of the latest descendant-kind envelope; both must be hexadecimal commit ids. When Git cannot answer (not a repository, an unknown commit as in a shallow clone, a timeout) the check is unsatisfied and `evaluated=false`, with Git's error in the detail |
| `lint-clean` | none | `devkit.rules` reports no violation for files under the unit directory (`CAP-DLV-workflow-orchestration`); the detail quotes the first three violations and counts the rest, naming `devkit rules check <unit>`. Temporary files of writes in progress (`.<name>.<12 hex digits>.tmp`) are not linted; another file removed while the rules run can fail the run, since the rule engine refuses a target that no longer exists, and running the command again resolves it. A unit directory that resolves outside the workspace root (an absolute `--unit` path outside it, or a symbolic link leaving it) cannot be linted: the check fails with a `PATH_UNSAFE` lint error; an absolute `--unit` inside the root is linted as usual |

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

### Implicit Gate Check

A stage with `human_gate` carries an implicit `human` check named `gate:<gate>`. It is asked only once every exit check of the stage holds: until then it is not listed under `[UNMET]`, no request is emitted, `[WAITING]` does not name it and `[GATE]` shows it as `satisfied=no`. Then it is listed under `[UNMET]` like any other check. It is satisfied by an accepted `gate:<gate>` decision record of the current segment, by `--given <gate>`, or by the `auto` policy; the whole stage is skipped under `off`, and any stage is skipped by `[workflow.stages] <id> = "off"` before its checks are evaluated (`CAP-DLV-workflow-orchestration`).

## 3. Binding

`new` and `bind` write `workflow: <id>` into the anchor's frontmatter. The binding records only the id, which every unit command looks up among the discovered definitions, so `--workflow <path>` binds only the file discovered for its id (for example `.devkit/workflows/<id>.md`); any other definition file is refused with `WORKFLOW_NOT_BINDABLE` before anything is written. `next --workflow <path>` still evaluates a unit against such a file without binding it. `handoff` rebinds the unit to the chosen candidate and appends the finished segment to `workflow_history`, one flow-style line:

```yaml
workflow: spec-driven
workflow_history: [{workflow: triage, completed: '2026-10-13', last_decision: 2}]
```

Binding updates replace the whole value of the keys they write, including every line of a block-style value, and keep every other frontmatter line and the body. An anchor without frontmatter (read as unbound) gets a block holding the binding. The anchor is replaced atomically (a temporary file in its directory, with its permission bits), so a failed write leaves it intact; a `handoff` whose anchor cannot be rewritten (any error, an interrupt included) removes the decision record it wrote for `--workflow`. Only a process killed outright between the two writes leaves that record behind: an accepted `handoff` choice in the unchanged segment, which the next `handoff` uses. `last_decision` is the highest decision sequence number when the segment ended; decision records up to it belong to finished segments. After a handoff, `next` evaluates the new workflow from its first stage against the unit's files; finished segments are never re-evaluated.

On `next` (the policy lives in the library, `Workspace.evaluate_unit`):

- Unbound anchor: evaluated against `--workflow` or the configured default; output says `bound=no`.
- Bound: evaluated against the current definition; changes take effect without rebinding.
- Bound to another workflow than the one evaluated (`--workflow`): `[BOUND_ELSEWHERE: workflow=<bound id>]` and JSON `bound_elsewhere` name the binding.
