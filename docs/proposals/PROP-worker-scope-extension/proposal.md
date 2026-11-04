---
id: PROP-worker-scope-extension
title: Tiered write boundaries for delegated workers
summary: Splits a delegated worker's write boundary into an extensible estimate and a hard deny list, so a worker records and justifies an adjacent-path extension instead of stopping or having its whole result rejected, in local and cloud runs alike.
status: accepted                     # draft | reviewing | accepted | rejected
created_at: 2026-11-04
target_area: delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/development-worker.md.jinja
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/code-reviewer.md
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-tasks/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/worker-records.md
    - packages/devkit-spec/src/devkit_spec/features/worker/
    - packages/devkit-spec/src/devkit_spec/features/entrypoints/repositories/bundle.py
    - packages/devkit-spec/tests/unit/features/
    - packages/devkit-spec/tests/unit/features/worker/
    - packages/devkit-spec/tests/integration/features/worker/
    - packages/devkit-spec/tests/integration/bundles/spec/
    - packages/devkit/src/devkit_agt/features/workflow/cli/envelope.py
    - packages/devkit/src/devkit_agt/features/workflow/models/envelope.py
    - packages/devkit/src/devkit_agt/features/workflow/services/envelope/
    - packages/devkit/src/devkit_agt/features/workflow/usecases/envelopes.py
    - packages/devkit/tests/integration/features/workflow/
    - docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    - docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
    - docs/decisions/2026-11/20261102-orchestration-workers.md  # partial-supersession annotation only at handoff
  excludes:
    - docs/decisions/  # except the exact annotation-only path above and standard PADR promotion
    - .devkit/managed/
    - packages/devkit-spec/src/devkit_spec/features/workflow/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-worker-scope-extension] Tiered write boundaries for delegated workers

## 1. Background & Hypothesis

`spec-tasks` treats `_Boundary:` as an estimate, but `development-worker` and its Host validation reject any
unlisted write. A required sibling module, test helper or contract repair therefore causes an operator round trip.
The existing `(sync output)` exception already admits a recorded class of change-caused paths.

The draft assumed that worker-envelope authoring belongs to `devkit-spec`. It belongs to
`devkit_agt.features.workflow`; `devkit_spec.features.worker` reads that model. The evidence and rejected options
are in `materials/implementation-evidence.md`. The decision is
`PADR-recorded-adjacent-path-extensions-for-development-workers`.

Hypothesis: permit a task-linked adjacent-path extension under the same approved goal, record it before its first
source commit, and review its necessity. Retain explicit payload denies and protected classes as stop conditions.
The change prevents accidental boundary misses; it does not attempt to make a repository owner unable to bypass
local checks.

## 2. Technical Spike Questions

- **Q1 — Adjacent class**: use project ownership contracts, checked by the reviewer, rather than infer a universal
  ownership layout or add settings. An extension is a literal file within an already-declared feature ownership
  root, its corresponding test mirror, or an exact existing Living Spec document that restates the changed
  behavior. A project without a documented feature root uses the declared file's parent directory; no package-wide
  root is inferred. A test mirror must be identified by project guidance or the plan. A Living Spec extension
  names the affected contract ID in its reason. Other packages/features, a new feature edge and unrelated docs
  are not adjacent. Forced sync outputs retain their existing separate procedure. Lockfiles and other generated
  files need explicit initial scope; they are not a general extension class.
- **Q2 — Hard denies**: retain a short prose contract and payload-specific exact paths/prefixes. Explicit payload
  denies always win. For extensions, protected classes are other units/proposals, `.devkit/`, host projections,
  governance-rule implementations, architecture/dependency declarations, CI/release configuration, and paths outside
  the repository. A path deliberately included in initial Tier A scope may implement that task's governance or
  architecture work; an extension cannot grant itself that authority. Tests may be strengthened or updated for
  approved behavior, but never weakened to pass a check. No deny-list configuration is added.
- **Q3 — Evidence**: add a typed worker-only `scope_extensions` list with `{path, task, reason, requirements}` and
  `devkit workflow envelope worker --scope-extensions-file <file|->` in `devkit-agt`. The list contains exact
  repository-relative file paths, positive task ordinals from the checklist scanner, nonempty reasons and AC IDs.
  Duplicate paths, absolute/parent/glob paths, missing values and use on another envelope kind are refused.
  Existing envelopes omit the field and remain valid. Keep the task annotation `(scope extension: <reason>)`;
  the annotation and record use the same reason and task. A reason is one nonempty line without parentheses, so the existing parenthesized-note grammar remains unambiguous. The shared boundary parser exposes annotations
  additively without changing `TaskBoundary.values` or existing callers.
