---
id: PROP-incubation-sdd-baseline
title: Adopt SDD from a verified implemented baseline
summary: "Establishes an evidenced retained-product baseline through an explicit SDD adoption playbook before activating SDD, without reconstructing incubation delivery history."
status: accepted
created_at: 2026-10-28
target_area: delivery/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
milestone: MS-idea-incubation
boundaries:
  owns:
  - packages/devkit-spec/
  - docs/capabilities/delivery/
  - docs/capabilities/harness/
  - docs/usecases/delivery/
  - docs/usecases/harness/
  - docs/decisions/
  - guides/
  excludes:
  - packages/devkit-docs/src/
  - packages/devkit-dist/src/
  - packages/devkit/src/
  - packages/devkit-catalog/src/
task_kind: feature
workflow: sdd-proposal
depends_on:
- PROP-incubation-lifecycle-policy
- SPEC-incubation-development-guidance
---

# [PROP-incubation-sdd-baseline] Adopt SDD from a verified implemented baseline

## 1. Background & Hypothesis

`MS-idea-incubation` permits an app to stay in incubation. A user who chooses SDD needs a truthful account of the retained product, its important structure, current choices and verification methods before future changes are managed through SDD.

The existing `brownfield-adoption` playbook installs SDD and contains legacy Markdown debt. It intentionally allows gradual migration rather than requiring a verified retained-product baseline. `spec-sync` starts from a completed feature Unit; inventing such a Unit for past experiments would misrepresent history. `CAP-DLV-drift-reconciliation` provides bounded evidence and disposition practices but does not define adoption readiness.

Hypothesis: one explicit baseline playbook in the existing spec bundle can reuse those methods and establish the missing transition, without a new CLI command, workflow engine or historical delivery artifacts.

## 2. Technical Spike Questions

- **Q1 — reuse**: recommend a dedicated `sdd-baseline` playbook in `spec:core`, reusing document templates, lookup and bounded drift evidence practices. Keep debt containment in `brownfield-adoption` optional and separately authorized. See `materials/reuse-and-boundary-evidence.md` and `PADR-adopt-sdd-through-an-evidenced-baseline-playbook`.
- **Q2 — readiness**: recommend a coverage-and-evidence threshold for the user-selected retained product, rather than a fixed number of documents or a passing rule run alone.
- **Q3 — activation**: prepare while the effective approach remains incubation; activate SDD only after the current baseline and exact policy effects are ready for the user's decision. The authoritative policy interface comes from `PROP-incubation-lifecycle-policy`.

## 3. Proposed Design & Impact

### Entry and ownership

1. Add the explicitly invoked or confirmed `sdd-baseline` playbook to devkit-spec's existing spec bundle. Ordinary incomplete-idea development never invokes it automatically. The incubation entry may recommend it when the user asks for adoption, but elapsed time, code size and experiment count do not trigger it.
2. If devkit-spec is absent, present installation and asset-selection effects before using the repository's supported installation instructions. Keep the effective approach incubation while preparing. Installing or selecting spec assets does not itself establish baseline readiness or authorize activation. The policy feature must make this combination coherent.
3. Accept semantic inputs from existing incubation context: current goal and constraints, retained choices versus assumptions, unresolved questions, implementation and run/check evidence. Read the actual implementation and current documents. The playbook imposes no context filename or schema on `SPEC-incubation-development-guidance` and does not require historical context to exist.
4. Reuse `devkit docs` lookup/references, docs-owned authoring instructions/templates and the project's independent run/lint/build/test commands. Reuse the evidence and explicit disposition method of `CAP-DLV-drift-reconciliation` without requiring its optional maintenance bundle. Do not run feature-only `spec-sync` as if a completed feature Unit existed.

### Baseline preparation and evidence

5. Begin with repository identity, exact HEAD and relevant dirty paths, retained product scope, intended user flows and exclusions, current policy/asset selection, check commands and a report destination under the repository's ordinary materials location. Default destination: `docs/materials/<YYYY-MM>/<YYYYMMDD>-sdd-baseline/report.md`. Reuse an existing project evidence location when it has the same purpose. This is a material report, not a Unit, workflow binding or envelope.
6. Enumerate retained behavior and representative user flows, important structure/interfaces, current decisions and verification methods. For each, record its current document or missing-document destination, implementation citation, evidence/check result and status: verified, gap or excluded. Exclusions name what is outside the selected adoption scope and why; they never count as verified. Present scope and material uncertainty before rewriting documents.
7. Draft or correct only the current-state documents needed to cover that retained scope. Use capabilities/use cases for retained behavior and flows; architecture for important structure; decision documents for current retained choices whose reasons matter; and development instructions for run/verification methods. A full arc42 set, one ADR per past experiment and duplicated existing accurate documents are not prerequisites. Retained-choice documents describe the present choice and actual known reason; label unknown reasons rather than inventing past alternatives or approval history.
8. Exercise representative retained flows and run applicable independent project checks. Record exact revision, command, environment constraints, outcome and limitations. A skipped/unavailable check is a gap rather than PASS. A deterministic document check proves only its checked condition. Semantic readiness requires comparison against implementation and observed usage.
9. Present mismatches together for the user's disposition: correct a document, fix actual behavior, narrow retained scope, or defer and stay in incubation. Apply corrections only within granted scope. A required retained behavior or verification gap cannot be waived into readiness. Baseline preparation does not authorize unrelated product changes, automatic document deletion or legacy moves. Reuse existing development routing appropriate to the current approach for a separately agreed code correction.
10. The report is ready only when every retained item has truthful current-state documentation and verification evidence, every applicable document/project check passed, and no unresolved retained-scope mismatch or missing required evidence remains. Report excluded areas and bounded coverage explicitly. Do not claim whole-repository consistency from a selected scope.

