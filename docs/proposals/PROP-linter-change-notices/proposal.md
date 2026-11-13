---
id: PROP-linter-change-notices
title: Non-blocking rule notices for changed code
summary: "Introduce a distinct notice severity for change-scoped linter guidance while preserving warning semantics. Define changed-block targeting and read-time context so agents can review relevant considerations without remediation or approval records."
status: reviewing
created_at: 2026-11-11
target_area: governance/
priority: low
size: M
planning_effort: medium
dev_effort: high
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/rules/
    - packages/devkit/src/devkit_agt/features/gate/usecases/gates/rules.py
    - packages/devkit/src/devkit_agt/features/gate/models/errors.py
    - packages/devkit/tests/unit/features/rules/
    - packages/devkit/tests/integration/features/rules/
    - packages/devkit/tests/integration/features/gate/
    - packages/devkit/tests/integration/features/workflow/
    - packages/devkit/tests/e2e/features/gate/
    - packages/devkit/README.md
    - docs/capabilities/governance/CAP-GOV-rules-engine.md
    - docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md
    - docs/capabilities/governance/CAP-GOV-rule-authoring.md
    - docs/capabilities/gate/CAP-GATE-commit-gates.md
    - docs/development/reference/rules.md
    - docs/decisions/
  excludes:
    - packages/devkit-dist/
    - packages/devkit-mcp/
    - packages/devkit-spec/
    - packages/devkit/src/devkit_agt/features/workflow/
    - packages/devkit/src/devkit_agt/features/rules/services/builtins/secret_leak/
    - .devkit/architecture.toml
task_kind: feature
workflow: sdd-proposal
---

# [PROP-linter-change-notices] Non-blocking rule notices for changed code

## 1. Background & Hypothesis

Some edits deserve a contextual reminder even when the result is valid. Adding a broad exception handler can
justify checking whether failure becomes indistinguishable from success; changing a public signature can justify
checking callers. Neither trigger alone proves a defect or requires a fix.

Warnings should retain their meaning as suspected problems that warrant review and possible correction.
Reporting these reminders as warnings dilutes that signal. Including them in hygiene creates recurring work for
conditions that only need consideration when they change.

Hypothesis: a distinct linter notice severity, scoped to relevant changed blocks, can supply timely guidance
without creating unresolved violations, approval requests or maintenance obligations. This remains a low-priority improvement. Planning prepares the direction for explicit acceptance and does not start implementation.

Current rule contracts expose `Severity.ERROR`, `Severity.WARNING` and `Severity.INFO`, file targets and Git
snapshot metadata. They do not expose a shared changed-hunk API. The Agent Advisory Protocol already distinguishes
`NOTICE` from `WARNING`; its notice level does not affect exit status, including under `--strict`.
Related contracts: `CAP-GOV-rules-engine`, `CAP-GOV-evaluation-lifecycle`, `CAP-GOV-rule-authoring`,
`CAP-ADV-agent-advisory-protocol` and `CAP-HOST-lifecycle-observation`.

## 2. Planning Decisions

The recommendation is one cohesive `sdd-spec-feature` at size `M`. `PADR-change-scoped-rule-notices` records the lasting
contract choice. Implementation remains subject to `plan-accept` and `proposal-handoff`.
`MAT-linter-notice-planning` records the source inspection at `aa6c51dc3148efba121bc54c8e582a59aacd11d1`.

| Question | Recommended resolution | Consequence |
| --- | --- | --- |
| Q1, severity | Add `Severity.NOTICE = "notice"`; keep `Severity.INFO = "info"` distinct, with its wire value and settings valid. | Additive API and summary count; no silent migration or alias. |
| Q2, evidence | Build immutable before/after changes from the exact evaluated source pair; expose old and new ranges. | Staged/CI rules never read unstaged bytes for either side. |
| Q3, semantic scope | Require a rule's emitted finding to carry affected construct evidence intersecting an old or new changed range. | A finding may point to a construct header outside added lines, and deletion can trigger it. |
| Q4, read surface | Add explicit host-neutral `devkit rules context FILE` returning change status, ranges, bounded excerpts and matching notices. | Works without native-read interception, hooks, MCP or a host feature edge; agents call it alongside their file read. |
| Q5, repetition | Only `rules context --session TOKEN` suppresses already-delivered identical notice fingerprints in transient state. | Ordinary rule checks remain deterministic and unsuppressed. |

