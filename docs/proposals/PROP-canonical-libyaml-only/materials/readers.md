# Production Python YAML reader inventory

Baseline: d363d27. Scout used read-only repository queries; the caller ran the corpus probe.

| Responsibility | Production path / operation |
| --- | --- |
| Strict frontmatter | `packages/devkit-core/src/devkit_core/core/frontmatter.py`: `_load_yaml`, `load_header` |
| Node positions | `packages/devkit-spec/src/devkit_spec/features/documents/models/parse.py`: `_compose` |
| Governance node composition | `packages/devkit-spec/src/devkit_spec/features/governance/usecases/{proposal_boundaries,code_entrypoints,traceability_link}.py` |
| Scalar round-trip probe | `packages/devkit-spec/src/devkit_spec/features/governance/usecases/spec_format.py`: `_yaml_scalar` |
| Glossary YAML | `packages/devkit-spec/src/devkit_spec/features/documents/usecases/search.py` |
| Committed report envelopes | `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/report.py` |
| Bundle invocation YAML | `packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/invocation.py` |
| Workflow decisions | `packages/devkit/src/devkit_agt/features/workflow/repositories/unit/decisions.py` |
| Workflow envelope reads | `packages/devkit/src/devkit_agt/features/workflow/services/envelope/model.py` |
| CLI YAML items | `packages/devkit/src/devkit_agt/features/workflow/services/envelope/authoring.py` |
| Cache consumer | `packages/devkit-spec/src/devkit_spec/features/documents/repositories/{index,memo}.py` |

New shared module: `packages/devkit-core/src/devkit_core/core/yaml.py` (nearest existing parent declared in owns).
New error: `packages/devkit-core/src/devkit_core/base/errors.py`; inspect the package exports during implementation.
The parser fingerprint currently names frontmatter, read/parse/codec modules, PyYAML/libyaml and Python versions;
include the shared parser source. Check availability before memo hits, not only inside a parser on cache misses.

## Error and write paths

`FrontmatterError`, `yaml.YAMLError` and `ValueError` handlers intentionally classify malformed input.
The missing-binding error must bypass those and broad catch/fallback handlers in index loads, report reads, envelope
hints, search and fixers. Check propagation at both CLI and MCP advisory boundaries.
Existing `SPEC_DOCUMENT_INVALID` warnings still skip a bad document while returning the others.

The workflow frontmatter repository and spec-format, traceability and entrypoint fixers use text edits.
Preserve those rather than safe-dumping whole headers. Unicode marks must be checked as character offsets;
comments, unrelated fields, body bytes and CRLF need before/after assertions.
Output-only safe_dump calls remain; reload tests ensure generated records remain valid under C parsing.

## Existing typed operations

Proposal/spec creation, PADR creation, proposal acceptance, workflow binding, entrypoint apply and envelope authoring
already own their metadata changes. No evidence requires a generic writer in this proposal.

## Explicit exclusion

`packages/devkit-viewer/frontend/src/lib/documents.ts` uses npm yaml for browser rendering. It is outside this Python
runtime decision and does not become the validation authority. No frontend change is proposed.

## Probe limits

Run `./.venv/bin/python docs/proposals/PROP-canonical-libyaml-only/materials/probe.py` from this worktree.
`probe-results.json` records the run before these Planning materials were added to the document corpus.
The probe compares currently accepted Markdown headers with the existing strict C subclass; it is not the final
implementation or exhaustive coverage. It does not execute fixers, installed consumers or foreign-platform wheels.
