---
id: PLAN-writing-guidance-layers
spec: SPEC-writing-guidance-layers
---

# Technical Plan: `SPEC-writing-guidance-layers` Layered writing guidance for documents and agent assets

## 1. Constitution & Invariant Review

- `ADR-terminology-guidance-lives-in-living-spec-writing` weighed a new instruction header against the context budget
  of every `get-context spec` call and kept terminology in `living-spec-writing`. This plan adds five `spec`
  instruction headers (about 250 tokens per session) and keeps the Glossary section where that ADR placed it. The
  new trade-off is recorded in a new ADR, `ADR-layered-writing-guidance`; the earlier ADR is not superseded.
- `ARCH-08-2-resource-taxonomy`: criteria and standards are instructions, procedures are playbooks. The plan follows
  it: writing criteria move out of the `skill-authoring` playbook into an instruction.
- `authoring` never depends on `spec` (both packages ship independently): `agent-asset-writing` is self-contained.
- No architectural MUST changes.

## 2. Architecture Overview & Impact

- **Impacted Components**:
  - `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/instructions/`: new `document-writing`,
    `decision-writing`, `capability-writing`, `story-writing`, `architecture-writing`; deduplicated
    `contract-authoring` and `living-spec-writing`.
  - `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/bundle.toml`: five instruction assets in preset `core`.
  - `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/templates/{decision,capability,story}.md`: a
    `## Confirmation` section and the Y-statement summary hint (decision); guide pointers in the business-rule and
    scenario comments (capability, story).
  - `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py`: the PADR skeleton gains
    `## 6. Confirmation`, since a PADR is promoted to an ADR.
  - `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-plan/SKILL.md`: pilot rewrite.
  - `packages/devkit/src/devkit_agt/bundles/authoring/bundle/`: new `instructions/agent-asset-writing.md`, asset and
    preset entries in `bundle.toml`, slimmed `playbooks/skill-authoring/SKILL.md`.
  - Living Spec: `CAP-HARN-agent-guidance`, `CAP-DIST-content-packages`, `docs/development/reference/rules.md`,
    `docs/development/reference/distribution.md`, `guides/install/bundle-recommendations.md`,
    `packages/devkit/README.md`, the new ADR.
  - Projections: `uv run devkit sync` refreshes `.devkit/managed/`, the projected skills and `.devkit/installation.json`.
- **New Dependencies**: None.

## 3. Component & Interface Design

### Instruction contract

Each new instruction is `instructions/<slug>.md` with `name` and `description` frontmatter; the description starts
with `Read before` and names its trigger, because `get-context` returns only the header until the body is needed.
English, lines of at most 120 characters.

| Instruction | Bundle, presets | Trigger (description) | Owns |
| --- | --- | --- | --- |
| `document-writing` | `spec`, `core` | Read before writing or editing any document | One directive or claim per sentence; condition before action; prohibition paired with its alternative; reason in one clause, background by ID; nothing the reader already has; no hedged directives; one default instead of option lists; concrete examples |
| `contract-authoring` | `spec`, `core` | unchanged trigger | RFC 2119 use, measurable contracts, Non-Goals, normative vs. example snippets |
| `living-spec-writing` | `spec`, `core` | unchanged trigger | Current state, decision and history placement, completed specs, traceability, summaries, references, glossary |
| `decision-writing` | `spec`, `core` | Read before writing an ADR or PADR | Y-statement summary, context limited to forces, options with one-line trade-offs, Confirmation, consequences |
| `capability-writing` | `spec`, `core` | Read before writing or editing a capability | EARS rule templates with RFC 2119 keywords, enforcing rule or test IDs, scope and interfaces as contracts |
| `story-writing` | `spec`, `core` | Read before writing or editing a user story | Narrative, Example Mapping (rules, examples, questions) to Given/When/Then, background as preconditions only |
| `architecture-writing` | `spec`, `core` | Read before writing or editing `docs/architecture/` | Constraint with its enforcing rule or test ID (fitness function), quality-attribute scenarios, C4/arc42 placement |
| `agent-asset-writing` | `authoring`, `skill-authoring` and `all` | Read before writing or editing a skill, playbook or instruction | Imperative directives, degrees of freedom, default with escape hatch, feedback loops, completion criteria, one-clause reason over capitals, gates for ordering, references one level deep, consistent terms, run vs. read for scripts |

Deduplication: `contract-authoring` keeps the RFC 2119 bullets and loses nothing it alone owns; any general sentence
rule duplicated in `living-spec-writing` or `contract-authoring` moves to `document-writing`. The Glossary section and
its eight rules stay unchanged.

### Playbook split

`skill-authoring` keeps Prerequisites, Step 1 (router structure: layout, frontmatter, body order, references), Step 2
(restructure), Step 3 (exception) and the completion conditions; its "Normative words" and example-density bullets
move to `agent-asset-writing`, and Step 1 links that instruction. `references/scripts.md` stays.

### Pilot record

`specs/2026-10/20261022-writing-guidance-layers/pilot.md` holds:

1. The mapping table: each constraint, command, output section and completion condition of the old `spec-plan`
   text, and its location in the new text (AC-08).
2. Three dry-run scenarios with fixed expected-behavior lists (AC-09):
   - S1 feature spec adding a CLI flag: invariant pre-flight commands, omitted inapplicable sections, IDs not
     paths, verification commands, skeleton marker removed, next stage `spec-tasks`.
   - S2 feature whose design breaks an architecture MUST: a new ADR with path, ID and template, the conflict listed
     in plan section 1.
   - S3 bugfix bundle at `plan-tasks` without `plan.md`: `plan.md` created with `id: PLAN-<slug>` and
     `spec: SPEC-<slug>`, the reproduction test kept as the regression test.
3. Per run, the met expected behaviors. Each run is a fresh agent context given the skill text and the scenario,
   asked for the plan outline and the commands it would run, with no file writes. The old text is taken from the
   base commit.

## 4. Error Handling & Edge Cases

- **A projected copy is edited instead of the source**: sync overwrites it; edit only bundle sources and run
  `uv run devkit sync`.
- **The pilot regresses (AC-09 fails)**: restore the missing directive in the new text and rerun the failing
  scenario for both versions; the rollout non-goal stays.
- **Header budget grows**: the ADR states the bound (five added headers, each description at most 300 characters);
  a later instruction needs its own justification.

## 5. Verification & Test Plan

- New `packages/devkit-spec/tests/integration/bundles/spec/test_writing_guidance.py`: the core preset contains the
  seven instructions; every instruction description starts with `Read before` and is at most 300 characters; the
  decision template has `## Confirmation`; the capability and story templates name their guide (AC-01, AC-03,
  AC-04, AC-05).
- `packages/devkit-spec/tests/integration/bundles/spec/test_terminology_guidance.py` stays green (Glossary kept,
  AC-02).
- PADR scaffold test in `packages/devkit-spec/tests/` updated for `## 6. Confirmation`.
- `packages/devkit/tests/integration/bundles/authoring/test_bundle.py`: preset `skill-authoring` selects
  `agent-asset-writing`; the instruction names no `spec` instruction; existing size and English checks (AC-06).
- AC-02 and AC-07 are review checks recorded in the review envelope; AC-08 and AC-09 in `pilot.md`.
- Commands: `uv run devkit sync`, `just lint`, `just check`, `just rules-check`, `just test-affected`,
  `uv run devkit rules check --phase hygiene` (AC-07, AC-10).
