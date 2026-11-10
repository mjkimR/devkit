---
id: ADR-adaptive-development-and-research
title: Adaptive development, SDD adoption and explicit deep research
summary: "For projects that build without SDD, we own a shared sdd or adaptive-dev approach in devkit-dist, ship an opt-in adaptive-dev bundle, an sdd-baseline adoption playbook and an approach-neutral deep-research bundle citing MAT materials, to keep independent checks, accepting semantic review."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-own-development-approach-policy-outside-sdd
  - ADR-adopt-sdd-through-an-evidenced-baseline-playbook
  - ADR-keep-incubation-guidance-opt-in-and-current-state-based
  - ADR-extend-incubation-with-optional-discovery-teams
  - ADR-keep-discovery-plans-distinct-from-delivery-commitments
  - ADR-retain-research-as-cited-materials
  - ADR-split-deep-research-bundle
  - ADR-adaptive-dev-approach-name
---

# [ADR-adaptive-development-and-research] Adaptive development, SDD adoption and explicit deep research

Superseded in part by `ADR-adaptive-assignment-commands`: the command-group part of "Identifiers and commands use `adaptive-dev`" only; the approach value, bundle, entry skill and context file retain `adaptive-dev`.

Superseded in part by `ADR-adaptive-requires-document-system`: the independent docs/catalog installation clause only: adaptive development installs through the single `devkit-adaptive` requirement; independence from `devkit-spec` remains in force.

Superseded in part by `ADR-adaptive-dev-distribution`: the adaptive-dev bundle owning-wheel clauses: its place in devkit-catalog and entry point, content-only catalog ownership and independent docs/catalog installation as far as they concern adaptive-dev, the rejection of a dedicated wheel, and the driver without another release wheel. Other decisions remain in force.

Superseded in part by `ADR-skill-local-swarm-roles`: the adaptive-dev role-set and role-authority clauses only; approach, current-context and research-material decisions remain in force.

Superseded in part by `ADR-post-merge-verification`: the premerge project/session readiness, touched-Unit integration refusal and provider-activation requirements only. Independent Host branch checks, approach policy, explicit SDD artifact checks, history and unrelated adoption/research decisions remain.

Superseded in part by `ADR-skill-local-research-roles`: the registered research-role projection and role-policy migration clauses only; bundle ownership, optionality and retained materials remain unchanged.

- **Status**: Accepted
- **Date**: 2026-11-02
- **Involved Components/Capabilities**: `CAP-DLV-adaptive-development`, `CAP-DLV-sdd-baseline-adoption`,
  `CAP-DLV-project-policy`, `CAP-DLV-proposal-planning`, `CAP-HARN-agent-guidance`, `CAP-DOCS-document-model`,
  `CAP-DIST-content-packages`

---

## 1. Context & Problem Statement

Independent document assets do not deactivate installed SDD runtime extensions, and an application-specific reader
cannot be the authority for a development approach that must remain inspectable without that application. Existing
SDD consumers must retain their defaults, while a project that iterates without SDD omits per-change lifecycle
obligations. Document formats are independently available under `ADR-document-system`; developing an idea
without SDD also needs agent coordination, optional support roles and resumable current facts without SDD records.
Shared docs authoring policy must serve other development approaches, while spec assets intentionally impose SDD.

"Incubation" named two concepts: the non-SDD development approach with its catalog bundle and the SDD proposal
lifecycle (`CAP-DLV-proposal-planning`), so a request to "incubate" an idea did not identify which one the user means.
The approach value and the bundle name are consumer-facing: a consumer writes them in `.devkit/config.toml`. No
consumer used the incubation approach or bundle.

`MS-idea-incubation` permits voluntary SDD adoption from the implemented product. Brownfield adoption contains legacy
rule debt; feature sync requires a completed Unit; drift reconciliation reviews a bounded batch without defining
adoption readiness. None establishes the transition without inventing delivery history.

Early discovery needs initial documents and a roadmap before implementation, a deliberate research entry, independent
alternatives, shared-assumption examination and document/roadmap synthesis. Existing capability, decision, milestone
and proposal documents have meanings that cannot be inferred from a research recommendation, and consumers may
install docs/catalog without devkit-spec; invoking a spec challenger would make the non-SDD path depend on an optional
SDD package. A repository under SDD also needs explicit research, and switching the shared approach for one
investigation makes spec extensions refuse new SDD records (`CAP-DLV-project-policy`). Research implements nothing and
creates no SDD Unit, so it needs no approach gate. Bundles declare no dependency on another bundle, and two selected
bundles that ship the same skill or subagent ID fail sync with `BUNDLE_CONFLICT`, so a role cannot be shared between
bundles.

