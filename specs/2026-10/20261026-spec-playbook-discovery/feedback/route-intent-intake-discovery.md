---
id: FB-route-intent-intake-discovery
title: Route-intent use case lacks the spec intake discovery step
scope: repo
kind: change-request
category: docs-mismatch
target: UC-route-development-intent
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-26
---

# [FB-route-intent-intake-discovery] Route-intent use case lacks the spec intake discovery step

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `UC-route-development-intent` §2 goes from entering the `spec` skill (step 1) and reading
  policy (step 2) straight to classification (step 3). Since `SPEC-spec-playbook-discovery`, the `spec` skill's first
  routing step is playbook discovery at new task intake, before classification
  (`ADR-spec-intake-playbook-discovery`, `CAP-HARN-agent-guidance` §3 principle 7).
- **Proposed Procedure**: add a step before classification: at a new task intake the agent runs one bounded
  `devkit playbook search` and, when a candidate names the requested operation, names it in one line with the
  classification statement; add extensions for a skipped intake (continuation, same-task follow-up, explicit entry,
  inside a playbook, information-only question), no match or search error (silent) and a confirmed or declined
  offer, and a scenario for each.
- **Expected Benefit**: the use case matches the delivered routing; a reader learns where the offer comes from.
- **Cost & Risk**: one use case edit; none to behavior.
- **Attempted**: not edited: `docs/usecases/delivery/` was outside the write scope of the Development run that
  delivered the step.
- **Restart condition and acceptance**: the next change touching `UC-route-development-intent`, or a hygiene pass;
  done when its main scenario names the intake step and `devkit rules check docs/usecases` passes.

## Evidence

```text
UC-route-development-intent §2: step 1 enters the spec skill, step 2 reads policy, step 3 classifies.
spec skill (skills/spec/SKILL.md.jinja) "Route the intent": step 1 "Playbook discovery at intake", step 2 classifies.
```

## Disposition

Resolved at the integration of `SPEC-spec-playbook-discovery`: `UC-route-development-intent` step 1 names
the intake search, extensions 1b (no new task intake, no search) and 1c (a one-line offer, confirm-first, a declined
candidate never offered again) cover the skip and offer paths, and scenarios 2a and 2b test them.
