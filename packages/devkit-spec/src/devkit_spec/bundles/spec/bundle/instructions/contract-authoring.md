---
name: contract-authoring
description: Read before authoring or reviewing specifications, acceptance criteria, policies, instructions, rules or workflows. Defines normative wording, measurable contracts, Non-Goals and examples.
---

# Contract Authoring

## Normative Wording

- State a trade-off as a bounded MUST or SHOULD, not as an `A > B` priority slogan.
- Use RFC 2119 keywords (`MUST`, `SHOULD`, `MAY`) with explicit boundaries and thresholds.
- Reserve MUST and MUST NOT for violations caught by a check/review or hard to undo, such as committing a secret, weakening a contract without approval or editing an accepted ADR. Working habits are SHOULD or "when it helps".

## Scope and Verifiability

- A Non-Goal states its **Scope Excluded**: exactly what will not be built. Add **Rationale** and **When to Reconsider** only when they help later decisions.
- Replace vague qualifiers ("handle errors properly", "ensure high performance") with checkable contracts for the interface: exit codes, status/error codes, output lines, payload structures and Given/When/Then acceptance scenarios. Each scenario carries an ID that tasks cover (`RULE-task-coverage`).
- Documentation code snippets and JSON payloads are non-normative examples unless designated as normative schemas.
