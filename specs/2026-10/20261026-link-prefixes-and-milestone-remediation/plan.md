---
id: PLAN-link-prefixes-and-milestone-remediation
spec: SPEC-link-prefixes-and-milestone-remediation
---

# [PLAN-link-prefixes-and-milestone-remediation] Viewer ID link prefixes and milestone path remediation

## 1. Constitution & Invariant Review

None. Both fixes restore agreement with existing contracts (`CAP-DOCS-document-model` ID grammar,
`CAP-VIEW-repository-viewer` §4 links by ID, `CAP-GOV-spec-rules` milestone location) and need no ADR. Neither
capability states the viewer prefix list or the remediation text, so no Living Spec sentence changes.

## 2. Architecture Overview & Impact

- `packages/devkit-viewer/frontend/src/lib/api/documents.ts`: the prose reference pattern in `renderDocument` lists
  the prefixes of `PREFIXES` in its order: `CAP|UC|ARCH|ADR|PROP|PADR|SPEC|PLAN|TASKS|REC|FB|MAT|MS`. The committed
  page under `packages/devkit-viewer/src/devkit_viewer/static/` is rebuilt with `just viewer build`. Serves
  `SPEC-link-prefixes-and-milestone-remediation` AC-01 and AC-02.
- `packages/devkit-spec/src/devkit_spec/features/governance/usecases/id_convention.py`: `_target` gives
  `Kind.MILESTONE` its own remediation, "Rename or move the file to docs/roadmap/MS-{slug}.md (the ID is the file
  stem), then run `devkit rules fix`", before the Living Spec and dated branches, which keep their text. Serves AC-03
  and AC-04.

No new dependency.

## 6. Verification & Test Plan

- Red then Green: a vitest case in `frontend/src/lib/documents.test.ts` for AC-01 and AC-02; a rule test in
  `rules/id_convention/tests/test_rule.py` for AC-03 and AC-04. Both stay as regression tests.
- Checks: `just viewer lint`, `just viewer check`, `just viewer test`, `just viewer build`;
  `just lint-check devkit-spec`, `just check devkit-spec`; `just test-affected`;
  `uv run devkit rules check --ci --base b38cf17b`.
