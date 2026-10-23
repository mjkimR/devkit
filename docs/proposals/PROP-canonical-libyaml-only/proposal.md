---
id: PROP-canonical-libyaml-only
title: Require libyaml for consistent YAML parsing
summary: "Require PyYAML LibYAML safe parsing for Python runtime frontmatter and standalone YAML inputs. Define installation eligibility, distinct missing-binding failures, and parser and fixer verification."
status: reviewing
created_at: 2026-10-23
target_area: capabilities/documents/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-core/src/devkit_core/core/
    - packages/devkit-core/src/devkit_core/base/errors.py
    - packages/devkit-core/tests/unit/core/
    - packages/devkit-spec/src/devkit_spec/features/
    - packages/devkit-spec/tests/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/instructions/document-writing.md
    - packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/invocation.py
    - packages/devkit-dist/tests/integration/features/distribution/test_skill_invocation.py
    - packages/devkit/src/devkit_agt/features/workflow/
    - packages/devkit/tests/integration/features/workflow/
    - packages/devkit-core/README.md
    - guides/INSTALL_GUIDE.md
    - docs/architecture/ARCH-07-deployment.md
    - docs/capabilities/documents/CAP-DOCS-document-model.md
    - docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
    - docs/capabilities/delivery/CAP-DLV-workflow-definitions.md
    - docs/capabilities/distribution/CAP-DIST-manifest-spec.md
    - scripts/smoke.sh
    - tests/e2e/smoke.sh
  excludes:
    - docs/decisions/
    - packages/devkit-viewer/frontend/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-canonical-libyaml-only] Require libyaml for consistent YAML parsing

## 1. Background & Hypothesis

`CAP-DOCS-document-model` defines a Python-compatible frontmatter grammar with C acceleration and fallback.
Standalone workflow records, bundle invocation settings and glossary YAML use separate readers.
Node-based document readers and fixers also select their own loader.
The same input can therefore produce different acceptance and diagnostics across Python operations.

Require one LibYAML safe parser boundary for Python runtime reads, accepting its syntax differences from the
Python parser. Preserve each format's existing schema validation and the surgical editing of document text.
The persistent decision is `PADR-require-the-libyaml-safe-parser-at-yaml-read-boundaries`.

### Source feedback

`FB-canonical-c-yaml-contract` remains open until Development implements and verifies this contract.
Planning alone does not resolve it.

## 2. Technical Spike Answers

### Q1: Installation eligibility

Retain Python `>=3.12` and the existing `pyyaml>=6.0.1` dependency declarations.
Dependency metadata cannot require an optional extension; runtime capability is the acceptance condition.
The audited wheel reference is PyYAML 6.0.3, already selected by `uv.lock`.
Its CPython 3.12–3.14 standard-ABI files cover Linux glibc 2.17+ and musl 1.2+ on x86_64/aarch64,
macOS 10.13+ x86_64 and macOS 11+ arm64. Wheel availability is distinct from devkit's tested platform support.
The reference also has Windows wheels, but this work does not promise Windows support for devkit's POSIX locks.
See `materials/installation.md` for exact evidence and exclusions.

Use a compatible PyYAML binary wheel as the normal installation route; no system libyaml development package is
needed for that route. Installation guides SHOULD show `--no-build-package pyyaml` on the documented `uv add` and
`uv tool install` routes to refuse new PyYAML source builds. Cached source-built wheels can still be reused,
so this option does not prove C availability; the runtime binding check remains authoritative.
An existing source-built installation is eligible only when `yaml.CSafeLoader` is usable.
Source-build troubleshooting is an exception route, not a new supported build matrix.
No package-version upper bound or new Python/platform support promise is introduced.

### Q2: Reader coverage and availability timing

Add `devkit_core.core.yaml` with lazy availability checking, safe value loading and node composition.
Check at the first YAML operation rather than module import or global CLI startup.
An index load that consumes previously parsed YAML is a YAML operation and MUST check availability before memo reuse.
`locate()` remains a text-only operation that needs no binding.
Do not cache a missing-binding result or let an already-selected loader conceal an unavailable installation in tests.

