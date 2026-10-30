---
id: PLAN-deep-research-bundle
spec: SPEC-deep-research-bundle
---

# Technical Plan: `SPEC-deep-research-bundle` Split explicit deep research into an approach-neutral bundle

## 1. Constitution & Invariant Review

- `ADR-split-deep-research-bundle` and `ADR-retain-research-as-cited-materials` are accepted and already promoted;
  they supersede `ADR-extend-incubation-with-optional-discovery-teams` and
  `ADR-keep-discovery-plans-distinct-from-delivery-commitments` through their `supersedes` fields. No further ADR is
  needed.
- `ADR-document-and-sdd-bundles` (no asset has two owners, no cross-bundle dependency engine) holds: every moved
  asset has exactly one owner after the change, and no dependency is declared.
- `ARCH-05-2-components`: the catalog stays content-only; the new bundle adds no runtime module. `RULE-architecture`
  needs `deep_research` among the catalog `data_roots` in `.devkit/architecture.toml`.
- `CAP-DIST-agent-projections` already projects `invocation = "user"` natively on Codex and Claude Code; no
  distribution change.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `packages/devkit-catalog/src/devkit_catalog/deep_research/` | New bundle: `__init__.py`, `bundle/bundle.toml`, skill `deep-research` with three references, four subagent contracts |
| `packages/devkit-catalog/src/devkit_catalog/incubation/bundle/` | Drops `incubate-research` and the three moved roles; text edits in `AGENTS.md`, the pointer, `/incubate`, its `discovery`, `delegation` and `current-context` references, the template and the researcher's scratch clause |
| `packages/devkit-catalog/pyproject.toml` | Entry point `deep-research = "devkit_catalog.deep_research"` |
| `packages/devkit-catalog/tests/` | New `integration/bundles/test_deep_research.py` and `e2e/bundles/deep_research/test_installed_consumer.py`; `test_incubation.py` and the incubation e2e test drop the moved assets |
| `packages/devkit-catalog/README.md`, `guides/` | Bundle row, explicit selection, migration steps; suggestion wording removed |
| `packages/devkit-spec/.../skills/spec/` | Intake exemption in `SKILL.md.jinja`; MAT citation line in `references/proposals-catalog.md` |
| `tests/e2e/smoke.sh` | Catalog bundle set and the unselected check |
| `.devkit/architecture.toml` | `deep_research` data root |
| Living Spec | New capability CAP-DLV-deep-research; `CAP-DLV-idea-incubation`, `CAP-HARN-agent-guidance`, three use cases, `ARCH-05-2-components`, `ARCH-07-deployment`, glossary (written at `living-spec-draft`) |

No new dependency. This repository selects the spec bundle, so `devkit sync` rewrites the projected spec skill and
`.devkit/installation.json` after the spec skill change; both are committed as sync outputs.

## 3. Component & Interface Design

```toml
# packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/bundle.toml (normative)
schema = 1
name = "deep-research"
version = "0.1.5"
default_preset = "core"
# assets: deep-research (skill, invocation = "user"), direction-explorer, discovery-critic,
#         discovery-planner, research-investigator (subagent)
[presets.core]
assets = ["deep-research", "direction-explorer", "discovery-critic", "discovery-planner", "research-investigator"]
```

- Skill body: H1, then the guard line of AC-02; Constraints (authority, writes, no commit, coordinator); Procedure
  naming each reference with `before`; Completion with the retained path, MAT ID and the commit direction.
- `references/orchestration.md`: assignments for the four roles, effective contracts under
  `.devkit/managed/deep-research/subagents/`.
- `references/workspace.md`: run directories under `.devkit/transient/deep-research/`, the same
  verify-ignored-then-stop check and the shell example the e2e test executes.
- `references/synthesis.md`: the retention contract of `ADR-retain-research-as-cited-materials` (layout, index
  fields, `Status`, collision check, partial resume, citation in a code span, no commit).

## 4. Error Handling & Edge Cases

- Role-policy key of a moved role under `incubation:` fails sync with the existing `ConfigError` from
  `validate_role_overrides`; the guides name the rename (AC-05, AC-11).
- Ignored-path conflict or absent Git: allocation stops or reports, unchanged from the moved reference.
- Slug collision: the coordinator picks another slug before writing (AC-07).

## 5. Verification & Test Plan

| AC | Verification |
| --- | --- |
| AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-09 | `just test devkit-catalog tests/integration/bundles` (`test_deep_research.py`, `test_incubation.py`, `test_bundles.py`) |
| AC-08 | `just test devkit-catalog tests/e2e/bundles` (new deep-research and changed incubation installed-consumer tests) |
| AC-10 | `test_deep_research.py` reads the spec skill and proposal reference text; `just test devkit-spec tests/integration/bundles/spec` keeps the spec bundle budgets and intake tests green |
| AC-11 | `test_deep_research.py` asserts the add command and migration identifiers in the named guides and README |
| AC-12 | `just smoke` |

Also: `just lint-check devkit-catalog`, `just check devkit-catalog`, `just test-affected` (with its `mode=full`
fallback), `just rules-check`, `uv run devkit sync --check` after the sync.
