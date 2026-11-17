---
id: CAP-<AREA>-<slug>
title: Capability Title (e.g., Payment Authorization and Cancellation)
summary: "One or two English sentences: what this capability provides and its boundary"   # required, English (RULE-document-summary); quote it, it may contain ": "
area: <area>              # Must match parent directory docs/capabilities/<area>/ (auth | billing | order, etc.)
status: draft             # draft | active | deprecated
usecases:
  - UC-<slug>
---

# [CAP-<AREA>-<slug>] Capability Title

## 1. Summary

## 2. Scope & Boundary
- **In-Scope**: Explicit scope and responsibilities handled by this capability.
- **Out-of-Scope**: Responsibilities handled by other capabilities or external systems (Non-Goals: Scope Excluded, with Rationale and When to Reconsider when they help).

## 3. Business Rules & Policies
<!-- One EARS sentence per rule with an RFC 2119 keyword (capability-writing): [WHEN <event> | WHILE <state> | IF <condition> THEN | WHERE <feature>,] <system> MUST <response>. End a checked rule with its RULE-<slug> or test path. Observable contract only; route mechanism, private formats and syntax by living-spec-writing. -->
1. **[Rule 1 Name]**: <!-- Rule specification and RFC 2119 keyword (MUST). -->
2. **[Rule 2 Name]**: <!-- Rule specification and RFC 2119 keyword (MUST). -->
3. **[Rule 3 Name]**: <!-- Rule specification and RFC 2119 keyword (SHOULD NOT). -->

## 4. Interfaces & Data Contracts
