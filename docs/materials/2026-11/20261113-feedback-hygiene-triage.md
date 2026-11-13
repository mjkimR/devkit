---
id: MAT-feedback-hygiene-triage
title: Feedback hygiene recommendations for the UI/UX pilot backlog
summary: "Classifies fourteen pilot feedback records and records six selected direct fixes, three local Impeccable mitigations and five dismissals. Historical upstream drafts remain evidence rather than pending submission work."
created_at: 2026-11-13
---

# [MAT-feedback-hygiene-triage] Feedback hygiene recommendations for the UI/UX pilot backlog

## Scope and provenance

The initial triage below was prepared before disposition. The selected work is recorded in the next section.
The inspection baseline is
`1e21b61a52b9b5e67ea3bd13460b8117491ed204` on a clean main checkout.

The records came from the earlier UI/UX consumer pilots. Commit `fe9d278a7` added ten tooling/procedure records;
commit `540998ec5` added four Impeccable/distribution records. Both commits are dated 2026-11-13. The subsequent
four-proposal delivery added no feedback records. The source records describe observations at older devkit
revisions or consumer installations; their proposed causes and remedies are not accepted facts merely because
the observation occurred.

## Selected work

- Implement the five guidance clarifications and the conditional proposal-cleanup improvement, then resolve their
  named source records only after verification.
- Dismiss the four normal-behavior/mechanism-expansion candidates and the historical mid-session invocation
  question. The latter dismissal makes no claim that a host fix was reproduced.
- Address the three Impeccable observations through bounded local skill guidance where useful: independently
  inspect a UI despite a negative detector signal, report unavailable autonomy probes without claiming they passed,
  and return audit results without inventing unsupported persistence commands. Preserve the existing selected-route,
  native-load, user-answer and file-permission boundaries.
- Close the upstream backlog by linking the local mitigation work when it receives those sources, or dismiss a
  source if no useful local compensation is needed. Do not maintain an external submission task or claim an upstream
  runtime fix. The drafts below remain historical evidence only.

The selected outcomes form three independent feature/spec work units at medium Development effort: guidance,
conditional cleanup, and UI/UX upstream limitations. No unresolved direction requires proposal Planning.

## Initial recommended batch

| Group | Count | Proposed action | Result after authorized work |
| --- | --- | --- | --- |
| Guidance clarification | 5 | Use existing envelope fields/procedures and explain timing, provenance and missing style sources | Resolve only after the changes and review verify each source |
| Cleanup-plan improvement | 1 | Omit inapplicable proposal-prune targets without weakening digest/recovery checks | Resolve only after implementation and regression verification |
| Normal behavior or unsupported mechanism expansion | 4 | Dismiss with the specific reasons below | Dismissed |
| Mid-session host invocation | 1 | Retain pending host discovery/invocation evidence | Open |
| Upstream Impeccable observations | 3 | Retain with the unsubmitted drafts below; no devkit runtime workaround | Open until independently resolved, dismissed or explicitly submitted |

The five guidance items form a bounded guidance change. The cleanup-plan item is a separate, settled-direction
feature change at spec depth because its observable cleanup contract changes. No rule, cache, extension point,
new check verdict, reviewer schema or feedback scaffold command is recommended.

## Item decisions and evidence

### Guidance clarifications: fix candidates