One broad investigation can inform several proposals at once, or an adaptive product and a later SDD proposal. A
proposal's own `materials/` moves into `docs/materials/` at its handoff, so research placed there belongs to one
proposal. An indexed material needs only a frontmatter `id` (`CAP-DOCS-document-model`); a backticked `MAT-<slug>` in
prose is a reference edge that `RULE-document-reference` resolves, and handoff rewrites only IDs it wrote, so a cited
MAT ID survives handoff unchanged.

---

## 2. Decision Drivers

### Approach policy
- Shared project intent stays available without devkit-spec and does not depend on managed-file freshness.
- Independent document/project checks and generic integration safeguards remain active.
- A task branch cannot weaken retained-base readiness; SDD history is not reopened automatically.
- Successor adaptive-development guidance can plan against a small stable interface without fixing its product flow.
- One name per concept, so no current setting, bundle, entry or document uses "incubation".
- The name pairs with spec-driven development (`sdd`) as the other development approach.
- The name holds for a product that stays in the approach indefinitely; SDD adoption is optional
  (`CAP-DLV-sdd-baseline-adoption`).
- The name does not read as adapting devkit to a project.
- The rename adds no compatibility code that no consumer needs.

### SDD adoption
- Preserve user-selected adoption and truthful current-state evidence.
- Reuse existing document tools and delivery assets rather than build another runtime engine.
- Keep baseline preparation distinct from policy activation and from historical feature delivery.
- Leave concurrent policy and live-context ownership with their prerequisites.

### Adaptive-dev bundle
- The bundle installs without devkit-spec and does not activate in existing SDD repositories implicitly.
- Reuse distribution and projection mechanisms without another release wheel or runtime service.
- Preserve enough current context to resume, without reconstructing delivery history.
- Verify actual discovery and usage behavior in addition to asset integrity.

### Discovery and materials
- Keep product decisions and authority with the user and invoking Host.
- Keep initial plans useful without representing planned behavior as current capability.
- Preserve uncertainty, evidence provenance and meaningful alternative reopening conditions.
- Reuse document conventions and mutable current context without another parser or lifecycle.
- Produce a proportionate result with no invented approval, dates or automatic implementation.
- One retained investigation serves several consumers without a copy.
- Consumers under either approach cite it the same way.
- An interrupted investigation can resume without an approach-specific file.
- No new document kind, relation field or check.

### Deep research
- Make broad-team research an explicit user action; the entry runs under either approach and only on explicit user
  invocation.
- Retain shared approach policy, SDD-independent installation and the existing lightweight entry.
  (ADR-extend-incubation-with-optional-discovery-teams)
- Broaden alternatives and evidence without mandatory tiers, personalities or runtime infrastructure.
- Verify semantic outcomes beyond distributed file integrity.
- `/adaptive-dev` keeps its optional support without requiring another bundle.
- No cross-bundle dependency and no `BUNDLE_CONFLICT` when both bundles are selected.
- No new runtime, CLI or distribution mechanism.
- Small duplicated contract text.

---

## 3. Considered Options

### Approach policy
- **Keep behavior and rely on removing assets** (rejected in `ADR-own-development-approach-policy-outside-sdd`):
  cannot coordinate installed runtime extensions and misrepresents omitted checks.
- **Infer from installed packages or selected assets** (rejected in `ADR-own-development-approach-policy-outside-sdd`):
  fewer keys, but installation and synchronization state become policy authority.
- **Put the setting in `[tool.spec]`** (rejected in `ADR-own-development-approach-policy-outside-sdd`): cheapest local
  change, but a doc-only consumer cannot inspect its policy without SDD.
- **Own explicit `[development] approach` in devkit-dist** (selected in
  `ADR-own-development-approach-policy-outside-sdd`): one common contract and snapshot authority, with additional
  consumer wiring.
- **Keep `incubation`** (rejected in `ADR-adaptive-dev-approach-name`): no migration; the ambiguity stays.
- **`project-incubation`** (rejected in `ADR-adaptive-dev-approach-name`): keeps the ambiguous word.
- **`project-bootstrap`** (rejected in `ADR-adaptive-dev-approach-name`): reads as a temporary phase, while the
  approach may remain a project's approach.
- **`project-adaptive`** (rejected in `ADR-adaptive-dev-approach-name`): reads as "adapts to the project"; the
  `project-` prefix distinguishes nothing.
