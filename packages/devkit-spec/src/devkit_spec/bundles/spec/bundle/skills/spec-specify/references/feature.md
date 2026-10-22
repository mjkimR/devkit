# spec-specify reference: feature specification

Read when the bundle is bound to workflow `sdd-spec-feature`; the procedure fills `spec.md` during the `specify` stage.
The shared contracts (non-goals, AC format, references, clarification rule, self-validation, DoD) are in `SKILL.md` §4
and §5.

## Step 1: Clarify intent and the core problem

- Derive the real user problem, audience and context from the agreed intent (`plan-intent`), the issue and the
  proposal or its carried content.
- Record inferences as assumptions (`SKILL.md` §4).
- Identify the primary user story:
  - **As a** `<role>`
  - **I want to** `<action/capability>`
  - **So that** `<outcome/value>`
- When an existing story already expresses it, cite it by ID (`` `US-<slug>` ``) and list it in `related_stories`.

## Step 2: Establish non-goals

Define what this feature will not do (`SKILL.md` §4).

## Step 3: Define acceptance scenarios

- One H3 per scenario with its `[AC-NN]` ID and Given/When/Then.
- Cover the happy path, boundary values, error scenarios (the interface's error contract: exit codes, status or error
  codes, error payloads) and permission or unauthorized cases.
- Default to scenarios a test or a CLI run can confirm literally.

## Step 4: Validate against system invariants

- Review `docs/architecture/` and the capabilities the feature touches; `devkit spec refs <CAP-ID> --direction in`
  shows what depends on them.
- If an ADR will be required, state it explicitly.

## Step 5: Output standard

Keep the frontmatter lines `devkit spec new` or `devkit spec proposal handoff` wrote (`id`, `workflow`, and `summary`
when given); fill in the rest.

```markdown
---
id: SPEC-<feature-slug>
title: <Feature Title>
summary: "<one or two English sentences: what the spec changes>"
status: planned # planned | in-progress | completed
created: <YYYY-MM-DD>
# depends_on: [PROP-foundation, SPEC-parser] # optional exact anchors; omit when empty
related_capabilities:
  - CAP-<AREA>-<slug>
related_stories:
  - US-<slug>
workflow: sdd-spec-feature          # written by `devkit spec new` or `devkit spec proposal handoff`
---

# [SPEC-<feature-slug>] <Feature Title>

## 1. Problem Statement & Motivation
<Brief context on why this feature is needed and the expected outcome.>

## 2. User Stories
- **US-1**: As a <role>, I want <goal>, so that <value>.

## 3. Non-Goals
1. **Scope Excluded**: <Item>
   - **Rationale**: <Why, when it helps>
   - **When to Reconsider**: <Trigger, when one exists>

## 4. Acceptance Criteria & Behavioral Contracts
### Scenario 1: [AC-01] <Happy Path Scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <outcome>

### Scenario 2: [AC-02] <Error / Edge Case Scenario>
- **Given** <precondition>
- **When** <invalid input or edge condition>
- **Then** <expected error response>

## 5. Security, Privacy & Compliance Considerations (optional: drop when the change has none)
<Permission boundaries, sensitive data handling, auth constraints.>
```

- If the feature has no related capabilities or stories yet, leave `related_capabilities` or `related_stories` as `[]`.
- Every listed ID must resolve (`devkit spec resolve <ID>`).
