---
id: PLAN-rename-incubation-to-adaptive-dev
spec: SPEC-rename-incubation-to-adaptive-dev
---

# Technical Plan: `SPEC-rename-incubation-to-adaptive-dev` Rename incubation to adaptive-dev and disambiguate proposal terms

## 1. Constitution & Invariant Review

- `ADR-adaptive-dev-approach-name` already records the naming decision and replaces the value set of
  `ADR-own-development-approach-policy-outside-sdd` and the bundle, entry and context-file names of
  `ADR-keep-incubation-guidance-opt-in-and-current-state-based`; no further ADR is needed.
- `ADR-immutable-decisions-editable-records` makes canonical-ID rewrites and one-line pointers editorial ADR edits;
  decision text stays.
- `ADR-document-id-aliases`: renamed documents keep the old ID in `aliases`, and `RULE-document-reference` reports an
  alias reference in a current document, which `devkit rules fix` rewrites.
- `ARCH-05-2-components`: `devkit_catalog.adaptive_dev` is a content-only regular package beside the other catalog
  bundles; `.devkit/architecture.toml` lists its data root. No layer or dependency changes.
- `CAP-DLV-idea-incubation` and `CAP-DIST-sync-and-transactions` keep their rules; only names change.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `devkit-dist` `features/project/models/development.py` | `Literal["sdd", "adaptive-dev"]`, check, message and `fix` |
| `devkit-dist` `features/distribution/services/installation/config.py` | template comment `sdd or adaptive-dev` |
| `devkit-spec` delivery `attach`, `integration`, `cleanup`; governance `applicability`, `hygiene`; policy `lifecycle` | compare `"adaptive-dev"`; output text names adaptive-dev |
| `devkit-spec` `features/delivery/cli/proposals.py`, `features/proposals/__init__.py` | help and docstrings use "Plan" and the renamed proposal capability ID |
| `devkit-spec` spec bundle `AGENTS.md.jinja`, `guidance/spec-pointer.md`, `skills/spec/SKILL.md.jinja`, `playbooks/sdd-baseline/SKILL.md` | name `adaptive-dev` and `/adaptive-dev` |
| `devkit-agt` `features/integration/usecases/project.py` | target policy `adaptive-dev`, evidence `omitted:adaptive-dev` |
| `devkit-catalog` | `git mv` `incubation/` to `adaptive_dev/`; bundle `adaptive-dev`; skill, pointer and researcher renamed; entry point in `pyproject.toml` |
| Living Spec | six documents renamed with aliases; prose in capabilities, use cases, architecture, development docs, READMEs and glossary |
| `guides/` | `install/adaptive-dev-sdd-adoption.md`; anchors and bundle names |
| Repository tooling | `.devkit/architecture.toml` data root, `tests/e2e/smoke.sh`, sync outputs `AGENTS.md` and `.devkit/installation.json` |

No new dependency. `uv.lock` records the workspace packages, not their entry points, so it changes only if
`uv lock --check` reports it.

## 3. Component & Interface Design

```python
# devkit_dist.features.project.models.development
class DevelopmentConfigError(ConfigError):
    code = "DEVELOPMENT_CONFIG_INVALID"
    fix = 'Use [development] approach = "sdd" or "adaptive-dev" in .devkit/config.toml'

class DevelopmentApproach(BaseModel):
    approach: Literal["sdd", "adaptive-dev"] = "sdd"
```

```toml
# packages/devkit-catalog/pyproject.toml [project.entry-points."devkit.bundles"]
adaptive-dev = "devkit_catalog.adaptive_dev"
```

```toml
# devkit_catalog/adaptive_dev/bundle/bundle.toml
name = "adaptive-dev"
[presets.core]
assets = ["adaptive-dev", "adaptive-dev-pointer", "product-clarifier", "product-researcher", "usage-reviewer", "current-context-template"]
```

Text substitutions, applied by hand per file so history and legacy mentions are kept:

| Old | New |
| --- | --- |
| approach value `incubation` | `adaptive-dev` |
| "incubation" as the approach in prose | "adaptive development" |
| `/incubate`, skill `incubate` | `/adaptive-dev`, skill `adaptive-dev` |
| `incubation-pointer`, `incubation-researcher` | `adaptive-dev-pointer`, `product-researcher` |
| `.devkit/incubation.md`, `.devkit/managed/incubation/` | `.devkit/adaptive-dev.md`, `.devkit/managed/adaptive-dev/` |
| `get-context incubation`, `devkit add incubation`, `incubation:core` | `get-context adaptive-dev`, `devkit add adaptive-dev`, `adaptive-dev:core` |
| "proposal incubation", "Incubate proposals" | "proposal Planning", "Plan proposals" |

## 4. Error Handling & Edge Cases

- A configuration naming `"incubation"` gets `DEVELOPMENT_CONFIG_INVALID`; a selection of `incubation` gets
  `SELECTION_INVALID`. Both are existing refusals; no new code path.
- A committed snapshot naming `"incubation"` is parsed by the same function and refused the same way.
- The split's legacy keys and paths (`incubation:<role>`, `.devkit/overrides/incubation/subagents/`,
  `.devkit/transient/incubation-research/`) stay, so the deep-research migration text and its tests keep working.

## 5. Verification & Test Plan

| Scenario | Evidence |
| --- | --- |
| AC-01 | `git ls-files -z \| xargs -0 rg --hidden -i -n incubat`, classified by a scratch script under the ignored `.devkit/transient/probe/`; zero lines outside the allowlist |
| AC-02 | `just test devkit-dist tests/integration/features/project/test_development.py` |
| AC-03 | `just test devkit-spec`, `just test devkit tests/integration/features/integration` (through `just test-affected`) |
| AC-04 | `just test devkit-catalog tests/integration/bundles tests/e2e/bundles` |
| AC-05 | `just smoke` |
| AC-06 | `uv run devkit docs resolve <old ID>` for the six old IDs; `just rules-check` |
| AC-07 | `just test devkit-spec tests/integration/bundles/spec tests/e2e/bundles/spec`; `uv run devkit spec proposal --help`; `uv run devkit sync` then `uv run devkit sync --check` |

Package checks: `just lint-check <module>` and `just check <module>` for devkit-dist, devkit-spec, devkit (agt),
devkit-catalog and devkit-docs; `just test-affected` with its `mode=full` fallback for the final content. The
pre-existing failure `test_fixes_carry_no_placeholder` (FB-envelope-commit-fix-placeholder-fails-output-contract) is
reported, not fixed.
