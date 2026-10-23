---
id: PROP-canonical-libyaml-only
title: Require libyaml for consistent YAML parsing
summary: Require PyYAML's LibYAML C binding for YAML parsing across frontmatter and standalone YAML inputs, and fail clearly when the binding is unavailable. Define the supported installation matrix and verify consistent parsing and error handling.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-23
target_area: capabilities/documents/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-core/src/devkit_core/core/frontmatter.py
    - packages/devkit-core/tests/unit/core/test_frontmatter.py
    - packages/devkit-spec/src/devkit_spec/features/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/instructions/document-writing.md
    - packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/invocation.py
    - packages/devkit/src/devkit_agt/features/workflow/
    - docs/capabilities/documents/CAP-DOCS-document-model.md
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-canonical-libyaml-only] Require libyaml for consistent YAML parsing

## 1. Background & Hypothesis
`SPEC-frontmatter-libyaml` currently uses the LibYAML C loader as an optimization, then routes scanner-sensitive
input and C-loader errors through the Python loader to preserve the existing grammar. Production code also reads
standalone YAML inputs, including glossary data, bundle invocation settings, workflow decision and envelope records,
and YAML supplied to workflow commands. Some frontmatter validators compose YAML nodes directly. These paths do not
all share one loader, so accepted syntax and diagnostics can depend on the call site or whether the C binding is
installed.

This proposal replaces that compatibility behavior with one implementation rule: YAML parsing uses PyYAML's
LibYAML C loader. A supported installation should select a PyYAML distribution that provides that binding. If the
binding is absent, devkit reports a stable execution failure instead of silently using the Python loader. Inputs
rejected by LibYAML remain parse failures.

## Source feedback (when this proposal receives feedback)

- `FB-canonical-c-yaml-contract`: address parser differences across frontmatter, CLI validation and fixer call sites
  by requiring the LibYAML C loader and failing explicitly when it is unavailable. The feedback remains open until
  the accepted follow-up is implemented and verified.

## 2. Technical Spike Questions
- **Q1**: Which supported Python, OS, architecture and Linux ABI combinations receive a PyYAML wheel with
  `CSafeLoader`, and what install failure should users see when no such wheel is available?
- **Q2**: Which production YAML readers should use the C loader, including frontmatter, standalone documents,
  workflow records and CLI-supplied YAML, and should the missing-binding check run at command startup or when parsing
  is first requested? Which YAML serializers only produce data and do not need loader changes?
- **Q3**: Can existing accepted documents and fixer operations retain their values and comments under the C loader,
  and which inputs should now fail because LibYAML rejects them?
- **Q4**: Which parser diagnostics can be presented consistently with the document path, line and column, a stable
  error code, and a deterministic corrective action?
- **Q5**: Which frontmatter fields are already created or updated by typed CLI operations, and are any additional
  CLI operations justified for metadata with a stable schema?

## 3. Proposed Design & Impact
Inventory production PyYAML parsing and composition call sites in the repository, distinguishing frontmatter from
standalone YAML formats and generated YAML output. Route the agreed readers through the LibYAML C loader. Remove
Python-loader fallbacks and scanner-based compatibility routing from the shared frontmatter path. Check for
`CSafeLoader` before parsing and return a stable, actionable failure if PyYAML was installed without its C binding.
Document and verify the supported installation matrix; do not require users to install a system `libyaml`
development package when a compatible PyYAML wheel is available. Keep each format's schema and validation rules
separate; sharing a parser does not make the documents interchangeable.

Prefer existing typed CLI operations for creating structured YAML records and changing workflow-managed metadata;
they can serialize known schemas without asking an agent to hand-author YAML. Add a CLI operation only where a
repeatable metadata change has a stable schema and a concrete authoring failure. Keep prose and ordinary document
editing available in Markdown editors, with `document-writing` guidance and validation for manually edited
frontmatter. Do not require every YAML edit to pass through a generic CLI writer, which would need to preserve
unrelated fields, comments and formatting across distinct document schemas.

Keep the accepted syntax defined by the selected LibYAML implementation rather than adding a second custom grammar.
Verify document validation and fixer behavior against representative accepted and rejected YAML, preserving values and
comments for any automatic transformations. Update `CAP-DOCS-document-model` with the parser requirement and failure
behavior. For malformed frontmatter, report the document path and parser location when available, explain the parse
failure, and return a stable advisory code with a deterministic action. For a missing C binding, report a distinct
code and an action that identifies the supported installation requirement. Update the source `document-writing`
instruction so agents write Markdown frontmatter in valid LibYAML-compatible YAML, with concrete guidance for indentation,
quoting ambiguous values and block scalars, and a link to the canonical contract. Keep that instruction concise and
leave unrelated YAML style preferences out of scope.

This proposal does not require unrelated parser changes or a broad YAML style guide.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr canonical-libyaml-only "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept canonical-libyaml-only --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff canonical-libyaml-only.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