| Source | Current observation and classification | Smallest proposed change |
| --- | --- | --- |
| `FB-reconcile-check-no-per-finding-closure` | The CLI deliberately rejects a reconcile-check source for reverify. A new reconcile-check is the existing closure route; its generic findings already support resolution and waiver fields. Improvement to guidance, not a missing ability to retain outcomes. | Add a closing example that identifies the preceding record and carries each finding's resolved/waived outcome and reason. Keep required contract mismatches non-waivable and keep the existing whole-round verification. Add no new CLI route. |
| `FB-envelope-check-status-vocabulary` | The authoring parser and help accept only PASS, FAIL and SKIP. A reviewer's command not rerun is different from verification evidence supplied by its caller. Guidance ambiguity. | Show SKIP with the command, source envelope and exact source SHA when the reviewer did not run it; distinguish that from a check the reviewer actually performed. Introduce no INHERITED verdict and change no stage exit semantics. |
| `FB-specify-task-coverage-before-tasks` | The current specify skill explicitly defers its commit until plan/tasks satisfy coverage. The UX review supports uncommitted Screens through an assumption. The sequence is valid but distributed between skills. Guidance improvement. | Add one end-to-end commit example: draft Screens, record the reviewed committed HEAD and uncommitted-input assumption, fold findings, finish plan/tasks, and make the appropriate combined commit. Keep the coverage gate and existing commit boundary. |
| `FB-ux-review-closure-stage-unnamed` | The Report template lists review stages but does not name the Development closing stage. The capability already distinguishes reviewer rounds from a further implementer closure record. Guidance defect. | Name build-verify for the implementer's closure. Explain how findings already folded into a draft are reported there, and that this closure is not another independent review round. Preserve the two-review-round limit and optional UX review. |
| `FB-ux-writing-missing-style-file` | UX writing requires a project style source but provides no route when it is absent. The consumer owns style decisions and steering documents. Guidance gap. | Explain how to use an existing project-owned style/token source, or draft a shared style source within the authorized task/document scope when the task decides it. Do not seed a style file into every project, force a filename or edit outside the agreed scope. |

Relevant current source locations:

- `packages/devkit/src/devkit_agt/features/workflow/services/envelope/authoring.py`: CHECK_VERDICTS and the
  reconcile-check refusal/own-route remediation.
- `packages/devkit/src/devkit_agt/features/workflow/models/envelope.py`: Finding already carries resolution/waiver.
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/envelope.md`.
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/review-loop.md`.
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-specify/SKILL.md`.
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-ux-review/SKILL.md`.
- `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/ux-writing.md`.
- `CAP-DLV-delivery-workflows` describes at most two reviewer rounds and a further implementer closure.

The observed exposure is consumer spec authoring/review. The feedback supplies individual pilot examples, not a
measured incidence rate. The demonstrated cost is manual interpretation or restating outcomes; no data loss or
blocked delivery is established. Wording/examples are smaller than new verdicts, closure APIs or record fields.

### Cleanup-plan improvement: fix candidate

`FB-integration-prune-without-proposal` is a repo-owned improvement. In
`packages/devkit-spec/src/devkit_spec/features/delivery/usecases/cleanup.py`, integration_plan adds a
proposal-prune target for every valid activity slug and _parse_targets expects the same tuple.
`CAP-DLV-proposal-lifecycle` describes that existing exact cleanup target. A no-op prune is therefore not evidence
of a missing proposal or an execution defect.

Proposed scope: declare a proposal-prune target only when proposal cleanup applies, while preserving exact
preparation/execution/recovery agreement. Use stable evidence available to the retained request/context; a mutable
filesystem-only test must not make the target disappear after the merge. Cover a spec-only Unit, a proposal handoff,
empty-directory cleanup and a cleanup retry. Keep branch/scope cleanup, publication authority and all refusal checks.

The observed frequency is one consumer integration; recurrence is unknown. The demonstrated impact is confusing
plan output and a manual check, not an unwanted deletion. The smaller alternative is to retain the no-op and explain
it; removing the inapplicable effect is preferred if the exact cleanup guarantees stay intact. This is a settled
direction with implementation choices, not a request for a general cleanup mechanism.

### Dismissal candidates

| Source | Reasoned recommendation |
| --- | --- |
| `FB-docs-list-status-unknown-for-valid-status` | Normal behavior under `CAP-DOCS-document-lookup` section 3.4: status vocabularies are open-ended, and the notice reports values absent from indexed documents while still applying the filter. Treating template examples as a closed status registry would add a new contract. Retain the current behavior and dismiss this proposed change unless a separate direction explicitly chooses that contract. |
| `FB-envelope-commit-companion-files` | The command intentionally commits one envelope; the source guide explicitly supports a combined manual commit and says never to detach a record from accompanying work. A single observed fallback does not justify widening this guarded mutation command with --with. Use the existing combined commit. |
| `FB-envelope-round-reviewer-identity` | The current round-prefix convention is explicit and was usable in the completed multi-round linter delivery. The record supplies a worker's question but no failed round count or lost provenance. Additional structured fields/flags would create competing sources of truth without demonstrated necessity. |
| `FB-feedback-record-no-scaffold-command` | The suggested command is a hypothesis. The evidence reports successful template-based records, with no demonstrated invalid record, blocking failure or measured cost. Keep the existing template plus validation rather than add another CLI surface. |