Development effort is `high`: this adds an exported rule API and machine-readable CLI contract used by external
bundles. Planning effort remains `medium`; one isolated challenger reviews this recommendation.

### Alternatives considered

1. Treat reminders as warnings. Rejected: strict rule checks can become negative and warnings lose their suspected-defect meaning.
2. Rename or alias INFO to NOTICE. Rejected: existing rule imports, configured severity values and consumers would silently change meaning.
3. Add NOTICE plus explicit change evidence and read context. Recommended: keeps the new behavior additive and bounded to a supported surface.
4. Inject context into every host's native file reads. Rejected: `CAP-HOST-lifecycle-observation` exposes advisory Codex
   lifecycle hooks, not a universal typed file-read event. This exceeds the stated excluded scope.

## 3. Proposed Design & Impact

### 3.1 Severity and output

- `Severity.NOTICE` is a rule finding severity, separate from the result's `notices` advisory array.
- Existing `Violation` and `EvaluationResult.violations` remain the rule-finding API, including NOTICE findings.
  Text remains `[VIOLATION: ... severity=notice ...]`; its status is `consider`, not `open`, `fixable` or `fixed`.
  JSON retains the existing finding fields with `severity: "notice"`; the summary adds `notices=N` while retaining
  `errors`, `warnings`, `infos`, `fixed` and `rules` with their existing meanings.
- A notice's message states the concrete consideration. It has no remediation, autofix, acknowledgement, waiver,
  promotion or unresolved-work requirement. NOTICE findings are excluded from remaining-violation/promotion counts.
  Invalid notice findings that request repair or claim a fix are rule-execution problems rather than silently altered findings.
- Notice-only results exit 0 with and without `--strict`, pass the `rules-check` gate and pass workflow `lint-clean`.
  Error, warning, INFO and rule-execution behavior stays unchanged. A project's explicit severity override still
  chooses the effective severity: an override to warning or error is then a warning or error, not a NOTICE finding.
- The gate returns NOTICE-level advisories for notice findings with stable code `GATE_RULES_NOTICES`, locations and
  the consideration; it never folds them into `GATE_RULES_WARNINGS`. Existing strict-warning exemptions remain unchanged.
  Workflow `lint-clean` continues testing blocking findings only; it creates no notice acknowledgement check.

### 3.2 Change evidence independent of severity

`BaseRule` gains optional `change_scope = True` (default false, read optionally for existing rule classes).
A change-scoped warning remains possible. A change-scoped rule is a linter rule, is omitted in hygiene even though
hygiene ordinarily includes linter rules, and cannot be parked/promoted through hygiene; an incompatible phase
or phase override is a policy error. Existing rules without the declaration keep their selection behavior.

`RuleContext` gains immutable change evidence, captured once for the evaluation, with source mode and base identity,
logical path, change status, old/new path, before/after content identities and old/new line ranges. Ranges use
1-based half-open intervals; a zero-length range is an insertion/deletion anchor, not an empty change. Source bytes
are read through the evaluated cache or the named Git object. Public helpers expose before text and changed
construct intersection; no model starts Git or reads disk. Repositories capture Git data, services calculate ranges,
and the project use case supplies the evidence. No new feature dependency is needed.

| Source | Before | After | Path handling |
| --- | --- | --- | --- |
| Working-tree linter | HEAD blob, or empty for an unborn repository | The run's cached working bytes, including staged plus unstaged content | Explicit file/directory targets intersect changed paths; no targets considers all tracked edits and nonignored untracked files. Unchanged constructs yield no findings. |
| Staged | The snapshot's HEAD tree, or empty initial tree | The captured index tree, including the commit gate's alternate index | Untracked and unstaged bytes are absent. Partial staging evaluates only the index content. |
| CI | The merge-base commit already selected by `--ci --base REF` | The captured HEAD tree | No working-tree bytes, including rule code/configuration, can affect either side. |

