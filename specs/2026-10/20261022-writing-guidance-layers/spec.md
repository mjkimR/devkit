---
id: SPEC-writing-guidance-layers
title: Layered writing guidance for documents and agent assets
summary: "Restructures writing guidance into a common baseline for all documents, per-document-type guides for ADRs, capabilities, stories and architecture, and a self-contained guide for agent-executed assets, piloted on existing skills."
status: in-progress
created: 2026-10-22
related_capabilities:
  - CAP-HARN-agent-guidance
  - CAP-DIST-content-packages
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-writing-guidance-layers] Layered writing guidance for documents and agent assets

## 1. Problem Statement & Motivation

Skills, playbooks and instructions read as prose: sentences stack a condition, an action, an exception and a
cross-reference, so an agent has to unpack each line before acting. The only authoring asset, the `skill-authoring`
playbook, covers file structure and size but not sentence-level writing. Living Spec documents (ADRs, capabilities,
stories, architecture) have templates but no type-specific writing patterns, and the two spec instructions
(`contract-authoring`, `living-spec-writing`) mix general writing rules with document-placement policy.

Anthropic's skill authoring and prompting guidance is the agreed baseline: concise text that adds only what the model
lacks, calibrated degrees of freedom, a default with an escape hatch instead of option lists, feedback loops,
explicit completion criteria, a one-clause reason instead of bare emphatic commands, and programmatic gates for
ordering that must hold. Further external research is deferred until the pilot shows a gap.

Expected outcome: three layers of guidance, each read only when relevant, and one pilot skill rewritten and compared
against its previous version.

## 2. User Stories

- **US-1**: As an agent writing or editing any repository document, I want one short common baseline, so that
  sentences carry one directive or claim each and repeat nothing the reader already has.
- **US-2**: As an agent writing an ADR, capability, story or architecture document, I want a guide for that type
  only, so that I apply its pattern without reading the others.
- **US-3**: As an agent authoring a skill, playbook or instruction, I want a self-contained writing guide that works
  even where the `spec` bundle is not installed, so that agent-executed text is directive and verifiable.

## 3. Non-Goals

1. **Scope Excluded**: Rewriting existing skills, playbooks, instructions or Living Spec documents to the new
   guidance beyond the pilot (`spec-plan`) and the `skill-authoring` playbook.
   - **When to Reconsider**: after the pilot comparison shows no regression; rollout is its own spec.
2. **Scope Excluded**: New governance rules that check writing style mechanically (hedge words, emphasis density,
   bare prohibitions).
   - **Rationale**: the patterns need pilot evidence before a check can encode them without false positives.
3. **Scope Excluded**: Writing guides for feature specs (`spec.md`, `plan.md`, `tasks.md`), proposals, milestones
   and materials; their skills and templates already define their structure.
4. **Scope Excluded**: Moving the terminology and glossary rules out of `living-spec-writing`
   (`ADR-terminology-guidance-lives-in-living-spec-writing`).
5. **Scope Excluded**: Changing `RULE-skill-document-size`, its threshold or the router structure of skills.

## 4. Assumptions

- **A1 (common baseline owner)**: a new `spec` bundle instruction `document-writing` holds the sentence-level rules
  for every document. `contract-authoring` keeps normative wording, verifiability, Non-Goals and examples;
  `living-spec-writing` keeps current-state writing, decision and history placement, completed specs, traceability,
  summaries, references and the glossary. A rule stated in more than one of the three is kept in one owner only.
- **A2 (per-type guides)**: one `spec` bundle instruction per document kind, named after the kind:
  `decision-writing`, `capability-writing`, `story-writing`, `architecture-writing`. Separate files keep each trigger
  precise; the added header cost is weighed in the plan's ADR against the context budget driver of
  `ADR-terminology-guidance-lives-in-living-spec-writing`.
- **A3 (agent assets)**: a new `authoring` bundle instruction `agent-asset-writing`, in presets `skill-authoring` and
  `all`. It restates the few common rules it depends on, because `authoring` is opt-in and never depends on `spec`.
- **A4 (patterns)**: ADR summaries use the Y-statement form and ADRs gain a Confirmation section (MADR 4); capability
  business rules use EARS sentence templates; stories derive scenarios by Example Mapping (rule, examples,
  questions); architecture constraints name the rule or test that enforces them (fitness function) or state that none
  does. Templates change only as far as their guide requires.