- **Q4 — Cloud verification**: ship the same worker/reviewer contract for local and cloud execution. `inspect` is
  informational and remains optional; this change does not claim that Hub calls it. The mandatory medium/high
  reviewer and the low-effort self-review judge adjacency, necessity, requirements and protected classes.
  No autohub code is changed, and adding a Hub inspect invocation is not required or promised by this proposal.
- **Q5 — Boundary syntax**: allow literal file and directory prefixes; both already work in `inspect`. Do not
  recommend globs: `inspect.prefix` rejects them and entrypoint normalization rejects them too. Directory scope
  stays narrow enough for independent verification; an extension annotation always names an exact file.

## 3. Proposed Design & Impact

### 3.1 Three tiers

| Tier | Admission | Required evidence | Stop condition |
| --- | --- | --- | --- |
| A, declared | The Host's initial payload, the unit's task boundaries and reconciliation targets | Existing records and review | An explicit payload deny or a change beyond the approved goal still stops the run |
| B, extension | An adjacent exact file necessary for an existing task and AC | Annotated owning `_Boundary:`, `scope_extensions` record, reviewer judgment | Missing justification is fixed within scope; a path outside the adjacent class needs Host authority |
| C, denied | No self-admission | `worker` problem naming the required path and recovery | Stop before writing the denied path; preserve partial work |

A worker adds a Tier B path and its reason to the owning task before the source commit that first touches it;
`tasks.md` and the file can be in that same commit. The worker lists every extension in its final or emergency
record; the turn still writes exactly one `worker` envelope. Code review reads the annotation, owning task and AC
before that envelope exists. The final Host/inspect check compares the record with the reviewed annotation; a
changed justification or extension after review is reverified like other changed review input.
For example:

```markdown
- [ ] **Task 1**: Parse a worker record
  - **_Boundary**: `src/app/records.py`, `tests/test_records.py`,
    `src/app/record_validation.py` (scope extension: shares Task 1 parsing validation for AC-01)
  - _Requirements: AC-01_
```

```yaml
scope_extensions:
  - path: src/app/record_validation.py
    task: 1
    reason: shares Task 1 parsing validation for AC-01
    requirements: [AC-01]
```

An extension is not new scope authority for another task, feature or package. Rewriting a path from a denied class
as a directory declaration does not admit it. Sandbox, Git and publication permissions remain independent.

### 3.2 Inspection and compatibility

Preserve `scope` as the existing list, its entry fields, `outside_scope`, and literal prefix matching.
Add top-level `scope_extensions` and `checks.scope_extensions`. A boundary entry may carry additive extension
metadata; the check compares the annotated exact paths and task ordinals with the worker records applicable to
the audited cumulative range. Extension records from earlier turns remain relevant to retained task annotations,
so inspection reads the unit's committed records rather than only the latest run. For a path recorded again,
the highest worker sequence supplies its current metadata. Historical records alone add no path to scope: the
matching annotation must remain on the returned task. A task move or changed reason needs a current matching
record; duplicate paths are forbidden within one envelope, not across successive turns.

For a recorded extension, check that the file is named on its owning task, the reason agrees, each listed AC is
owned by that task, and an extension annotated in the audited range has a matching record. Inspect rejects an
unrecorded extension, a mismatched record or an extension in a mechanically recognizable protected tree with
`SPEC_WORKER_SCOPE_EXTENSION_INVALID` (exit 1, action: correct the record or obtain Host authority). Malformed
input remains a not-run check with a stable input code; it never becomes a pass. The reviewer judges semantic
adjacency, whether a custom project path is protected, whether tests were weakened, and whether work stays in the
approved goal. Inspection does not claim to automate those judgments.

A changed path outside the complete admitted scope still fails `SPEC_WORKER_SCOPE_OUTSIDE`. `--scope` and
`--scope-file` continue to replace the entire derived scope; they are not silently unioned with extension paths.
The Host validates the extension evidence first and includes admitted extensions in an explicit complete scope
when overriding. Passing a narrower explicit scope still fails for its omitted extension. The tool never widens
scope, writes records or grants approval. With no extensions, existing output and checks retain their meaning;
the added list is empty and the added check passes. Existing `(sync output)` receipt checks stay independent.