### Activation and recovery

11. Present the exact ready baseline revision/report, retained scope, actual check outcomes, selected SDD assets and effective policy changes. The user's activation decision applies to those exact effects. Reuse an explicit decision already bound to the same source and effects; otherwise obtain the decision now. Baseline preparation intent alone does not authorize activation against an unknown final scope.
12. Change the authoritative approach to SDD through the interface selected by `PROP-incubation-lifecycle-policy`, synchronize the selected guidance, and verify that inspection, selected assets, rules and next development routing agree. Preserve existing approval, worktree, integration and project-check settings unless separately authorized; propose no universal SDD settings profile.
13. Revalidate evidence if relevant source or dirty content changes before activation. On an installation, policy-update or synchronization failure, report actual partial state and recovery instead of claiming adoption. Do not hide skipped checks or infer rollback from failure. Resume preparation from the report after rechecking its evidence; the process creates no persistent execution service.
14. Subsequent changes follow ordinary selected SDD policies. The baseline itself does not create retrospective proposals, spec Units, workflow approvals or ADRs for abandoned experiments. Keep existing SDD historical artifacts unchanged; this playbook neither reopens completed Units nor grants permission to mutate earlier accepted SDD decisions. A repository already in SDD uses ordinary reconciliation or brownfield adoption as appropriate rather than pretending to graduate from incubation again.

### Validation scenarios

- **AC-01 — voluntary entry**: Given an incubation project, when ordinary development continues or an agent notices size/time/experiment count, then no baseline transition begins. When the user invokes or confirms `sdd-baseline`, baseline preparation begins with visible scope and no policy activation yet.
- **AC-02 — retained baseline**: Given implemented flows, current documents and optional live context, when preparation runs, then the report maps retained behavior, important structure, current choices and verification to implementation/document/check evidence. Missing context is discovered from code and the user rather than reconstructed history. Existing accurate documents are reused.
- **AC-03 — blocked readiness**: Given a failed/skipped required check, undocumented retained behavior, an unresolved behavior mismatch or missing usage evidence, when readiness is reported, then the gap is named and SDD activation is not performed. A passing format check alone cannot resolve it; narrowing scope requires the user's actual intent decision.
- **AC-04 — activation boundary**: Given a ready report, when the user authorizes its exact source/scope/policy effects, then the authoritative approach, selected guidance and runtime checks agree on SDD and subsequent work uses ordinary SDD. Package installation or asset selection alone never substitutes for this activation decision.
- **AC-05 — changes and partial failure**: Given changed relevant source before activation, evidence is revalidated. Given an install/update/sync failure, the agent reports actual partial state and recovery, preserves unrelated edits and claims no successful transition. Repeated preparation reuses and revalidates the report instead of duplicating baseline documents.
- **AC-06 — no retrospective lifecycle**: Given discarded experiments and current retained choices, when baseline documents are written, then only current intended behavior and choices are described. No historical proposal/spec Unit, approval or invented decision rationale is created; existing SDD history is preserved.
- **AC-07 — delivered path**: Given the installed playbook and the prerequisite policy/guidance contracts, when a seeded incubation app is exercised through successful adoption and missing-evidence/changed-source cases, then its report, actual policy/asset state and next SDD route match AC-01 through AC-06. Asset inventory/guidance assertions and existing brownfield-adoption regression tests pass. Semantic exercise results identify real versus simulated user decisions.

### Boundaries and parallel Planning

`PROP-incubation-lifecycle-policy` owns authoritative policy selection and runtime enforcement. `SPEC-incubation-development-guidance` owns the incubation entry, optional roles and live context. Their implementation must be available before this feature's end-to-end adoption exercise and activation integration can complete. This Planning can proceed from the semantic interfaces above without choosing their schema or context path.

Development refreshes its base and checks the accepted prerequisite contracts before filling exact commands and references. A changed prerequisite that breaks the agreed transition is a Host problem, not permission to invent a second setting. No independent structural prerequisite was found.

- **Scope Excluded**: automatic graduation, a new application framework, a generic configuration resolver or policy writer, a new baseline CLI/API/workflow engine, historical experiment reconstruction, changes to incubation discovery/roles/live-context format, automatic legacy containment, unrelated code cleanup and a persistent adoption service.

### Planning review

The medium Challenger inspected the committed proposal, reuse comparison, PADR and prerequisite boundaries at `26ad7f98`. It reported no material findings. The proposal has no separate open design question; direction acceptance remains with Host/user. Actual adoption and missing-evidence/source-change/partial-failure exercises remain Development evidence.

## 4. Lifecycle & Retirement Criteria

Accept the direction and hand off one feature spec after Host review. Development completes when the playbook, installation/routing references, Living Spec and seeded adoption exercises satisfy AC-01 through AC-07. Missing prerequisite implementations block end-to-end completion; their drafts are not implementation evidence. This worker records no acceptance, activation or handoff authority.