- **A5 (pilot)**: `spec-plan` is the pilot skill; the comparison uses three dry-run scenarios with a fixed
  expected-behavior list, each run by a fresh agent context against the old and the new text.
- **A6 (style)**: instruction text is English with lines of at most 120 characters, the existing instruction style.

## 5. Acceptance Criteria & Behavioral Contracts

### [AC-01] Spec bundle lists the common and per-type instructions
- **Given** the `spec` bundle synced into this repository
- **When** `uv run devkit get-context spec` runs
- **Then** `instructions` contains exactly `contract-authoring`, `living-spec-writing`, `document-writing`,
  `decision-writing`, `capability-writing`, `story-writing` and `architecture-writing`, and each header
  `description` starts with `Read before` and names the documents or actions it governs

### [AC-02] Common baseline has one owner per rule
- **Given** `document-writing`, `contract-authoring` and `living-spec-writing` after the change
- **When** a reviewer compares their rules
- **Then** `document-writing` states the sentence-level rules (one directive or claim per sentence, condition before
  action, a prohibition paired with its alternative when one exists, the reason in one clause with background
  linked by ID, no explanation the reader already has, no hedged directives), no rule appears in two of the three
  files, and the `## Glossary` section of `living-spec-writing` keeps its eight rules

### [AC-03] Decision guide and template
- **Given** `decision-writing` and the `decision` template
- **When** an agent writes a new ADR
- **Then** the guide requires a `summary` in Y-statement form (context, concern, decision, achieved quality, accepted
  downside) and a Confirmation section naming the rule, test or review that checks compliance, and the template
  contains a `## Confirmation` section

### [AC-04] Capability guide and template
- **Given** `capability-writing` and the `capability` template
- **When** an agent writes or edits a capability's business rules
- **Then** the guide gives the EARS templates for ubiquitous, event-driven (`WHEN`), state-driven (`WHILE`),
  unwanted-behavior (`IF ... THEN`) and optional-feature (`WHERE`) rules with RFC 2119 keywords, requires a rule a
  check enforces to name that rule or test ID, and the template's business-rule comment points to the guide

### [AC-05] Story and architecture guides
- **Given** `story-writing` and `architecture-writing`
- **When** an agent writes a story or an architecture document
- **Then** `story-writing` derives Given/When/Then scenarios from rules and examples (Example Mapping) and limits
  background to preconditions, and `architecture-writing` requires each constraint to name its enforcing rule or
  test ID or to state that none exists, and gives the quality-attribute scenario form (source, stimulus,
  environment, response, measure)

### [AC-06] Agent asset guide in the authoring bundle
- **Given** the `authoring` bundle with preset `skill-authoring` or `all`
- **When** `uv run devkit get-context authoring` runs
- **Then** `instructions` contains `agent-asset-writing`, whose body covers imperative directives, degrees of
  freedom, one default with an escape hatch, feedback loops, completion criteria, a one-clause reason instead of
  emphatic capitals, gates or scripts for required ordering, conditional references one level deep and consistent
  terms, and names no `spec` bundle instruction as required reading

### [AC-07] Playbook keeps procedure only
- **Given** the `skill-authoring` playbook after the change
- **When** a reviewer reads it
- **Then** it holds the create, restructure and exception procedures and their completion conditions, links
  `agent-asset-writing` for sentence-level writing, states no sentence-level writing rule itself, and
  `uv run devkit rules check --phase hygiene` reports no `RULE-skill-document-size` warning for it

### [AC-08] Pilot rewrite preserves every constraint
- **Given** `spec-plan` rewritten under `agent-asset-writing`
- **When** a reviewer compares the old and new text using the mapping table in the unit's pilot record
- **Then** every constraint, command, output section and completion condition of the old text maps to a location in
  the new text, with zero dropped entries

### [AC-09] Pilot behavior comparison
- **Given** three dry-run planning scenarios with a fixed expected-behavior list each, recorded in the unit
- **When** a fresh agent context runs each scenario once with the old and once with the new `spec-plan` text
- **Then** the pilot record lists the met expected behaviors per run, and in each scenario the new text meets at
  least as many expected behaviors as the old text

### [AC-10] Living Spec and checks
- **Given** the change complete
- **When** `uv run devkit sync`, `just rules-check` and `just test-affected` run
- **Then** all three exit `0`, and `CAP-HARN-agent-guidance`, `CAP-DIST-content-packages`, the rules and
  distribution references and `guides/install/bundle-recommendations.md` list the new instructions