- **`adaptive`** (rejected in `ADR-adaptive-dev-approach-name`): a bare adjective that does not name development.
- **`adaptive-dev`** (selected in `ADR-adaptive-dev-approach-name`).

### SDD adoption
- **Keep brownfield adoption unchanged** (rejected in `ADR-adopt-sdd-through-an-evidenced-baseline-playbook`): no new
  asset, but rule debt containment and later migration do not prove the retained baseline before SDD.
- **Add an incubation branch to brownfield adoption** (rejected in
  `ADR-adopt-sdd-through-an-evidenced-baseline-playbook`): shares installation instructions, but one playbook would mix
  gradual debt containment with evidence-complete activation and expose the wrong default for each path.
- **Create a baseline Unit/CLI/workflow** (rejected in `ADR-adopt-sdd-through-an-evidenced-baseline-playbook`): gives
  machine tracking, but adds a new runtime model and invites retrospective lifecycle artifacts without a demonstrated
  requirement.
- **Add a focused `sdd-baseline` playbook in the existing spec bundle** (selected in
  `ADR-adopt-sdd-through-an-evidenced-baseline-playbook`): reuses docs formats and evidence methods while owning the
  missing readiness/activation contract; adds a separate entry and semantic verification cost.

### Adaptive-dev bundle
- **Keep existing SDD skills** (rejected in `ADR-keep-incubation-guidance-opt-in-and-current-state-based`): smallest
  asset count, but product discovery still enters a delivery lifecycle.
- **Put guidance into docs** (rejected in `ADR-keep-incubation-guidance-opt-in-and-current-state-based`): fewer
  selections, but approach-specific entry contaminates generic document installation.
- **Add a dedicated wheel** (rejected in `ADR-keep-incubation-guidance-opt-in-and-current-state-based`): independent
  release ownership, with extra wheel/release wiring and no distinct runtime dependency currently requiring it.
- **Use an opt-in bundle in devkit-catalog** (selected in
  `ADR-keep-incubation-guidance-opt-in-and-current-state-based`): existing independent content distribution and
  explicit selection, at the cost of catalog installation alongside docs and a separate applicability check.
- **Keep resume state only in conversation** (rejected in
  `ADR-keep-incubation-guidance-opt-in-and-current-state-based`): no file, but the next session cannot resume without
  history.
- **Use SDD records or immutable product decisions** (rejected in
  `ADR-keep-incubation-guidance-opt-in-and-current-state-based`): existing formal artifacts, but impose the lifecycle
  being omitted.

### Discovery and materials
- **Context file only** (rejected in `ADR-keep-discovery-plans-distinct-from-delivery-commitments`): minimal; broad
  research and several roadmap alternatives become difficult to inspect.
- **Fixed mandatory PRD/ADR/capability/milestone suite** (rejected in
  `ADR-keep-discovery-plans-distinct-from-delivery-commitments`): familiar names; premature commitments and
  unnecessary volume.
- **Project-owned research/planning notes linked from context** (selected in
  `ADR-keep-discovery-plans-distinct-from-delivery-commitments`): flexible and SDD-independent; semantic review is
  needed.
- **Copy into each proposal's `materials/`** (rejected in `ADR-retain-research-as-cited-materials`): self-contained
  proposals; duplicated evidence that drifts.
- **One indexed material per investigation, cited by ID** (selected in `ADR-retain-research-as-cited-materials`): one
  source; a consumer follows a citation.
- **A new research document kind with a relation field** (rejected in `ADR-retain-research-as-cited-materials`):
  checked links; a document-model change no failure requires.

### Deep research
- **Existing single-entry guidance only** (rejected in `ADR-extend-incubation-with-optional-discovery-teams`):
  smallest surface; broad discovery initiation remains implicit.
- **Explicit research skill inside the approach bundle** (selected in
  `ADR-extend-incubation-with-optional-discovery-teams`, replaced by `ADR-split-deep-research-bundle`): clear intent
  and reused ownership; one additional skill to maintain.
- **Separate discovery bundle** (rejected in `ADR-extend-incubation-with-optional-discovery-teams`; the self-contained
  bundle below is selected in `ADR-split-deep-research-bundle`): clearer standalone branding; duplicated
  context/policy and installation selection.
- **New master subagent and swarm runtime** (rejected in `ADR-extend-incubation-with-optional-discovery-teams`):
  execution control, with unnecessary infrastructure and host coupling.
