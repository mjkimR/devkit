---
id: FB-presentation-fallback-field-unused
title: The presentation language fallback field is now always false
scope: repo
kind: suggestion
category: other
target: devkit_dist.features.project.models.presentation.PresentationLanguage.fallback and devkit config show presentation_language
skill: spec-sync
agent: claude-code
origin: agent
severity: noise
recurring: false
status: dismissed
created_at: 2026-10-22
---

# [FB-presentation-fallback-field-unused] The presentation language fallback field is now always false

Nature: a dead output field left for write-boundary reasons.

## 2. Suggestion / Change Request

- **Current Procedure**: Configuration validation refuses unsupported `[presentation] language` values, so `resolve_language` always returns `requested == resolved` and `fallback=false`; `devkit config show` still prints both.
- **Proposed Procedure**: Drop `fallback` (and possibly `requested`) from `PresentationLanguage` and the `config show` JSON, and update the three `docs/development/reference/` quick references that list it, in one change.
- **Expected Benefit**: Less agent context per `config show` and no field implying a fallback that cannot happen.
- **Cost & Risk**: Breaking output change (allowed in place while there are no external consumers); the quick references and `CAP-DIST-sync-and-transactions` must change together.
- **Attempted**: Not attempted; `docs/development/reference/` was outside this unit's write boundary.

## Diagnostic Details

- **Reproduction**: Read `resolve_language` after `SPEC-feedback-quick-fixes`.
- **Expected / Actual**: Expected no always-constant field; actual `fallback` is always `false`.
- **Versions**: Unit base 490b0b28.
- **Conditions**: not applicable.
- **Workarounds Attempted**: not applicable.
- **Related Assets**: `packages/devkit-dist/src/devkit_dist/features/project/services/presentation.py`, `CAP-DIST-sync-and-transactions`, `docs/development/reference/distribution.md`, `host.md`, `integration.md`.

## Evidence

```text
return PresentationLanguage(requested, requested, config.sources["presentation.language"], False)
reference docs: "reports the requested and resolved language, source and fallback"
```

## Disposition

Dismissed as moot. Under the user decision recorded with the return to build-verify (`decisions/02-return-build-verify.yaml`), an unsupported `[presentation] language` again resolves to `en` with `fallback=true`, and `language_notices` reads that field to return the `PRESENTATION_LANGUAGE_UNSUPPORTED` warning from `devkit sync`, `devkit status` and `devkit config show`. The field is no longer constant or unused.
