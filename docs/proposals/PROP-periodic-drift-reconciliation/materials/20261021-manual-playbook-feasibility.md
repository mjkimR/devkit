---
id: MAT-manual-playbook-feasibility
title: Manual drift playbook feasibility
summary: "Compares bounded manual reconciliation with rejected detector and scheduler expansion, and checks maintenance bundle delivery against existing preset validation."
created_at: 2026-10-21
---

# [MAT-manual-playbook-feasibility] Manual drift playbook feasibility

## Evidence

Inspection at base `6387059f7d8f4845b20de957840f3c9bbd3cc119` and Planning status commit
`baf66e2c224449fe5f44de65a031be2dfbfc673c` found:

- `packages/devkit-catalog/pyproject.toml` registers only response-style and host-observer; no maintenance module
  or companion playbook is delivered. The package README prescribes a resource module, a bundle manifest,
  registration, a default preset, and a recommendation-table update.
- `packages/devkit-dist/src/devkit/distribution/bundles/manifest.py` rejects an empty preset asset list and
  duplicate or unknown asset selections (lines 416-418). Thus an empty reporting preset or references to
  undelivered weekly-report/review-refactor assets cannot represent independent delivery.
- `CAP-DIST-manifest-spec` supplies reserved implicit `all`, default selection and opt-in operation.
  `CAP-DIST-context-and-playbooks` supplies explicit invocation, on-demand bodies and existing lookup.
- `CAP-DOCS-document-lookup` and `CAP-TRACE-code-entrypoints` supply navigation, not semantic correctness.
  `CAP-GOV-evaluation-lifecycle` supplies deterministic check evidence, not an intent decision.
- `ADR-dual-source-of-truth-and-periodic-reconciliation` requires human arbitration between the two ledgers.
  `MAT-drift-candidate-retrospective` remains the retained empirical reason against path-based stale hints.

## Options

| Option | Result | Assessment |
| --- | --- | --- |
| Bounded manual playbook using existing lookup/checks | Explicit coverage, evidence and user dispositions in a material | Selected direction; no engine or persistence feature |
| New path detector | Automatic candidates with measured low precision/recall | Rejected by retained evidence; reopening condition unchanged |
| Scheduled repository sweep | Requires trigger, execution and authority design | Outside agreed manual scope |
| Initially deploy only drift under upkeep and implicit all | Valid bundle without companion implementations | Recommended, awaiting explicit preset decision |
| Wait for all companion assets | Preserves final three-asset organization at first release | Alternative; introduces external delivery dependency |

## Verification and Limits

Source inspection establishes manifest feasibility; no new bundle was created and no packaging, deployment or
runtime test is claimed. Development must test discovery, preset selection, opt-in behavior and independent
lookup, then run a real read-only bounded sweep plus a clearly simulated fixture exercise for every disposition.
The proposal's rules check returned zero errors and warnings before the challenger pass. No new detector
experiment or cross-repository accuracy measurement was performed. The optional traceability consumer note
must not expand the existing lookup contract.
