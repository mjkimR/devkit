---
id: PROP-incubation-lifecycle-policy
title: Apply explicit development approach policy across lifecycle consumers
summary: "Owns an inspectable project development approach outside devkit-spec and aligns runtime lifecycle checks, integration and installed guidance while preserving independent verification and existing SDD artifacts."
status: reviewing
created_at: 2026-10-28
target_area: delivery/
priority: medium
size: L
planning_effort: medium
dev_effort: medium
milestone: MS-idea-incubation
depends_on: [SPEC-document-bundle-split]
boundaries:
  owns:
    - packages/devkit-dist/
    - packages/devkit/
    - packages/devkit-spec/
    - packages/devkit-docs/
    - docs/capabilities/
    - docs/usecases/
    - docs/architecture/
    - docs/decisions/
    - docs/steering/glossary.md
    - guides/
    - tests/e2e/smoke.sh
    - .devkit/config.toml
    - .devkit/installation.json
    - AGENTS.md
  excludes:
    - packages/devkit-core/
    - packages/devkit-advisory/
    - packages/devkit-cli/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-incubation-lifecycle-policy] Apply explicit development approach policy across lifecycle consumers

## 1. Background & Hypothesis

`SPEC-document-bundle-split` supplies document-only assets. Selecting or removing assets does not define runtime
policy: installed devkit-spec registers integration, attachment, cleanup, hygiene and document-display extensions.
Some already check for a managed spec directory; others do not. See `materials/consumer-inventory.md`.

`MS-idea-incubation` motivates a development approach that does not introduce SDD Units or per-change lifecycle
records. It retains document formats and independent build, test and usage checks. An explicit project-owned
approach can coordinate these consumers without deriving policy from Python installation or stale managed files.

## 2. Technical Spike Questions

- **Q1 — owner and defaults**: recommend devkit-dist ownership of `[development] approach = "sdd" | "incubation"`,
  with an omitted key resolving to `sdd`. `devkit config show` exposes the value and source without devkit-spec.
- **Q2 — applicability**: distinguish ordinary incubation work, deliberately bound SDD artifacts and independent
  verification. Use the consumer table below rather than disabling all workflow or rule execution.
- **Q3 — overrides**: recommend no environment or clone-local override. The shared project config is authoritative.
  A task branch's proposed policy change cannot lower the base's integration readiness.

`PADR-own-development-approach-policy-outside-sdd` compares alternatives. These are proposed choices pending
Host/user acceptance, not decisions already made by the user.

## 3. Proposed Design & Impact

### Shared policy contract

1. devkit-dist's existing project feature owns a typed reader for `[development]`, its commented config template,
   validation and `devkit config show` output. No application imports enter devkit-core.
2. The only key is `approach`, accepting exactly `sdd` or `incubation`; absent table/key means `sdd`. A wrong table,
   unknown key, wrong type or value is `DEVELOPMENT_CONFIG_INVALID`, exit 2, before policy-dependent writes.
3. Extend the existing JSON-only `devkit config show` with effective `development.approach` and its source
   (`default` or `.devkit/config.toml`) in the report's established value/source structure. `devkit spec policy`
   also reports this shared value when devkit-spec is installed; it does not own another copy.
4. The setting is project-shared. `config.local.toml` must continue rejecting it with `CONFIG_LOCAL_KEY_FORBIDDEN`.
   There is no environment override or runtime-specific default. Installing a wheel, adding/removing a bundle,
   or invoking a skill never changes the setting. Document-only users choose incubation explicitly when wanted;
   document commands themselves do not require SDD to be installed under either value.
5. SDD remains the default so existing repositories keep their behavior. The repository developing this feature
   keeps `sdd`. Guides show an explicit incubation configuration and its independent verification commands.

### Consumer applicability

| Consumer | `sdd` | `incubation` |
| --- | --- | --- |
| docs model/lookup/search, nine docs rules | Existing behavior | Existing behavior; malformed document config still fails |
| Generic project build/lint/test, commit gates, custom workflows, host hooks | Existing behavior | Existing behavior; no global gate or workflow shutdown |
| spec router/pointer/constitution and operational guidance | Existing routing | Inspect shared approach first; do not classify incubation edits into SDD depths or request per-change Units, approvals or envelopes |
| `spec new`, proposal creation/accept/handoff and composed lifecycle operations | Existing behavior | Refuse before mutation with `SPEC_LIFECYCLE_INACTIVE`; action identifies the inactive approach and a deliberate SDD choice rather than suggesting a bypass |
| Read-only `spec policy`, worker/scope inspection, docs status overlay | Existing behavior | Remain inspectable; report effective approach and existing state without imposing lifecycle work |
| Five spec lifecycle rules | Existing target and history semantics | Apply to explicitly SDD-bound artifacts only; omit unbound incubation artifacts with coded omission evidence |
| Attachment hook | Existing SDD unit checks | Preserve checks when attaching an SDD-bound unit; leave a generic non-SDD unit to generic validation |
| Rejected-proposal and milestone hygiene | Existing behavior | Preserve checks for retained SDD proposals/milestones; do not infer SDD obligations from ordinary incubation documents |
| Post-finish scoped cleanup | Existing behavior | Clean only existing task-owned records within the prepared scope; mode changes do not broaden or orphan cleanup |
| Integration | Existing SDD unit/session readiness | Independent project readiness for session tasks; no SDD workflow/Unit, effort/depth or per-change record requirement |