### Retained host question

`FB-projection-guard-after-mid-session-install` remains open. The repo owns the native user-invocation projection,
but host skill-list refresh and the consumer's exact invocation route remain unverified. Current projection source
still writes the native explicit-invocation setting described by `CAP-DIST-agent-projections`; that alone neither
proves a host defect nor defines a reload procedure.

Missing evidence: the host/version, visibility of the newly installed slash command, whether discovery refreshes
in that same session, and whether a fresh session changes the result. Do not authorize cache reads, remove the
invocation setting or mandate a speculative reload mechanism. Retain the observation for best-effort confirmation
when this installation situation next occurs.

## Historical unsubmitted upstream report drafts

These reports concern historical observations and make no claim that a current Impeccable release reproduces
them. No external submission is authorized or performed. Drafting is not a forwarded status.

### Draft A: monorepo visual implementation detection

- Source: `FB-impeccable-context-target-no-visual-implementation`, `MAT-uiux-improve-pilot` A2c.
- Environment: a consumer monorepo with a SvelteKit SPA in a subdirectory; Impeccable 4.8.x, exact version unknown.
- Report: impeccable context returned hasVisualImplementation=false from the repository root. Repeating it with
  --target pointing at the SPA still returned false. The consumer used its own OOUX documents for framing.
- Requested triage: confirm the expected --target semantics and try a subdirectory SPA fixture. The original
  consumer path is intentionally omitted; the issue has not been reproduced in this checkout.
- Current devkit action: keep accurate coverage and no claim that --target alone fixes detection.

### Draft B: autonomy check in a delegated child

- Source: `FB-impeccable-autonomy-probe-in-subagent`, `MAT-uiux-improve-pilot` A2b.
- Environment: fresh Claude Code children in two consumer runs; Impeccable plugin 4.8.x, exact version unknown.
- Report: AUTONOMY_DIRECTIVE_CHECK requested a live probe that the delegated child could not perform. The child
  continued under a brief that supplied explicit stop conditions. This workaround does not establish upstream
  authorization or equivalence.
- Requested triage: document a supported delegated-session path when a caller supplies an explicit bounded brief,
  or a clear fallback when the probe is unavailable. Native host behavior has not been retested here.
- Current devkit action: preserve capability checks, limited-coverage reporting and the user-operated fallback.

### Draft C: audit persistence command clarification

- Source: `FB-impeccable-audit-storage-write-missing`, `MAT-uiux-improve-second-pilot`.
- Environment: a consumer audit under Impeccable CLI 4.8.2.
- Report: the coordinator reported that audit-storage write was unavailable. The exact command transcript and
  upstream instruction that requested it were not retained, so this is a request for clarification, not a confirmed
  CLI defect.
- Requested triage: identify the supported audit-persistence operation for that version and whether its skill and
  CLI naming agree. A --help transcript or a minimal reproduction is needed before asserting a current bug.
- Current devkit action: do not add a runtime workaround or invent an audit-storage interface.

## Check results and limits

- All fourteen records and their current repo targets were read. No source feedback status has changed.
- The hygiene rule run exited 0. It reported one existing archival material length warning and
  WORKTREE_STALE_SKIPPED because gh authentication failed; remote branch staleness was not checked. No rejected
  proposal cleanup was reported. No unrelated material, branch, host registration or authentication was changed.
- The starting checkout was clean. No implementation, upstream probe or external send was performed in this triage.
- Proposed future fixes require their own appropriate source review, rules/sync checks and implementation checks.