- **Keep the entry in the approach bundle with a relaxed gate** (rejected in `ADR-split-deep-research-bundle`): no new
  bundle; an SDD project must still select the approach bundle it does not use, and the bundle text keeps mixing both
  concerns.
- **Self-contained `deep-research` bundle with its own researcher** (selected in `ADR-split-deep-research-bundle`): no
  dependency or conflict; one near-duplicate researcher contract to maintain.
- **`deep-research` owns the shared researcher; the adaptive entry delegates to it only when selected** (rejected in
  `ADR-split-deep-research-bundle`): no duplicate; the adaptive entry loses its research role without the second
  bundle, and its text depends on another bundle's IDs.
- **`deep-research` copies all three shared roles under new IDs** (rejected in `ADR-split-deep-research-bundle`): full
  coverage; three duplicates where the coordinator or the researcher covers clarification and usage evidence.
- **Layer the bundles through a Python package dependency plus `auto_select`** (`CAP-DIST-content-packages`; deferred
  in `ADR-split-deep-research-bundle`): a shared role without a dependency engine, which `ADR-document-system`
  rules out across bundles. It works only across wheels, and both bundles ship in the opt-in `devkit-catalog` wheel, so
  it needs a separate wheel. Deferred until a real cross-bundle need appears.

---

## 4. Decision Outcome

We adopt a devkit-dist-owned development approach with the values `sdd` and `adaptive-dev`, the opt-in `adaptive-dev`
catalog bundle, the `sdd-baseline` adoption playbook, retained research as indexed materials cited by ID and a
self-contained `deep-research` catalog bundle.

### Approach policy
- The development approach is an explicit `[development] approach` owned by devkit-dist, so common inspection, runtime
  behavior and conditional guidance agree independently of asset selection.
  (ADR-own-development-approach-policy-outside-sdd)
- The approach value is `[development] approach = "adaptive-dev"` beside `"sdd"`, with `sdd` when absent.
  (ADR-adaptive-dev-approach-name; default per ADR-own-development-approach-policy-outside-sdd)
- `devkit config show` reports the effective approach and source. No local or environment override is supported. SDD
  remains default; adaptive development is an explicit project choice.
  (ADR-own-development-approach-policy-outside-sdd; value name per ADR-adaptive-dev-approach-name)
- SDD-specific consumers apply lifecycle knowledge, while generic rules reporting exposes omissions and devkit-agt
  provides independent project readiness. Explicitly bound historical SDD artifacts retain their checks.
  (ADR-own-development-approach-policy-outside-sdd)
- The retained committed target governs integration readiness; a source-only policy change cannot select a weaker
  path. Project/session readiness first detects touched prior/proposed workflow-owned Units regardless of the caller's
  label, refusing unless the matching lifecycle validator runs. Missing optional SDD tooling cannot weaken retained
  history checks; untouched history does not require that tooling. (ADR-own-development-approach-policy-outside-sdd)
- No dependency resolver, mandatory iteration Unit, new application package or broad structural refactor is
  introduced. `SPEC-incubation-lifecycle-policy` defines the applicability and verification boundary.
  (ADR-own-development-approach-policy-outside-sdd)
- No compatibility is kept: `"incubation"` is an ordinary invalid approach value, refused in the working configuration
  and in committed snapshots with `DEVELOPMENT_CONFIG_INVALID`, whose fix names `"sdd"` or `"adaptive-dev"`.
  (ADR-adaptive-dev-approach-name)
- The `incubation` bundle name gets no alias. (ADR-adaptive-dev-approach-name) → `CAP-DLV-adaptive-development` rule 18
  (MUST NOT)
- `.devkit/incubation.md` gets no fallback read. (ADR-adaptive-dev-approach-name) → `CAP-DLV-adaptive-development`
  rule 18 (MUST NOT)
- Documents call the approach "adaptive development". (ADR-adaptive-dev-approach-name) →
  `CAP-DLV-adaptive-development` rule 18 (MUST)
- Identifiers and commands use `adaptive-dev`. (ADR-adaptive-dev-approach-name) → `CAP-DLV-adaptive-development`
  rule 18 (MUST)
- The approach contract is unchanged by the name: a product may stay in adaptive development, and SDD adoption stays
  the explicit `sdd-baseline` procedure. (ADR-adaptive-dev-approach-name)

### SDD adoption
- The focused `sdd-baseline` playbook keeps retained-product readiness separate from legacy debt containment.
  (ADR-adopt-sdd-through-an-evidenced-baseline-playbook)
