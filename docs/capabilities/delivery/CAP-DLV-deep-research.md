---
id: CAP-DLV-deep-research
title: Deep Research
summary: "An opt-in, approach-neutral catalog bundle supplies an explicitly invoked research team that compares directions with sourced evidence and retains each investigation as one indexed material under docs/materials/, cited by its MAT ID; it never implements, commits or creates delivery records."
area: delivery
status: active
created_at: 2026-10-30
usecases:
  - UC-research-an-idea-and-shape-a-roadmap
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/SKILL.md
---

# [CAP-DLV-deep-research] Deep Research

## 1. Summary

The opt-in `deep-research` catalog bundle supplies `/deep-research`, an explicitly invoked entry for a bounded
research team, and four optional research roles. The invoking agent is the coordinator. It compares independent
directions with sourced evidence and retains the result as one indexed material under `docs/materials/` that
proposals, specs, decisions and adaptive current context cite by its `MAT-<slug>` ID. The entry works under either
development approach and neither reads nor changes it.

`ADR-split-deep-research-bundle` owns the bundle split and role ownership; `ADR-retain-research-as-cited-materials`
owns the retained material and its citation.

## 2. Scope and Boundary

- **In-Scope**: explicit research-team coordination, independent alternatives, source provenance, optional
  criticism, initial document and roadmap synthesis, bounded partial results, the transient research workspace and
  the retained material with its collision, resume and citation conventions.
- **Out-of-Scope**: product iteration and its current context (`CAP-DLV-idea-incubation`), shared approach policy
  (`CAP-DLV-project-policy`), SDD routing (`CAP-HARN-agent-guidance`), generic projection
  (`CAP-DIST-agent-projections`) and document formats (`CAP-DOCS-document-model`).
- **Scope Excluded**: an approach gate, a research runtime, CLI or scheduler, a bundle or package dependency, a
  shared role, a new document kind or materials rule, committing or publishing results, and migration of earlier
  incubation research runs or materials.

## 3. Business Rules and Policies

1. **Explicit selection**: WHERE `deep-research:core` is selected, sync MUST deploy the entry and its four roles
   without seeding documents or context; no catalog bundle selects it automatically. Test:
   `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py`.
2. **Independent installation**: The bundle MUST install with docs and catalog without a devkit-spec distribution,
   under the default `sdd` approach. Test: `packages/devkit-catalog/tests/e2e/bundles/deep_research/test_installed_consumer.py`.
3. **Explicit invocation**: The bundle MUST declare `invocation = "user"` for the entry, and its skill body MUST open
   with the explicit-only guard; native projection follows `CAP-DIST-agent-projections`. Test:
   `test_entry_projects_explicit_invocation_for_each_host`.
4. **No suggestion**: No skill, guidance pointer, guide or role SHOULD suggest or start the entry, also on a topic
   match; install guides list it only as a bundle the user selects. Test:
   `test_guides_name_the_bundle_only_as_a_selection` and the incubation text check.
5. **Approach neutrality**: WHEN the entry starts, the coordinator MUST NOT inspect, require or change the
   development approach, read approach-specific context or write `.devkit/incubation.md`. Test:
   `test_bundle_text_is_approach_neutral_and_self_contained`.
6. **SDD intake exemption**: WHILE the effective approach is SDD, an explicit `/deep-research` invocation MUST NOT be
   classified into a planning depth or create a Unit; work the research informs starts as ordinary intake
   (`CAP-HARN-agent-guidance`).
7. **Research authority**: WHEN the entry runs, the coordinator MUST write only its transient run directory and the
   retained material; it MUST NOT implement, publish, stage or commit, or create a Unit, approval or envelope.
8. **Bounded evidence**: WHEN research or an experiment informs the investigation, the coordinator MUST distinguish
   observations, assumptions, limitations and the decision informed; an experiment names its write boundary and
   stop condition.
9. **Truthful verification**: WHEN reporting a check or role result, the coordinator MUST identify the actual
   source- or artifact-specific execution and its limits; skipped, unavailable or inconclusive evidence remains
   unverified.
10. **Optional support**: WHERE a separable question warrants delegation, the coordinator MAY invoke a research role;
    no investigation requires all roles, a fixed team count or a role sequence.
11. **Role boundaries**: WHEN a role is invoked, the coordinator MUST supply one goal, absolute boundaries,
    source/artifact identity, permitted actions, stop condition and expected output before verifying the actual
    return. The role reports native or emulated availability truthfully. Test:
    `test_roles_keep_optional_execution_and_coordinator_material_ownership`.
12. **Independent alternatives**: WHILE direction is open, the coordinator SHOULD develop materially different
    premises independently before sharing peer conclusions, then compare them under relevant common criteria.
13. **Research provenance**: WHEN a claim informs a direction, the investigation MUST retain its inspected source,
    material date or version and limits while distinguishing vendor claims, inference, contradictions and unknowns
    from observation. Synthetic users and fixtures are scenario input.
14. **Optional criticism**: WHEN shared assumptions or unsupported convergence need examination, the coordinator MAY
    use discovery-critic; zero supported findings is a valid return.
15. **Initial synthesis**: WHEN retaining research documents and a roadmap, the coordinator MUST distinguish
    recommendations, actual user decisions, assumptions and proposed behavior rather than claim implemented
    capability or a delivery commitment.
