---
id: PLAN-canonical-libyaml-only
spec: SPEC-canonical-libyaml-only
---

# Technical Plan: `SPEC-canonical-libyaml-only` Require libyaml for consistent YAML parsing

## 1. Constitution & Invariant Review

- `ARCH-07-deployment` keeps package wheels and consumer installation routes authoritative. PyYAML's optional C extension needs a runtime check because the dependency metadata cannot require it.
- `ADR-require-the-libyaml-safe-parser-at-yaml-read-boundaries` selects lazy LibYAML safe parsing for Python YAML reads, distinct execution failure for a missing binding, unchanged format schemas and surgical fixer edits.
- `ADR-content-keyed-document-parse-memo` and `ADR-parse-memo-location-and-format` require the memo fingerprint to cover every parse implementation and reuse only under the matching fingerprint.
- Package boundaries keep the parser and dependency error in `devkit-core`; application readers call its API, while format validation stays in each owning package.
- No invariant conflict requires another ADR.

## 2. Architecture Overview & Impact

The parser boundary lives in `devkit_core.core.yaml`. It lazily checks `yaml.CSafeLoader`, exposes safe value loading and node composition, and raises `YamlBindingUnavailableError` for an absent binding. `devkit_core.core.frontmatter` uses that boundary and retains frontmatter-specific duplicate-key and document validation.

`devkit-spec` migrates document parsing, index memo reuse, glossary loading, node-based governance, proposal report reads and scalar validation. `devkit-dist` migrates bundle invocation parsing. `devkit-agt` migrates workflow decision, envelope and CLI YAML reads. Each reader preserves its existing format schema and input error contract. No new runtime dependency is introduced.

The bundle's source `document-writing` instruction and the supported installation guide explain LibYAML-compatible frontmatter and binary-wheel installation. Existing `tests/e2e/smoke.sh` scenarios verify dist-only and harness wheel consumers. Living Spec changes occur at `living-spec-draft`, after implementation review.

## 3. Component & Interface Design

```text
devkit-dist / devkit-spec / devkit-agt readers and fixers
                         |
                         v
              devkit_core.core.yaml
              require_libyaml() -> None
              safe_load(text, *, source) -> object
              safe_compose(text, *, source) -> yaml.Node | None
                         |
                         v
             yaml.CSafeLoader / yaml.compose
```

The functions check binding availability at each operation. A missing extension raises `YamlBindingUnavailableError`, which derives from `DevkitCoreError` and not from `FrontmatterError`, `yaml.YAMLError` or `ValueError`. It carries the stable code `YAML_BINDING_UNAVAILABLE`, execution-failure semantics, source context and a deterministic action to reinstall PyYAML with a compatible binary wheel in the active environment.

`safe_load` and `safe_compose` preserve the original PyYAML exception and its problem/context marks. Callers translate malformed data into their current advisory code and add a workspace-relative path or supplied input name. Frontmatter adds the header's document line offset. Errors without a parser mark do not claim coordinates.

`DocumentIndex.load` checks availability before memo reuse. `FINGERPRINT_MODULES` includes `devkit_core.core.yaml`, so a parser change invalidates cached entries. `locate()` stays independent because it only scans delimiters.

Frontmatter defines a strict loader on `CSafeLoader` and keeps duplicate-key, mapping and string-key validation. Standalone formats call the shared safe loader without inheriting frontmatter-only checks. Node consumers use `safe_compose`; node type checks and field-specific validation remain local.

Fixers construct replacement text without reserializing whole documents, parse the proposed value through the shared loader, and write only after validation. A binding error or failed validation leaves the source bytes unchanged.

## 4. Storage & State Management

The memo format does not change. The parser fingerprint changes because its named module list adds the shared YAML boundary. Old entries are rebuilt on the next index load. No migration or memo deletion is required.

Installation changes no package version floor. The uv project/tool installation route passes `--no-build-package pyyaml` to refuse new source builds; runtime verification remains authoritative because cached source-built wheels can be reused.

## 5. Error Handling & Edge Cases

- Missing `CSafeLoader` fails at the first YAML read or composition, including an index operation with a warm memo. It does not fail module import, non-YAML help or `locate()`.
- The dependency error remains outside malformed-data exception translation, broad fallback and fixer best-effort catches. Advisory boundaries return it as execution failure with exit `2` and one JSON error object in JSON mode.
- LibYAML syntax failures retain each reader's existing invalid-input code, exit or notice behavior. Indexed malformed documents remain `SPEC_DOCUMENT_INVALID`; one malformed document does not hide valid documents.
- Parser marks use UTF-8 input and 1-based line/column values. Frontmatter maps header-relative lines to the original file. Character offsets used by fixers are not confused with byte offsets.
- Safe parsing rejects unsafe Python object tags. The C parser may accept or reject syntax differently from PyYAML's Python parser; no fallback restores the old grammar.
- Fixers validate before atomic or targeted writes. Tests assert complete source-byte preservation when validation or binding checks fail.
- Output-only `yaml.safe_dump` calls and browser/npm parsing are outside this change.

## 6. Verification & Test Plan

Map AC-01 and AC-03 to `packages/devkit-core/tests/unit/core/test_yaml.py` and `test_frontmatter.py`, plus spec document parse and index unit/integration tests. Cover missing bindings by deleting or monkeypatching `CSafeLoader`, including a warm memo.

Map AC-01, AC-04 and AC-05 to existing governance, proposal-report, workflow decision/envelope, invocation and entrypoint integration tests. Add or extend cases for error propagation, parser marks, comments, Unicode offsets, quoted values, LF/CRLF and unchanged bytes on refusal.

Map AC-06 to document memo unit and integration tests. Map AC-07 to `tests/e2e/smoke.sh` and its installed dist-only/harness environments. Run `just test-affected`, preserving its full fallback, `just test-dist`, `just test-e2e` for changed end-to-end flows, `just smoke`, `just lint-check`, `just check` and `just rules-check`. Run the named viewer frontend check only if a frontend change is approved; the browser is currently out of scope.