- It ships in spec:core and is invoked only for explicitly requested or confirmed graduation. Package/asset
  installation is a prerequisite, not activation. (ADR-adopt-sdd-through-an-evidenced-baseline-playbook)
- It prepares an ordinary material report and needed current-state documents while the `adaptive-dev` approach
  remains effective, and requires evidence coverage of the user-selected retained product, with no unresolved
  retained-scope mismatch or required missing check evidence.
  (ADR-adopt-sdd-through-an-evidenced-baseline-playbook; approach value per ADR-adaptive-dev-approach-name)
- It presents the exact ready source/scope/effects for the user's activation decision, reusing a decision already bound
  to them. It changes the authoritative approach through the accepted policy contract, includes necessary
  missing-provider configuration or a project-to-spec integration provider switch among the explicitly authorized
  effects, then syncs and verifies consistency. (ADR-adopt-sdd-through-an-evidenced-baseline-playbook)
- Ordinary SDD starts for later changes. No historical Units/approvals or discarded-experiment ADRs are created and
  existing SDD history is preserved. (ADR-adopt-sdd-through-an-evidenced-baseline-playbook)

### Adaptive-dev bundle
- The catalog bundle is `adaptive-dev:core` in devkit-catalog (entry point
  `adaptive-dev = "devkit_catalog.adaptive_dev"`), with one `/adaptive-dev` coordinator, three optional support
  contracts and a project-owned mutable `.devkit/adaptive-dev.md`; its pointer guidance is `adaptive-dev-pointer`.
  (ADR-keep-incubation-guidance-opt-in-and-current-state-based; names per ADR-adaptive-dev-approach-name)
- The bundle keeps `/adaptive-dev`, `product-clarifier`, `product-researcher`, `usage-reviewer`, the pointer and the
  current-context template; the research entry, its references and the three research roles are not in it.
  (ADR-split-deep-research-bundle)
- The skill reads the common effective approach before product work; bundle selection itself grants no
  runtime approach change. Shared document instructions remain in docs.
  (ADR-keep-incubation-guidance-opt-in-and-current-state-based; ADR-split-deep-research-bundle)
- Content-only catalog ownership, explicit installation, the shared approach check, independent docs/catalog
  installation, source-specific evidence and mutable coordinator-owned current context are preserved. No entry
  switches approach, authorizes publication, creates SDD records or requires eventual SDD adoption.
  (ADR-extend-incubation-with-optional-discovery-teams)
- Context records current goal, retained choices versus assumptions, run and verification evidence, unresolved
  questions and next useful action. Only the coordinator updates it. Retention follows current usefulness rather than
  immutable history. The baseline proposal consumes semantic facts and does not require parsing this filename.
  (ADR-keep-incubation-guidance-opt-in-and-current-state-based)
- `/adaptive-dev` keeps its own product notes in reused destinations linked from `.devkit/adaptive-dev.md`, and links a
  research material by its MAT ID. (ADR-retain-research-as-cited-materials; names per ADR-adaptive-dev-approach-name)

### Discovery and materials
- Discovery uses proportionate project-owned notes for the product brief, evidence/alternatives,
  direction/architecture recommendation and outcome/dependency roadmap, labelled as discovery/planning, with no new
  document kind and no fixed file count. (ADR-keep-discovery-plans-distinct-from-delivery-commitments;
  ADR-retain-research-as-cited-materials)
- Only the coordinator saves retained synthesis. User decisions, recommendations, assumptions, observations and
  unverified areas stay distinguishable. Surviving alternatives and reopening conditions are kept where they inform
  the next decision; immutable experiment history is not reconstructed.
  (ADR-keep-discovery-plans-distinct-from-delivery-commitments; ADR-retain-research-as-cited-materials)
- Native document semantics apply only when the subject warrants them. A roadmap note is not automatically a milestone
  or a delivery Unit. Research completion grants no implementation, integration, publication or SDD adoption
  authority. A later user-authorized product action can consume these documents through existing entries.
  (ADR-keep-discovery-plans-distinct-from-delivery-commitments; ADR-retain-research-as-cited-materials)
- A retained investigation is the directory `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/` with an index document
  `<YYYYMMDD>-<slug>.md` carrying `id: MAT-<slug>`, `created_at` and H1 `# [MAT-<slug>] <title>`. The index links the
  run's other notes by relative path; a note carries its own `MAT-` ID only when a consumer cites it alone.
  (ADR-retain-research-as-cited-materials)
