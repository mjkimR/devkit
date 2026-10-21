---
id: PLAN-exact-playbook-get
spec: SPEC-exact-playbook-get
---

# Technical Plan: `SPEC-exact-playbook-get`

## Constitution & Invariant Review

`ADR-external-playbook-execution` authorizes explicit exact invocation while preserving discovery and permission boundaries. No dependency or layering changes are needed.

## Architecture and Components

Add installation/playbook_get.py and a result dataclass, sharing synchronized_project_root, project_lock, read_synchronized and read_owned. Validate the two exact slugs before project access; resolve only receipt assets and require one owned entrypoint in the bundle prefix. Reuse playbook header validation and frontmatter end offsets to preserve the complete body. Wire the service into the existing JSON-only CLI boundary.

## Assumptions and Premise Check

The current base retains the named receipt readers, shared lock, header parser and CLI boundary described in the carried design. The ADR is already promoted by handoff. Ordinary overrides use live bytes; playbook templates remain unsupported. Reusing existing readers deliberately preserves unrelated stale render-evidence failures and the deployed receipt snapshot. A frozen result model with to_dict follows adjacent result APIs; no new resolver or dependencies are justified.

## Verification

Focused tests map exact body/metadata/hash/CLI to AC-01, overrides and shared failure paths to AC-02/03, large bodies and resource non-reading to AC-04, receipt snapshots/workspace/context to AC-05. Review guidance and Living Spec for AC-06. Run just lint-check dist, just check dist, just test-affected, just test-dist and cumulative governance checks. Independent medium code review and reconcile verification precede the final report.