Use Git with external diff/text conversion disabled and rename detection disabled. A rename is an old-path deletion
and new-path addition; this is reported explicitly, not inferred as a semantic move. A deleted path has before
bytes/ranges and no after bytes; its findings use the old logical path and line. Existing rules continue receiving
only present target files; change-scoped rules can also enumerate the selected deleted evidence. Excluded paths
remain excluded. A mode-only change supplies status but no textual ranges and cannot alone trigger a text notice.

A semantic rule selects a function, handler or other construct from before/after text, then emits only when its
recorded affected construct intersects the corresponding changed range. Deleting a handler body can therefore
report at its old header; editing an unrelated function cannot trigger the unchanged handler. The engine validates
that finding evidence belongs to the selected path/source pair and overlaps a changed range. The authoring contract
requires tests of the rule's semantic choice; overlap alone does not prove that a broad whole-file span is useful.
A representative Python broad-exception fixture, not a shipped catalog of reminder rules, exercises this contract.

If Git evidence is unavailable in an ordinary working-tree check (outside Git, unreadable HEAD, binary/undecodable
content or a content race), omit only the affected change-scoped evaluation with stable reason
`RULE_CHANGE_EVIDENCE_UNAVAILABLE` and a NOTICE-level advisory; never substitute a whole-file historical scan.
Independent rules still run. Snapshot capture/materialization failures retain their existing failure/exit-2 behavior.
A changed file whose captured bytes change again is unavailable for that run; never combine mismatched text/ranges.

### 3.3 Explicit read-time context

Proposed synopsis: `devkit rules context FILE [--session TOKEN] [--format text|json]`. It is a read companion,
not a general file-reading command. It always returns working-tree versus HEAD change status and old/new hunk
ranges, even when no rule matches, the file is unchanged, or the file has been deleted. A deleted tracked FILE is
valid for this command; an unknown or outside-workspace path is `RULES_TARGET_INVALID`. Untracked nonignored files
are additions; explicitly named ignored files retain existing explicit-target behavior but source exclusions apply.

The result carries up to 20 hunk excerpts, at most 20 lines per side per hunk and 8192 UTF-8 bytes in total, with
explicit omitted-hunk/line/byte counts. Ranges and source identities remain available when excerpts are truncated.
Changed content is deliberately returned to the calling agent only on this explicit request and is never logged
or stored in the dedupe memo. Escaped JSON/sentinel fields keep control characters from breaking the protocol.

The use case evaluates only applicable change-scoped NOTICE rules for this FILE. It returns original rule-finding
objects and their consideration messages; it does not run unrelated blocking rules or fixes. `--session` never
suppresses hunk evidence. JSON is one object containing `file`, `change`, `hunks`, `findings`, `suppressed`, `omitted`
and the ordinary advisory `notices` field. Text uses `[RULE_CONTEXT: ...]`, `[CHANGE_HUNK: ...]`, the ordinary
`[VIOLATION: ... severity=notice status=consider ...]` and one summary. An unavailable evidence result returns
`change.status=unavailable`, no guessed hunks/findings and `RULE_CHANGE_EVIDENCE_UNAVAILABLE`; this is not an unchanged result.

Without `--session`, every explicit context request returns all matching notices. With `--session`, the caller
provides an opaque random token for one agent session. The memo stores only hashed token/fingerprints and delivery
metadata under `.devkit/transient/rules/read-notices/`, never source, native host payloads or raw session IDs.
A fingerprint includes rule ID, executing rule fingerprint, effective settings, logical path and the exact relevant
before/after construct bytes; unrelated edits elsewhere do not reissue an identical consideration.
The session boundary is the token, at most 24 hours from first use and 2048 delivered fingerprints. At the bound,
return `RULE_READ_SESSION_EXPIRED`, stop suppressing and require a fresh token for another suppression session.
The command remains useful without a token. A subsequent relevant content edit produces a new fingerprint.