- The index holds the logical contents (brief, alternatives, direction, conditional roadmap) or links them, plus a
  `Status` line (`complete` or `partial`), open questions and the next investigation.
  (ADR-retain-research-as-cited-materials)
- An SDD proposal, spec or ADR cites the index ID in a code span and never copies or moves the material into its own
  `materials/`. Adaptive current context links the same ID. (ADR-retain-research-as-cited-materials)
- A later investigation that builds on a complete material creates a new material citing it. Only a resumed run of
  the same investigation updates a `partial` index in place. (ADR-retain-research-as-cited-materials)
- Before creating a material, the coordinator checks that `devkit docs resolve MAT-<slug>` finds nothing and the
  directory is absent, and otherwise picks another slug. (ADR-retain-research-as-cited-materials)
- The transient run brief holds in-flight state until a result is retained; nothing else replaces the approach
  context file for research. (ADR-retain-research-as-cited-materials)
- The entry writes these files and never commits them. Its report tells the user to commit the material through the
  project's Git policy, because a proposal can cite it only once it is committed to the base.
  (ADR-retain-research-as-cited-materials)

### Deep research
- `deep-research` is a self-contained catalog bundle with its own researcher, because it meets every deep-research
  driver at the cost of one duplicated contract. It is designed without regard to adaptive development: no role is
  shared, and no bundle or package dependency exists in either direction. (ADR-split-deep-research-bundle)
- `deep-research:core` holds the `/deep-research` entry (`invocation = "user"`), its `orchestration`, `workspace` and
  `synthesis` references, `direction-explorer`, `discovery-critic`, `discovery-planner` (moved, same IDs) and a new
  `research-investigator` (one question per instance; optional bounded experiment in its assigned scratch).
  (ADR-split-deep-research-bundle)
- The invoking agent is the coordinator. It commissions bounded assignments and synthesizes returned evidence; native
  peer communication is optional and no role sequence is mandatory. Source provenance is kept and plans stay distinct
  from delivery commitments. Content-only catalog ownership, explicit selection and installation with docs and catalog
  without devkit-spec apply. (ADR-extend-incubation-with-optional-discovery-teams; ADR-split-deep-research-bundle)
- The entry has no approach gate, reads no approach-specific context file and writes no approach context file. It
  never implements or publishes and creates no SDD Unit, approval or envelope. (ADR-split-deep-research-bundle)
- Under SDD, an explicit `/deep-research` invocation is not development intake: the spec entry does not classify it
  into a depth, and the research run writes only its transient run directory and the retained material. Spec routing,
  `CAP-HARN-agent-guidance` and `UC-route-development-intent` state this exemption. (ADR-split-deep-research-bundle)
- No skill, guidance pointer, guide or role suggests the entry, also on a topic match. The bundle ships no guidance
  asset; install guides list it only as a bundle the user selects. Because Antigravity has no native explicit-only
  setting, the skill body opens with the guard "Run only when the user explicitly invokes this entry; never suggest or
  start it otherwise", and its description carries no trigger phrasing. (ADR-split-deep-research-bundle)
- The two researchers differ in scope: `research-investigator` answers one question of a team investigation;
  `product-researcher` gathers one product decision's evidence or runs one bounded experiment.
  (ADR-split-deep-research-bundle)
- `/adaptive-dev` never invokes or suggests `/deep-research`; it only reads a retained material by its `MAT-<slug>` ID.
  (ADR-split-deep-research-bundle; entry name per ADR-adaptive-dev-approach-name)

---

## 5. Consequences

- **Positive**:
  - Common inspection, runtime behavior and conditional guidance can agree independently of asset selection.
    (ADR-own-development-approach-policy-outside-sdd)
  - "incubation" no longer names the approach, the bundle or its entry. (ADR-adaptive-dev-approach-name)
  - The SDD transition remains voluntary, inspectable and based on actual retained behavior; it reuses current document
    and verification tools. (ADR-adopt-sdd-through-an-evidenced-baseline-playbook)
  - The complete adaptive path is opt-in, independent of SDD assets and resumable across sessions.
    (ADR-keep-incubation-guidance-opt-in-and-current-state-based)
  - Clear research intent and reusable responsibilities for broad product discovery.
    (ADR-extend-incubation-with-optional-discovery-teams)
  - Useful pre-development documents and roadmap without a parallel delivery lifecycle.
    (ADR-keep-discovery-plans-distinct-from-delivery-commitments)
  - One investigation is cited by several proposals; handoff leaves it in place.
    (ADR-retain-research-as-cited-materials)
  - SDD and adaptive projects run the same research entry; neither bundle needs the other.
    (ADR-split-deep-research-bundle)
