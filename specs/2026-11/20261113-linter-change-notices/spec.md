---
id: SPEC-linter-change-notices
title: Non-blocking rule notices for changed code
summary: "Adds nonblocking NOTICE findings, exact change evidence and an explicit bounded read-context companion while preserving INFO, warnings and snapshot semantics."
status: planned
created: 2026-11-13
related_capabilities: [CAP-GOV-rules-engine, CAP-GOV-evaluation-lifecycle, CAP-GOV-rule-authoring, CAP-GATE-commit-gates]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-linter-change-notices] Non-blocking rule notices for changed code

## 1. Problem Statement & Motivation

Contextual guidance about changed constructs needs a nonblocking severity without weakening warnings or INFO compatibility. `ADR-change-scoped-rule-notices` selects additive NOTICE, exact source evidence and an explicit read companion. `MAT-linter-notice-planning` contains the source baseline.

## 2. User Stories

- **US-1**: As a rule author, I can express a change-scoped consideration without creating repair obligations.
- **US-2**: As an agent, I can request bounded changed-file context and avoid repeated identical session reminders.

## 3. Non-Goals

- **Scope Excluded**: Native read interception, host/MCP adapters, production reminder catalogs, migrations of existing rules, acknowledgements and permanent suppressions, new feature edges and workflow implementation changes.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Relevant semantic edits
- **Given** a change-scoped representative broad-exception rule and changed source.
- **When** the linter evaluates the source.
- **Then** a relevant construct yields one NOTICE and unchanged or unrelated constructs yield none.

### [AC-02] Deletion evidence
- **Given** a changed construct with relevant deleted text.
- **When** the rule reports its before-side semantic span.
- **Then** the engine accepts a notice at the old path/header even outside added lines.

### [AC-03] Nonblocking notices
- **Given** notice-only, warning and error findings.
- **When** ordinary, strict, gate and workflow lint-clean evaluation run.
- **Then** NOTICE alone passes each boundary; legacy warning and error semantics remain unchanged.

### [AC-04] Change scope and hygiene
- **Given** a rule declares change_scope.
- **When** phase selection or policy validation runs.
- **Then** hygiene omits the rule and an incompatible phase or promotion declaration is an explicit policy error.

### [AC-05] Exact source snapshots
- **Given** staged or CI snapshots with different unstaged rule/config/product bytes.
- **When** change evidence and rules are evaluated.
- **Then** both sides depend only on the captured Git source pair, including initial trees, partial/alternate indexes, deletion and rename-as-delete/add.

### [AC-06] Finding output
- **Given** mixed ERROR, WARNING, INFO and NOTICE findings.
- **When** text and JSON render.
- **Then** the additive notice count and severity are distinct and notice status is consider with no repair obligation.

### [AC-07] Read companion and dedupe
- **Given** a FILE and optionally one session token.
- **When** rules context is called repeatedly or the relevant construct changes.
- **Then** hunk evidence always returns; identical notices suppress only with the token and relevant changes reissue within bounded state.

### [AC-08] Legacy INFO compatibility
- **Given** a legacy rule imports INFO and uses existing settings.
- **When** it is installed with the additive API.
- **Then** the info wire value, settings, counts and exit behavior remain unchanged.

### [AC-09] Unavailable evidence
- **Given** unavailable working-tree Git/text evidence or failed snapshot capture.
- **When** evaluation runs.
- **Then** affected change rules omit with RULE_CHANGE_EVIDENCE_UNAVAILABLE while snapshot failures retain exit 2 and independent rules still run.

### [AC-10] Autofix freshness
- **Given** another fixer adds or removes a representative notice trigger.
- **When** the single convergence recheck runs.
- **Then** fresh immutable after-evidence is compared to the original base; successful paths refresh and unknown writes refresh all evidence.

## 5. Contract Details

The accepted Planning AC-N1 through AC-N10 map in order to AC-01 through AC-10 above. The following source-pair, output and state bounds remain part of the agreed scope.


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

`RuleContext` gains immutable change evidence, captured immutably for each evaluation pass, with source mode and base identity,
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

For working-tree `rules fix`, keep the original before/base identity across the one repair pass and one recheck.
After successful fixes, refresh cached after-content, content identities, hunks and affected-construct evidence for
every returned modified path before the recheck. After a failed fixer with unknown writes, invalidate and recapture
all working-tree change evidence before the existing all-active recheck. Each pass receives a fresh immutable
evidence object; no initial notice survives merely because its trigger existed before a successful repair. If
fresh capture fails, apply the stated unavailable-evidence omission rather than matching old ranges to fresh text.
Snapshot runs remain read-only and never enter an autofix pass. An integration case has another fixer introduce
and remove the representative trigger, proving the final findings reflect the single recheck's bytes.

If Git evidence is unavailable in an ordinary working-tree check (outside Git, unreadable HEAD, binary/undecodable
content or a content race), omit only the affected change-scoped evaluation with stable reason
`RULE_CHANGE_EVIDENCE_UNAVAILABLE` and a NOTICE-level advisory; never substitute a whole-file historical scan.
Independent rules still run. Snapshot capture/materialization failures retain their existing failure/exit-2 behavior.
A changed file whose captured bytes change again is unavailable for that run; never combine mismatched text/ranges.

### 3.3 Explicit read-time context

Synopsis: `devkit rules context FILE [--session TOKEN] [--format text|json]`. It is a read companion,
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
| AC-N10 | Given another fixer introduces or removes the representative trigger, when the single recheck runs, then fresh after-evidence against the original base yields only the final notices; unknown writes refresh all evidence. | Autofix integration cases, successful output paths and failed-fixer all-active recheck. |

No runtime or timing improvement is claimed. Development validates with repository lint, types and
`just test-affected --base <unit-base>` preserving full fallback, plus targeted source-specific checks and installed
CLI/gate coverage. Empirical host/model trials are best effort and are not an implementation gate.