An explicitly SDD-bound artifact has an SDD workflow binding in its anchor. When only a companion is targeted or
an anchor is deleted, derive its owner from the companion and the comparison snapshot's prior anchor. Changing
approach or removing that binding must not silently erase an existing SDD artifact's checks. Incubation's editable
current decisions do not retroactively reopen retained SDD decisions or completed Units.

The generic workflow engine still supports deliberate workflow-bound Units, including existing SDD history and
custom workflows. Incubation never makes a workflow mandatory for ordinary edits. Read-only inspection of older
artifacts is not a policy failure. Existing explicit SDD work must be settled through its existing authority;
this change supplies no artifact conversion or history rewrite.

### Omitted checks and integration

- An omitted lifecycle rule is not a successful rule execution. Extend rule reporting with deterministic omission
  records containing the rule ID, code `SDD_LIFECYCLE_INACTIVE` and reason. Preserve target-scope `skipped` semantics;
  document and independent rules still execute. If retained SDD artifacts are checked, report that narrower scope.
  Use an optional generic applicability/reporting contract, with existing rules remaining applicable by default;
  keep SDD knowledge in devkit-spec.
- Add a `project` readiness provider in devkit-agt for session integration without devkit-spec. It runs cumulative
  project linter rules and requires explicit passing `review`, `tests` and `lint` claims using the existing claim
  convention. Claims report performed checks, not fabricated SDD envelopes or a prescribed review role.
- In incubation, the installed `spec` provider delegates session readiness to `project`; a document-only consumer
  can explicitly select `[integration] provider = "project"`. In SDD, `project` cannot bypass SDD readiness and
  refuses with `INTEGRATION_APPROACH_MISMATCH`. An incubation `unit` task carrying SDD history retains SDD readiness
  when that provider is available; a missing required provider fails closed rather than silently downgrading.
- Before choosing an ordinary session path, project readiness inspects prior and proposed committed trees for
  touched workflow-bound Unit ownership, independent of caller task kind. Inspect changed/deleted anchors and
  companions through prior ownership as well as current bindings. Any retained workflow-owned Unit requires its
  lifecycle validator, even if the request says `session`, its anchor/binding was removed, or its package/assets
  are no longer installed. The generic project provider refuses with `INTEGRATION_LIFECYCLE_VALIDATION_REQUIRED`
  and identifies the affected Unit when the matching validator does not run. It never treats absence as success.
  The spec provider can use independent readiness only for ordinary incubation diffs; for touched retained SDD
  ownership it retains SDD artifact validation and completion/hold checks. Untouched history does not require the
  SDD package. Generic ownership detection belongs in devkit-agt; SDD judgments remain in devkit-spec.
- `project` readiness carries `DEVELOPMENT_APPROACH`, `LIFECYCLE` (`omitted:incubation`), source/target/result identity,
  CI-rule result and verification-claim evidence. It enforces the existing source/target/receipt/runtime checks,
  finish guards, approval, PR policy, worktree identity and scoped cleanup contracts. It never creates a Unit.
- The retained target's committed approach governs readiness. Bind both target and prospective approach values to
  evidence and the prepared digest. A source-only switch from SDD to incubation is still evaluated under SDD.
  Changing the base after preparation invalidates the request. No branch can activate its own weaker path.
- Check snapshot configuration from that snapshot, not the live working tree. Policy-dependent malformed config
  fails closed. Unrelated document operations retain their independent configuration boundary.

### Validation scenarios

- **AC-01 — common inspection and validation**: Given devkit-dist without devkit-spec, when `config show` reads no
  setting, then it reports `sdd`/default. Explicit incubation reports its shared-file source. Invalid shared values
  fail with the stable code; a local override is rejected; config-template round trips its documented default.
- **AC-02 — unchanged SDD**: Given the existing default or explicit SDD selection, when routing, lifecycle commands,
  rules, attachment, hygiene and integration run, then their existing checks/gates hold. Selecting `project` cannot
  bypass SDD readiness. Existing SDD regression tests remain green.