16. **Bounded partial result**: IF evidence, delegation or research effort is insufficient, THEN the coordinator MUST
    retain the actual partial evidence and missing coverage in a `partial` material without inventing a winner,
    execution or runtime limit.
17. **Research completion**: WHEN the entry returns, the coordinator MUST report its bounded outcome, the retained
    material's path and ID and the next decision, and MUST tell the user to commit the material through the
    project's Git policy before a consumer cites it; implementation and publication require their own authority.
18. **Research workspace**: WHEN scratch writes are needed, the coordinator MUST allocate separate run and task paths
    under `.devkit/transient/deep-research/`, verify Git ignore and untracked state where applicable, and grant only
    explicit task scratch writes; product source and the retained material stay read-only to members. Test:
    `packages/devkit-catalog/tests/e2e/bundles/deep_research/test_installed_consumer.py`.
19. **Selective promotion**: WHEN retaining research outputs, the coordinator MUST select useful synthesis and
    evidence rather than copy the whole run, and resolve retained references without transient-only dependencies;
    allocation edits no ignore rule and deletes no scratch automatically.
20. **One material per investigation**: WHEN an investigation is retained, the coordinator MUST create one directory
    `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/` with an index document carrying `id: MAT-<slug>`. Test:
    `test_retention_contract_and_no_commit_are_stated`.
21. **Collision check**: IF `devkit docs resolve MAT-<slug>` finds a document or the directory exists, THEN the
    coordinator MUST choose another slug and never overwrite an existing material.
22. **Resume**: WHEN the user names a `partial` material of the same investigation, the coordinator MAY update that
    index in place; a `complete` material MUST NOT be rewritten, and later research creates a new material citing it.
23. **Citation**: WHEN a proposal, spec, decision or current-context note uses a retained material, it SHOULD cite
    the index ID in a code span and MUST NOT copy or move the material into its own directory.
24. **Material preservation**: WHEN sync, removal or re-selection runs, sync MUST preserve retained materials. Tests:
    `test_reselection_preserves_retained_material` and the installed-consumer test.

Distribution checks enforce file and metadata contracts. Evidence comparison, optionality, synthesis and the absence
of suggestion beyond the text checks are semantic agent contracts checked by review.

## 4. Interfaces and Data Contracts

### Distribution and entry

Install devkit-docs and devkit-catalog, then select `uv run devkit add deep-research` (`deep-research:core`, entry
point `deep-research = "devkit_catalog.deep_research"`). The skill and four role contracts use existing projection
mechanisms; Codex receives `allow_implicit_invocation: false` and Claude Code `disable-model-invocation: true`. The
bundle ships no guidance asset and no constitution. No research runtime or CLI is added.

`/deep-research <question or decision>` accepts natural-language goals and existing documents. The coordinator
frames a question and bound, commissions useful assignments, validates evidence, compares directions and retains a
proportionate synthesis. It reads an earlier run directory or material only when the user names it as an input.

### Optional roles

| Role | Result | Source and Git boundary |
| --- | --- | --- |
| research-investigator | Sourced evidence for one question of the investigation, or one bounded experiment (including actual usage of an existing flow) | Read-only by default; assigned scratch notes or experiment writes only |
| direction-explorer | One distinct premise with its users and problem, intended usage, trade-offs, critical assumptions and discriminating evidence | Product read-only; assigned scratch notes only; no production implementation or winner declaration |
| discovery-critic | Cross-candidate framing and evidence findings with failure conditions, or zero findings | Product read-only; assigned scratch notes only; no decision or demanded consensus |
| discovery-planner | Draft research brief, research and architecture notes and a conditional roadmap | Product read-only; assigned scratch notes only; no retained-material writes |

Every role leaves the index and HEAD unchanged and commits or publishes nothing; only the coordinator writes the
retained material. A result contains status (`completed`, `needs_input` or `failed`), summary, source/artifact
identity, observations with evidence and failure conditions, recommendation or draft, assumptions and unverified
areas; an experiment also returns actual changed paths, commands and outcomes. Effective contracts live under
`.devkit/managed/deep-research/subagents/`.

### Workspace

The coordinator allocates a collision-free run and per-task directories under `.devkit/transient/deep-research/`.
Git-backed runs verify exact ignored and untracked paths before scratch writes; absent Git is reported. The run brief
holds in-flight state. Earlier `.devkit/transient/incubation-research/` runs stay in place and are read only when the
user names one.

### Retained material

| Part | Contract |
| --- | --- |
| Directory | `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/` |
| Index | `<YYYYMMDD>-<slug>.md` with frontmatter `id: MAT-<slug>` and `created_at`, H1 `# [MAT-<slug>] <title>` |
| Contents | Research brief, research and alternatives, direction and architecture, initial roadmap, in the index or linked notes; no fixed file count |
| Status | A `Status:` line (`complete` or `partial`), open questions and the next investigation |
| Linked notes | Relative links from the index; a note carries its own `MAT-` ID only when cited alone |
| Citation | `MAT-<slug>` in a code span, which `RULE-document-reference` resolves; proposal handoff leaves it unchanged |

The layout and fields are a convention: no rule checks materials (`RULE-spec-format` skips `materials/`). A material
is no capability, decision, milestone, proposal or Unit.
