---
id: PADR-background-pointer-in-constitution
title: Point agents to project background from the spec constitution
summary: For project-wide background that every role needs only when its work depends on it, we add one constitution line naming the group and its trigger, each file opening with a one-line scope, to reach workers and nested roles at constant context cost, accepting that reading stays the agent's judgment.
proposal: PROP-foundation-documents
status: draft
created_at: 2026-10-26
---

# [PADR-background-pointer-in-constitution] Point agents to project background from the spec constitution

- **Status**: Draft
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

Project-wide background (product purpose, tone, style direction, the glossary) applies to wording, naming, interface
and content decisions in every activity, Development workers and nested roles included. Agents read it only when
guidance tells them where it is and when it applies. Three places could carry that pointer:

- The `spec` skill's intake runs only for a user's own request, never for a worker turn or a nested role (`spec` skill,
  Route step 1), so it does not reach Development workers.
- `living-spec-writing` is read only before writing `docs/` or `specs/`, not before code or interface work.
- The spec constitution (`AGENTS.md.jinja` of the `spec` bundle, 4677 bytes) is loaded once per agent context by every
  role through `devkit get-context spec`. Each line there is paid by every context
  (`ADR-writing-and-terminology-guidance`).

The group has no size bound, so an instruction to read all of it would load every background file into every role.

## 2. Decision Drivers

- Reach every role that makes a wording, naming, interface or content decision, workers included.
- Constant context cost per agent context, independent of the size of the group.
- A mechanical check that the pointer exists and names its trigger.

## 3. Considered Options

### Option 1: One conditional constitution line, scoped files (Selected)
- **Overview**: one line in the constitution's Living Spec section names the group's location and the trigger ("before
  a naming, wording, interface or content decision, read the background file it concerns"); each background file opens
  with a one-line scope so an agent opens only the file it needs.
- **Pros**: reaches every role; one line of cost; reading stays proportional to the decision.
- **Cons**: whether an agent applies the trigger is judgment, not a check.

### Option 2: A step in the `spec` skill at work-unit start
- **Overview**: intake or Unit creation tells the agent to read the group.
- **Pros**: no constitution cost.
- **Cons**: never reaches workers and nested roles, who make most interface and content decisions.

### Option 3: An unconditional read in the constitution
- **Overview**: "read the background group before development work".
- **Pros**: no judgment involved.
- **Cons**: loads every file into every context, reviewers and challengers included, with no bound.

### Option 4: Search only
- **Overview**: agents find background through `devkit spec search`.
- **Pros**: no guidance change.
- **Cons**: an agent does not search for what it does not know exists; ID-free files are not search candidates today.

## 4. Decision Outcome

We decided to adopt **Option 1**: it is the only option that reaches workers (driver 1) at the cost of one line
(driver 2), and a guidance test can assert the line and its trigger (driver 3). The `docs-skeleton` seed gives each
seeded background file its scope line; `living-spec-writing` states the scope-line convention.

## 5. Consequences

- **Positive**: every role learns where background lives and when to read it; context cost stays one line.
- **Negative / Risks**: an agent may skip a relevant file; the scope line mitigates it but does not prove it.
- **Follow-ups**: if reviews show background drift despite the pointer, reconsider a review-stage check that names the
  background files a change's wording depends on.

## 6. Confirmation

A guidance test under `packages/devkit-spec/tests/integration/bundles/spec/` (in the style of
`test_terminology_guidance.py`) asserts the constitution line, its location and its trigger, and that each seeded
background file starts with a scope line; `test_bundle_budgets.py` keeps the bundle within its size budgets.
