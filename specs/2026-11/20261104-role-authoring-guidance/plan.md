---
id: PLAN-role-authoring-guidance
spec: SPEC-role-authoring-guidance
---

# Technical Plan

## 1. Constitution & Invariant Review

Preserve independent authoring-bundle distribution and one owner per writing rule. Add an ADR for the shared
placement default; existing registered roles are not migrated and no native API is changed.

## 2. Architecture Overview & Impact

Extend the common instruction description and add a concise Role placement section. The skill-authoring
playbook points to that section when delegation is needed. Reflect it in `CAP-HARN-agent-guidance` and resolve
`FB-skill-local-role-authoring`. No new feature edges or dependencies.

## 6. Verification & Test Plan

Run existing authoring bundle distribution, isolation and wording checks via `just test-affected`, asset hygiene,
package lint/type checks, sync and CI governance. Independent review walks skill-only, reusable and host-settings
cases; no token-matching test is added for this prose-only policy change.
