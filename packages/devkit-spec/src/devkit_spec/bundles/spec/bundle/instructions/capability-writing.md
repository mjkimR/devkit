---
name: capability-writing
description: Read before writing or editing a capability (docs/capabilities/). Defines EARS sentence templates for business rules, references to enforcing checks, scope boundaries and interface contracts.
---

# Capability Writing

A capability is the current contract of one feature area: what the system guarantees. Start from the `capability`
template.

## Business Rules

Write each rule as one EARS sentence with an RFC 2119 keyword. Choose the template by what triggers the rule:

| Template | Trigger | Illustrative example |
| --- | --- | --- |
| `<system> MUST <response>` | Always | The exporter MUST write UTF-8. |
| `WHEN <event>, <system> MUST <response>` | An event | WHEN an import finishes, the exporter MUST print one summary line. |
| `WHILE <state>, <system> MUST <response>` | A state | WHILE a lock is held, the exporter MUST refuse a second run. |
| `IF <unwanted condition>, THEN <system> MUST <response>` | An error or invalid input | IF the input is empty, THEN the exporter MUST exit `2` with `INPUT_EMPTY`. |
| `WHERE <feature or setting>, <system> MUST <response>` | An optional feature | WHERE `--dry-run` is given, the exporter MUST write no file. |

- Combine clauses when a rule needs them: `WHILE <state>, WHEN <event>, ...`.
- Keep one response per rule; split a rule with two responses into two numbered rules.
- Start each rule with a short bold name, so reviews and other documents can point to it.
- End a rule a check enforces with that check: `RULE-<slug>` or a test path.

## Scope and Interfaces

- Name each In-Scope responsibility once. Name the owner of each Out-of-Scope item: another capability or an
  external system.
- List interfaces exactly: commands with flags, output kinds, exit and error codes, payload fields.