- **AC-03 — ordinary incubation**: Given explicit incubation, installed devkit-spec and both selected asset bundles,
  when ordinary unbound current documents and application code change, then no SDD Unit, stage, approval/envelope
  or immutable decision history is required. Guidance takes the incubation branch, document rules and project
  checks run, and omitted lifecycle checks are identified separately from passed checks. Repeat with devkit-spec
  absent to prove common inspection and independent checks do not rely on it.
- **AC-04 — retained SDD artifacts**: Given existing SDD-bound or completed artifacts and an incubation approach,
  when an anchor, binding, companion, reconciliation target or history record is changed/deleted, then the
  existing applicable lifecycle checks are preserved using prior snapshot ownership. Ordinary incubation changes
  do not manufacture historical completion claims. No automatic conversion or reopening occurs.
- **AC-05 — inactive mutation**: Given incubation, when an SDD creation/acceptance/handoff operation is invoked,
  then it fails before changing files, branches or records with `SPEC_LIFECYCLE_INACTIVE`. Read-only inspection and
  generic non-SDD workflows remain usable. Test composed CLI and direct public use-case entrypoints.
- **AC-06 — independent integration**: Given a doc-only incubation consumer with the `project` provider and a
  session branch, when passing independent verification claims and cumulative rules are present, then integration
  prepares without SDD artifacts. Missing/failed claims or document/project violations refuse it; lifecycle
  omissions appear as omissions. Configured approvals, route, guards, runtime and cleanup checks remain enforced.
- **AC-07 — snapshot authority**: Given retained SDD target policy, when a source sets incubation or changes its
  provider, then retained SDD readiness still governs. Given a prepared incubation request, when base policy or
  source/result identity changes, then it is stale. Exercise source/target/result config and rule-snapshot cases. A `session` label never bypasses touched retained Unit
  validation: repeat with devkit-spec absent and selected lifecycle assets absent, and assert coded refusal rather
  than a successful independent-check claim. Untouched history must still allow ordinary incubation integration.
- **AC-08 — guidance and packaging**: Given each supported approach with or without installed devkit-spec, when
  templates, config inspection, guidance, rules and consumer smoke run, then they agree on the effective approach.
  No local/env override, implicit migration, mandatory iteration history or skipped-as-pass result is introduced.
  Run lint/types, `just test-affected` with full fallback, consumer smoke and cumulative governance.

### Successor Planning inputs

`PROP-incubation-development-guidance` can plan against the proposed shared reader/`config show` contract,
incubation's lack of implicit SDD records, and preservation of independent checks once this direction is accepted.
Its bundle name, entry skill, optional roles, current-context artifact and product discovery flow remain open to
its own Planning. Guidance Planning can run alongside policy Development, with final binding to the implemented
interfaces before its own verification. `PROP-incubation-sdd-baseline` can research baseline evidence independently;
its final transition writes and entry behavior depend on the accepted policy and current-context contracts.

### Non-goals

- **Scope Excluded**: incubation entry skills, product discovery/research/usage roles and resumable product context;
  these remain `PROP-incubation-development-guidance`.
- **Scope Excluded**: voluntary baseline adoption, automatic graduation, rewriting existing SDD history or switching
  this repository to incubation; adoption remains `PROP-incubation-sdd-baseline`.
- **Scope Excluded**: disabling project checks, all custom workflows or all commit gates; a generic bypass flag;
  local/environment overrides; adding a workflow for every incubation iteration; generic bundle resolver changes.
- **Scope Excluded**: moving packages solely for structure. No independent structural prerequisite is required by
  this design; a discovered prerequisite returns to the Host rather than silently expanding the feature.

## 4. Lifecycle & Retirement Criteria

Acceptance approves the explicit policy and consumer applicability direction and promotes its PADR. Handoff starts
one feature spec. Implementation must pass AC-01 through AC-08; it does not complete `MS-idea-incubation`.
Keep this proposal in review until Host/user direction acceptance. No worker records acceptance or handoff.

Planning ran source-evidence Scout and one medium Challenger round. The Challenger independently rechecked the
P1 correction and found it resolved without waiver. No user-only question remains outside acceptance of this
proposed direction. Runtime behavior, package isolation and snapshot/omission evidence remain Development checks.

The medium Challenger identified one P1 gap in session integration over retained workflow-owned artifacts. Planning
closed it by requiring prior/proposed ownership detection before task-kind dispatch and coded refusal unless the
matching lifecycle validator runs. This design correction is part of AC-04, AC-06 and AC-07, not a waiver.