- **Negative / Risks**:
  - Cost: devkit-dist configuration, generic applicability reporting, project readiness and SDD consumers must be
    verified together. (ADR-own-development-approach-policy-outside-sdd)
  - A global skip or live-tree read can bypass existing history or snapshot authority; retained-binding and
    policy-change tests are required. (ADR-own-development-approach-policy-outside-sdd)
  - A configuration that names `incubation` fails with `DEVELOPMENT_CONFIG_INVALID` or `SELECTION_INVALID` and gets no
    migration steps. (ADR-adaptive-dev-approach-name)
  - A reader of an accepted ADR without the pointer would write the old value, which the working configuration
    refuses. (ADR-adaptive-dev-approach-name)
  - Semantic completeness of SDD adoption requires a reviewer/exercise rather than a new deterministic readiness
    command. A bounded report cannot prove unexamined product areas.
    (ADR-adopt-sdd-through-an-evidenced-baseline-playbook)
  - Source changes or failed installation/sync make earlier evidence stale; the playbook rechecks source and reports
    partial state without claiming activation. (ADR-adopt-sdd-through-an-evidenced-baseline-playbook)
  - Dependency: policy and guidance contracts must be integrated before end-to-end SDD adoption completion; their
    schema and context format are not chosen by the adoption decision.
    (ADR-adopt-sdd-through-an-evidenced-baseline-playbook)
  - Consumers install catalog and docs, and guidance behavior needs semantic walkthrough evidence.
    (ADR-keep-incubation-guidance-opt-in-and-current-state-based)
  - Stale context can mislead a later session; source identity, current checks and explicit uncertainty limit that
    risk. The entry consumes the shared policy inspection interface; relevant changes require affected consumer
    verification. (ADR-keep-incubation-guidance-opt-in-and-current-state-based)
  - Three additional role contracts and conditional guidance need maintenance and consumer checks.
    (ADR-extend-incubation-with-optional-discovery-teams)
  - Many similar agents can amplify one assumption; independent candidate premises and evidence comparison require
    semantic evaluation. (ADR-extend-incubation-with-optional-discovery-teams)
  - Free-form notes require content review; filenames alone cannot establish evidence quality.
    (ADR-keep-discovery-plans-distinct-from-delivery-commitments)
  - A summary can erase uncertainty; the master checks the draft against research evidence and user decisions.
    (ADR-keep-discovery-plans-distinct-from-delivery-commitments)
  - A reviewer of a proposal reads the cited material separately; the proposal report does not include it.
    (ADR-retain-research-as-cited-materials)
  - A material cited only in bare text is not a reference edge; the spec guidance line asks for a code span.
    (ADR-retain-research-as-cited-materials)
  - An uncommitted material leaves a later proposal's citation unresolved; the entry's report names the commit the user
    directs. (ADR-retain-research-as-cited-materials)
  - `research-investigator` and `product-researcher` share most constraints and drift independently.
    (ADR-split-deep-research-bundle)
  - A consumer with `incubation:core` loses the research entry on upgrade; sync removes the unmodified
    projections and announces `deep-research` once with `BUNDLE_UNSELECTED`, and the guides name
    `uv run devkit add deep-research`. Three customizations of a moved role need a manual step the guides name: an
    `incubation:<role>` role-policy key (sync fails until renamed to `deep-research:<role>`), a file override under
    `.devkit/overrides/incubation/` (silently stops applying until moved to `.devkit/overrides/deep-research/`) and an
    edited projection left with `ORPHAN_LEFT` (blocks `devkit add deep-research` until moved or deleted).
    (ADR-split-deep-research-bundle)
- **Follow-ups**:
  - Entry/support/context and verified adoption are distinct proposals; their Planning can begin using accepted policy
    interfaces. (ADR-own-development-approach-policy-outside-sdd)
  - Optional SDD adoption remains `SPEC-incubation-sdd-baseline`; runtime applicability remains
    `SPEC-incubation-lifecycle-policy`. (ADR-keep-incubation-guidance-opt-in-and-current-state-based)
  - Decision records and completed specs that use the old name stay as history and resolve through document aliases.
    (ADR-adaptive-dev-approach-name)
  - Reconsider separate ownership only when independently useful non-incubation research behavior establishes a concrete
    need (met by ADR-split-deep-research-bundle). (ADR-extend-incubation-with-optional-discovery-teams)
  - Reconsider a standardized discovery template only after repeated concrete output failures demonstrate a need.
    (ADR-keep-discovery-plans-distinct-from-delivery-commitments)
  - If a real cross-bundle need appears (a third bundle needs the same researcher, or a bundle must require another),
    reconsider the deferred package-dependency layering with a separate wheel. (ADR-split-deep-research-bundle)