Write only fingerprints actually returned, after successful rendering preparation. Use atomic replacement and the
existing project lock to serialize memo updates; concurrent context calls with one token cannot both claim first
delivery after a successful write. If the memo cannot be safely read/locked/written, return the unsuppressed notices
with `RULE_READ_SESSION_UNAVAILABLE` (NOTICE), without a retry loop. A crash between memo commit and host display
can suppress a notice on retry; exactly-once delivery to the model is not claimed. Session files are derived,
ignored, safely prunable state, never a suppression/approval database.

### 3.4 Scope and verification

The implementation changes only the rules feature, its gate adapter and their documented public contracts.
`target-docs.md` names the Living Spec targets and candidate code paths. `CAP-ADV-agent-advisory-protocol` and
`CAP-HOST-lifecycle-observation` remain governing read references; neither changes. The original `governance/`
boundary was a document-area shorthand rather than an existing source owner. The corrected boundaries admit the
actual feature and its tests. The `docs/decisions/` exclusion is removed to admit promotion of the PADR required by
this changed lasting API contract; it does not authorize editing an existing accepted ADR.

Scope excluded:

- Converting existing warning or INFO rules without a separate semantic review.
- A catalog of production reminder rules; the representative rule remains a test fixture.
- Native file-read interception, hook registration, MCP transport or another host adapter.
- Acknowledgement databases, approval gates, permanent per-file suppressions and judgment-based autofixes.
- New cross-feature edges or a workflow implementation change.

Acceptance and planned checks (each original criterion is retained):

| ID | Given / When / Then | Verification |
| --- | --- | --- |
| AC-N1 | Given a changed broad exception construct, when the fixture runs, then one NOTICE is returned; unchanged or unrelated edits yield none. | Rule-context and semantic fixture unit tests. |
| AC-N2 | Given a deletion in the checked construct, when evaluated, then a notice can report its old path/header even outside added lines. | Before/after and deletion-only Git integration cases. |
| AC-N3 | Given notice-only results, when ordinary, strict, gate and lint-clean checks run, then they pass; an existing warning retains its strict-CLI behavior. | CLI/gate/workflow integration matrix with existing severities. |
| AC-N4 | Given change_scope rules, when hygiene runs or an incompatible phase override is configured, then hygiene never executes the rule and invalid policy is explicit. | Phase/evaluator tests; historical whole-tree trigger case. |
| AC-N5 | Given staged/CI input and different unstaged code/config/rule content, when evaluated, then findings and hunks depend only on the exact selected source pair. | Partial staging, alternate index, CI, deletion, rename-as-delete/add, untracked and initial commit snapshot tests. |
| AC-N6 | Given mixed severities, when text and JSON render, then notice counts/locations/IDs differ from warning/INFO and notice status carries no repair obligation. | Renderer and subprocess contract tests. |
| AC-N7 | Given FILE and a session token, when context is read twice, then hunk evidence is returned twice and identical notices once; a relevant edit returns a fresh notice. | Memo concurrency, expiry/cap, corruption/lock failure, no-match/unchanged and excerpt-bound tests. |
| AC-N8 | Given legacy INFO imports/settings/findings, when the additive API is installed, then they keep `info` and the existing counts/exit behavior. | Legacy rule/plugin compatibility fixtures. |
| AC-N9 | Given unavailable working evidence or failed snapshot capture, when evaluated, then omission versus execution-failure codes and independent-rule results remain distinct. | Outside-Git, binary/decode, capture race and failing Git tests. |

No runtime or timing improvement is claimed. Development validates with repository lint, types and
`just test-affected --base <unit-base>` preserving full fallback, plus targeted source-specific checks and installed
CLI/gate coverage. These are future checks; Planning runs document and envelope validation only.

## 4. Lifecycle & Retirement Criteria

Keep `priority: low`; this batch explicitly selects Planning. Acceptance settles the additive severity, exact
source evidence and explicit read companion together. `plan-accept` integrates only the Planning documents.
`proposal-handoff` then creates the spec worktree and promotes `PADR-change-scoped-rule-notices`; Development
implements AC-N1 to AC-N9 and reconciles the named Living Spec contracts. No criterion is silently deferred.

If the owner requires automatic context on native reads rather than the explicit companion, retain this proposal
in review and revisit scope before handoff; the current design makes no universal-host delivery claim.