Migrate the production Python load/compose sites and scalar round-trip probe listed in `materials/readers.md`.
Retain `yaml.safe_dump` for output-only serialization.
Frontmatter keeps strict duplicate-key rejection, top-level mapping/string-key validation, date/datetime values,
recursive-alias identity, BOM/delimiter rules and body offsets. Standalone formats keep their current schema,
duplicate-key and empty-document behavior; this proposal does not impose frontmatter's schema on them.
Node composition uses the same C parser while validation remains in its existing owner.

### Q3: Existing values, syntax and fixers

The Planning probe on Python 3.12.3 / PyYAML 6.0.3 found 713 currently accepted Markdown headers under `docs/` and
`specs/`, with zero C-only rejections and zero value changes. This is a local corpus result, not platform coverage.
The probe excluded headers already invalid under the current parser.
The synthetic `key:\tvalue` input changes from a Python scanner failure to C acceptance; this is intentional.
Both parsers rejected duplicate keys, unsafe Python tags and impossible dates in the focused probe.
Remove Python-parity tests, scanner-character routing and event-depth preflight; test C behavior explicitly.
Do not claim byte-for-byte Python diagnostics or a YAML 1.2 grammar.

Keep fixers' targeted text replacements. Preserve unrelated fields, comments, quote style, CRLF and body bytes.
Validate a replacement with the canonical parser before writing; refuse unsafe repairs without modifying the file.
Test Unicode node positions and recursive/deep inputs explicitly; handle constructor errors without fallback.

### Q4: Error semantics

Introduce `YamlBindingUnavailableError`, a sibling of `FrontmatterError` under `DevkitCoreError`, with code
`YAML_BINDING_UNAVAILABLE`. It MUST be an execution failure (CLI exit 2), including `--format json` and `--strict`.
It MUST NOT inherit from `FrontmatterError`, `yaml.YAMLError` or `ValueError`, because those are caught as bad input.
Its deterministic action instructs the agent to reinstall PyYAML from a compatible binary wheel in the environment
that runs devkit and rerun the command. Include that interpreter/environment in the diagnostic when available.
The implementation MUST audit broad exception handlers too; a sibling type alone does not prove propagation.
The same error must reach the existing CLI and MCP advisory boundaries without library printing or a raw traceback.

Malformed YAML keeps the owning format's existing code and exit/notice semantics. An invalid indexed document still
produces `SPEC_DOCUMENT_INVALID` while valid documents stay usable; a missing binding aborts the operation instead.
Retain parser problem/context marks as structured information. File readers report a workspace-relative path and
1-based document line/column when marks exist; frontmatter adds the opener-line offset. CLI item inputs identify
their supplied path or stdin. A constructor failure without marks reports the source and reason without inventing
coordinates. Actions instruct the agent to correct the indicated YAML and rerun validation.

### Q5: Typed metadata operations

Existing proposal/spec creation, proposal acceptance/PADR creation, workflow binding, entrypoint apply and envelope
authoring already serialize typed records. Prefer those commands for their owned operations.
No additional generic metadata writer is justified by this parser defect.
Manual frontmatter editing remains supported. Update the source `document-writing` instruction with concise
indentation, quoted ambiguous scalar and block-scalar examples and the canonical contract reference.

## 3. Proposed Design & Impact

### Planning decision and alternatives

Choose required lazy C parsing over the current compatibility fallback or fail-at-import behavior.
The former leaves parser-dependent results; the latter blocks commands that do not read YAML.
Use one shared implementation boundary while leaving format schemas and serialization ownership in place.

### Development sequence

1. Add the shared parser and distinct binding error in devkit-core. Replace frontmatter's fallback routes and test
   C syntax, duplicate handling, aliases, safe construction, deep inputs and missing-binding imports/reads.
2. Migrate standalone readers and node consumers. Update index memo fingerprints to include the shared module and
   check availability before warm-cache use. Verify error propagation and no writes on dependency failure.
3. Verify fixers and generated YAML round trips, including Unicode marks, comments, quoted text and line endings.
   Add installed-wheel consumer coverage in the existing `tests/e2e/smoke.sh` scenarios, including dist without agt.
   Keep `scripts/smoke.sh` as the thin entrypoint.