---

## 6. Confirmation

- Approach policy (`ADR-own-development-approach-policy-outside-sdd`): Development tests default/explicit/invalid
  config, local override refusal, doc-only and installed-spec consumers, rule omission versus execution,
  direct/composed command refusal, retained-history changes/deletions, session integration claims and
  source/target/result policy changes. Independent code review and reconcile verification compare every consumer
  against the proposal's table. Planning source evidence is in
  `docs/materials/2026-10/20261028-incubation-lifecycle-policy/consumer-inventory.md`.
- Approach name (`ADR-adaptive-dev-approach-name`):
  `packages/devkit-dist/tests/integration/features/project/test_development.py` accepts `adaptive-dev` and `sdd` and
  refuses `incubation` with `DEVELOPMENT_CONFIG_INVALID`; `packages/devkit-adaptive/tests/integration/bundles/` selects
  and projects the `adaptive-dev` bundle; `tests/e2e/smoke.sh` lists `adaptive-dev` under `devkit-adaptive`.
- SDD adoption (`ADR-adopt-sdd-through-an-evidenced-baseline-playbook`): asset inventory and guidance assertions
  verify entry/ownership and prohibited retrospective artifacts. Seeded app exercises cover ready, missing-evidence,
  source-change and partial-failure paths, recording coverage and real versus simulated decisions. Existing brownfield
  adoption tests preserve its legacy containment behavior. Semantic retained-scope coverage is review-only;
  deterministic format checks alone never establish it.
- Adaptive-dev bundle (`ADR-keep-incubation-guidance-opt-in-and-current-state-based`): build-wheel isolation, catalog
  manifest/projection/reference tests and context-byte preservation exercise distribution. Bounded scenario
  walkthroughs exercise incomplete-goal discovery, research/experiments, inline and delegated iteration, usage
  verification and cross-session resume. Review compares results to AC-01 through AC-06; token checks alone are
  insufficient. `packages/devkit-adaptive/tests/integration/bundles/test_adaptive_dev.py` and
  `packages/devkit-adaptive/tests/e2e/bundles/adaptive_dev/test_installed_consumer.py` verify distribution and policy
  consumption. `SPEC-incubation-development-guidance` retains labelled scenario, actual command and fresh-context
  resume evidence; those bounded observations do not establish general model reliability or real-user usability.
- Discovery teams (`ADR-extend-incubation-with-optional-discovery-teams`): catalog manifest/projection and docs-only
  installation tests check distribution, native role metadata and retained IDs. Bounded observed research and
  fresh-context resume exercises check orchestration, comparison, honest evidence and the distinction between
  recommendations and user decisions. Review only for product strategy quality beyond the selected scenarios; no
  deterministic rule proves global optimality.
- Discovery notes (`ADR-keep-discovery-plans-distinct-from-delivery-commitments`): document rules check applicable
  identity and references. Semantic walkthroughs inspect proposed/current distinctions, source support, unknowns,
  coherent dependencies and fresh-context resume. Review only for the substantive validity of a product
  recommendation and any actual user commitment.
- Materials (`ADR-retain-research-as-cited-materials`): `RULE-document-reference` resolves backticked MAT citations in
  proposals, specs and ADRs. The spec skill's proposal reference states the citation rule. The layout and index fields
  are review only, as for every material (`RULE-spec-format` skips `materials/`). The entry's report line directing
  the commit is review only.
- Deep research (`ADR-split-deep-research-bundle`): `packages/devkit-catalog/tests/integration/bundles/` gains a
  deep-research test that checks the preset contents, explicit invocation projection on every host with the body
  guard, selection with `incubation:core` without `BUNDLE_CONFLICT`, an `incubation:<moved-role>` role key failing
  while `deep-research:<role>` passes, no incubation bundle file naming `incubate-research` or `deep-research`, and no
  deep-research file naming `configuration.development.approach`, `.devkit/incubation.md` or `incubation`. The
  installed-consumer e2e test runs the entry's assets under the default `sdd` approach without devkit-spec.
  Approach-neutral behavior and the absence of suggestion beyond these text checks are review only.