A new boundary added without an extension annotation is reviewed against the recorded payload and task diff.
No sealed original-boundary journal is introduced: the task documents are already mutable and deliberate
self-reclassification is outside this personal project's threat model. An omitted annotation is a material review
finding, not proof that the change was authorized merely because derived scope includes it.

### 3.3 Review and result acceptance

`spec-review` and the `code-reviewer` contract use the same checks: owning task and AC, necessary adjacent file,
annotation evidence before the final worker record exists, absence of a deny and no weakened tests. The final Host/inspect check enforces annotation/record agreement. A missing annotation/record for an adjacent
file is P2 and can be repaired before the final return. A denied/non-adjacent write or a change outside the approved
goal is P1 and blocks the range. The Host accepts an extension only after these checks and all existing ancestry,
clean-worktree, envelope and cumulative-check conditions hold. A failed range is preserved and recovered through
the existing problem/resolution procedure.

### 3.4 Implementation and Living Spec boundaries

- `devkit-agt` owns the additive worker record model, parser, CLI authoring, validation and serialization. Add the
  corresponding feature-owned integration tests. This is an existing feature, so no new feature edge is needed.
- `devkit-spec` owns boundary annotation exposure, inspect reporting/checks, its tests, the Development worker and
  Code Reviewer contracts, `spec-tasks`, `spec-review`, delegation payload/validation and worker-record guidance.
  Add `subagents/code-reviewer.md` to the implementation scope alongside the declared Development contract.
- Update `CAP-DLV-delivery-workflows` for tier admission, inspection evidence and review; update
  `CAP-DLV-workflow-envelopes` for the optional list and CLI flag. Keep gate names and authority unchanged.
- The PADR partially supersedes `ADR-orchestration-workers` only where every unlisted path currently fails the
  worker result. Handoff promotes the PADR and adds the required partial-supersession annotation; remaining Git,
  sync-output, range and permission decisions stay in effect.
- Selected `spec` bundle source changes run `devkit sync`; tracked projections and the receipt are admitted and
  recorded by the existing sync-output rule. `.devkit/managed/` is never edited directly.

### 3.5 Planning decisions and limits

Use the typed optional list rather than encode records into free-form checks, assumptions or findings. Those
fields do not preserve path/task/AC structure across authoring and parsing. Use review for project-specific
adjacency rather than create a generic ownership registry or add a scope-policy setting. Keep `size: M` and
`dev_effort: medium`: this is one contract change across existing `devkit-agt` and `devkit-spec` features, with
one mandatory Code Reviewer and a separate Reconcile Reviewer for the cross-package reflection.

No live autohub inspection was performed. Its current invocation behavior is outside this repository and is not
needed to establish the shared worker contract. No latency or operator-round-trip reduction is asserted as a
measured outcome.

## 4. Lifecycle & Retirement Criteria

Acceptance and handoff create one feature spec. Completion requires these scenarios and their task trace:

1. A valid same-feature extension has the annotation and typed record, passes inspection and review, and is
   admitted by Host validation without a new business approval.
2. A missing/mismatched record or wrong task/AC fails extension inspection; a malformed CLI list writes nothing.
3. An unlisted path outside admitted scope fails. A denied extension fails even when added to returned task
   boundaries; custom/semantic deny cases are caught by review.
4. A narrower explicit `--scope` still fails for an omitted extension; no flag silently widens it. Existing
   envelopes without extensions, ordinary directory boundaries and sync-output verification remain compatible.
5. A second accepted worker turn can retain earlier extension annotations without copying those records into its
   latest envelope; inspection and cumulative blocked-range recovery use the applicable committed records.
6. Contract/content tests exercise the same three-tier admission on local/cloud guidance, the Code Reviewer's
   check and missing-evidence/denied-path findings. Existing role and parser tests pass.
7. Run relevant lint/type checks, `just test-affected` with its full fallback, the envelope/inspect/parser/content
   tests and `devkit sync --check`. Verify final contracts through the cross-package reconcile review.

Non-goals: general write authority outside the approved goal; Planning-worker extensions; autohub changes;
changing Git, sandbox, publication or approval gates; a new config setting or ownership registry; glob support;
general generated/lockfile admission; changing another unit's scope; weakening tests; changing `(sync output)`.