4. Reconcile the affected contracts and installation guide. Update source agent guidance and run normal sync;
   generated deployment receipts and projections are only outputs of that tool, never manually edited sources.

### Acceptance checks for the Development spec

| ID | Given / When / Then |
| --- | --- |
| AC-1 | Given each inventoried Python YAML read/compose path, when it reads YAML, then it uses the shared C boundary and its existing format schema. A source audit finds no Python-loader fallback in production readers. |
| AC-2 | Given an unavailable C binding, when a value read, composition, cold/warm index load or fixer runs, then `YAML_BINDING_UNAVAILABLE` reaches the boundary as exit 2, with one JSON error object under JSON mode and no file writes or invalid-document substitution. Non-YAML help and text-only locate still work. |
| AC-3 | Given representative valid/invalid frontmatter, when parsed or indexed, then C acceptance, strict duplicate-key policy, date types, aliases and existing delimiters hold. Malformed input retains its owner code and source location when available. |
| AC-4 | Given comments, Unicode before an edited node, quoted scalars, flow/block lists and CRLF, when an existing fixer rewrites a supported field, then unrelated text and body bytes remain identical and the result reloads under C parsing. Unsupported repairs leave bytes unchanged. |
| AC-5 | Given a previously persisted memo, when the shared parser implementation changes, then the fingerprint invalidates it. A warm memo cannot hide a missing binding. |
| AC-6 | Given installed wheels and the documented installation route, when the smoke consumer parses YAML, then CSafeLoader is present and parsing succeeds; a simulated missing binding returns the same execution advisory for dist-only and harness consumers. |
| AC-7 | Given typed CLI record creation and scalar quoting, when the emitted YAML is read through C parsing, then typed values and existing schema validation hold. Guidance names the canonical syntax and supported installation route. |

### Challenger review disposition

The medium Challenger pass found two P2 issues: an unsupported uv install option and an omitted installed-consumer
scenario owner. Both are folded into this proposal. The documented routes use `--no-build-package pyyaml`, with
runtime checks authoritative for cached wheels. Development owns `tests/e2e/smoke.sh` for the existing scenarios.
The Host reverifies those changes; no findings are waived and no design question remains open.

### Contract reconciliation

- `CAP-DOCS-document-model`: replace compatibility grammar/diagnostic routing and extend the memo fingerprint contract.
- `CAP-DLV-workflow-envelopes` and `CAP-DLV-workflow-definitions`: document canonical Python reads and dependency failure.
- `CAP-DIST-manifest-spec`: document invocation YAML parsing and missing-binding propagation.
- `ARCH-07-deployment`, core README and installation guide: runtime prerequisite, wheel eligibility and actual test coverage.
- The PADR is promoted to an ADR by handoff; ordinary Development does not edit existing ADRs.

Run `just lint-check`, `just check` and `just test-affected` for Development's final affected content, preserving the
selector's full fallback. Run `just test-dist` and `just smoke` for the isolated installed-consumer acceptance.
Cross-platform wheel availability is metadata evidence until an actual runner verifies it; report that limitation.

### Non-goals

- Scope Excluded: browser/npm YAML parsing and viewer frontend behavior; the browser renderer is not the Python validation authority.
- Scope Excluded: a YAML 1.2 implementation, universal duplicate-key policy, generic metadata CLI or YAML style rules beyond parser-safe authoring.
- Scope Excluded: serializer replacement, general round-trip reformatting, automatic repair of malformed YAML or source-build toolchain management.
- Scope Excluded: PyYAML extension guarantees through dependency metadata, new OS support, or a full platform CI matrix.

## 4. Lifecycle & Retirement Criteria

Planning is complete when the evidence, PADR, Challenger review and reverify are committed and boundary rules pass.
`dev_effort: medium` remains appropriate: several internal packages change, with no data migration or external API
change to devkit-advisory/devkit-cli. Development still requires independent code review and reconciliation review.
`plan-accept=ask` requires the user's direction decision before Planning integration.
`proposal-handoff=ask` separately authorizes Development. Neither gate is supplied by this Planning request.
