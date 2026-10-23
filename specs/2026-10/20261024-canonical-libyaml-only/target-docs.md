---
id: SPEC-canonical-libyaml-only-target
title: Target Living Spec Structure for Require libyaml for consistent YAML parsing
status: draft
spec: SPEC-canonical-libyaml-only
created_at: 2026-10-24
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
  - file: docs/capabilities/documents/CAP-DOCS-document-search.md
  - file: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
  - file: docs/capabilities/delivery/CAP-DLV-workflow-definitions.md
  - file: docs/capabilities/distribution/CAP-DIST-manifest-spec.md
  - file: docs/architecture/ARCH-07-deployment.md
---

# Target Living Spec Structure: Require libyaml for consistent YAML parsing

This blueprint identifies the Living Spec contracts expected to change after implementation. Reconcile may narrow or
expand these targets based on the behavior that actually ships.

## Capability contracts

- `CAP-DOCS-document-model`: specify LibYAML as the required safe parser for Python frontmatter reads, the distinct
  missing-binding execution failure, and preservation of frontmatter validation and parser locations.
- `CAP-DOCS-document-search`: record the LibYAML boundary for optional glossary expansion and its distinct missing-binding error.
- `CAP-DLV-workflow-envelopes` and `CAP-DLV-workflow-definitions`: document that workflow YAML syntax is parsed through
  the shared safe boundary while envelope and decision schemas remain format-owned; document how a missing binding
  propagates as an execution failure.
- `CAP-DIST-manifest-spec`: record the shared parsing boundary for bundle invocation YAML and retain its existing
  format validation and malformed-input behavior.

## Architecture contract

- `ARCH-07-deployment`: document the runtime binding check and supported uv binary-wheel installation route, including
  the limits of dependency metadata and the fact that runtime availability is authoritative.

## Use cases and development guidance

No use-case scenario changes are planned unless implementation changes an existing user-visible flow beyond its error
result. Source authoring and installation guidance are implementation references, not Living Spec targets; keep them
consistent with the capability and architecture contracts above.

## Before and after

| As-is | To-be |
| --- | --- |
| Python YAML readers can select different parser implementations or fall back to Python parsing. | In-scope Python reads use one lazy LibYAML safe boundary and fail clearly when its binding is unavailable. |
| Parser choice and dependency failures are not consistently reflected in the document, workflow and deployment contracts. | Owning format contracts retain their schemas and describe parser and missing-binding behavior; deployment guidance matches the runtime check. |
