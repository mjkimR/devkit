---
id: PROP-adaptive-package-extraction-target
title: Target Living Spec Structure for PROP-adaptive-package-extraction
status: draft
proposal: PROP-adaptive-package-extraction
created_at: 2026-11-10
# The Living Spec files this proposal changes, one "- file: <workspace-relative path>" each;
# devkit spec scope compare reads them to find overlaps with other work.
targets:
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-development.md
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
  - file: docs/usecases/delivery/UC-advance-an-idea.md
  - file: docs/usecases/delivery/UC-import-third-party-agent-assets.md
  - file: docs/architecture/ARCH-05-1-containers.md
  - file: docs/architecture/ARCH-05-2-components.md
  - file: docs/architecture/ARCH-07-deployment.md
  - file: docs/decisions/2026-11/20261102-adaptive-development-and-research.md
  - file: docs/decisions/2026-11/20261106-skill-local-swarm-roles.md
---

# [Blueprint] PROP-adaptive-package-extraction: Target Living Spec Structure for Extract adaptive development into a devkit-adaptive distribution

This document defines the target blueprint of how the docs/ backbone (Living Spec) will evolve if proposal PROP-adaptive-package-extraction is accepted. It represents a hypothesis plan subject to adjustment during implementation. Upon handoff, it is copied into specs/ to serve as a baseline for plan.md boundaries and reconcile.md targets.

---

## 1. System Capabilities Plan (docs/capabilities/)

- `CAP-DLV-adaptive-development`:
  - `entrypoints`: the four paths move to
    `packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/`.
  - §1: "catalog bundle" becomes the bundle of the `devkit-adaptive` distribution; a sentence names
    the decision promoted from `PADR-adaptive-dev-distribution` as the owner of the packaging.
  - §2 Scope Excluded: "new wheel" is removed. The runtime scheduler, agent bus, model routing and the other
    exclusions stay.
  - Rule 2: "MUST install with devkit-docs and devkit-adaptive without a devkit-spec distribution", with the moved
    end-to-end test path.
  - Rules 1, 18, 26, 27, 28 and 38 and the paragraph after rule 39: the test paths move to
    `packages/devkit-adaptive/tests/`. Rule 15 names the package's integration and installed-consumer tests instead
    of "catalog integration" tests.
  - §4 "Distribution and entry": "Install devkit-docs and devkit-adaptive". The sentence "No adaptive-development
    runtime or CLI is added" stays; this unit adds neither.
  - §4 "Evidence-scoring test support": the scorer command path moves to
    `packages/devkit-adaptive/tests/support/adaptive_behavior_scorer.py`.
- `CAP-HARN-agent-guidance`: the `entrypoints` path of the adaptive-dev skill moves; the section "Adaptive
  development entry and current context" says "Install devkit-docs and devkit-adaptive" and drops "catalog" from
  "`adaptive-dev:core` catalog bundle". The deep-research entry and text stay.

No rule number, code, sentinel or agent-facing behavior changes.

---

## 2. Use Cases Plan (docs/usecases/)

- `UC-advance-an-idea` and `UC-import-third-party-agent-assets`: the `entrypoints` paths move (two each). No flow,
  step or extension changes: the move changes no agent or user flow.

---

## 3. Architecture & Decision Impact (docs/architecture/ & docs/decisions/)

- `ARCH-05-1-containers`: the container diagram and the package list gain `packages/devkit-adaptive`
  (`devkit-adaptive` wheel) beside the catalog; section 2.7 describes it as the owner of the `adaptive-dev` bundle,
  tested against the manifest reader of `devkit-dist`.
- `ARCH-05-2-components`:
  - Section 1 names `devkit_adaptive` among the packages that own their extensions.
  - Section 1.1: `adaptive-dev` leaves the sentence on the content-only catalog, which keeps `deep-research`,
    `uiux-improve` and `design-explore`. A new sentence states that `devkit_adaptive` owns the opt-in `adaptive-dev`
    bundle under `devkit_adaptive/bundles/adaptive_dev/bundle/`, holds no feature, runtime module or dependency
    until its first command, and keeps the bundle independent of `deep-research`. The sentences on the swarm
    archetypes, the import entry and reuse by external callers stay with the new owner.
- `ARCH-07-deployment`:
  - The paragraph "The devkit-catalog wheel registers `adaptive-dev = ...`" becomes: the `devkit-adaptive` wheel
    registers `adaptive-dev = "devkit_adaptive.bundles.adaptive_dev"`; a clean installation uses devkit-docs plus
    `devkit-adaptive` without `devkit-spec`; the moved end-to-end test path. The following paragraph on
    `deep-research` starts with "The devkit-catalog wheel registers" instead of "The same wheel registers".
- New decision: `PADR-adaptive-dev-distribution`, promoted at handoff. It supersedes in part
  `ADR-adaptive-development-and-research`.
- `ADR-adaptive-development-and-research`: stays `accepted`; gains the line "Superseded in part by" the promoted
  decision, naming the owning-wheel clauses of the adaptive-dev bundle, and a reference repair in its Confirmation
  section: the adaptive-dev test paths and the sentence that `tests/e2e/smoke.sh` lists `adaptive-dev` in the
  catalog bundle set. Its clauses stay as written.
- `ADR-skill-local-swarm-roles`: wording repair of the sentence "`ARCH-05-2-components` restates catalog ownership"
  to name the bundle's owner; no decision changes.

---

## 4. Development Conventions & Governance (docs/development/ & .devkit/)

- Root `AGENTS.md` package table and root `README.md` (package list, module and short names, namespaces, README
  links) name `devkit-adaptive`.
- `packages/devkit-adaptive/README.md` is new; `packages/devkit-catalog/README.md` loses the adaptive-dev row and
  section.
- `guides/INSTALL_GUIDE.md`, `guides/install/existing-repository.md`, `guides/install/new-repository.md`,
  `guides/install/adaptive-dev-sdd-adoption.md` and `guides/install/bundle-recommendations.md` name
  `devkit-adaptive` as the package of `adaptive-dev` for a fresh installation: devkit-docs beside `devkit-adaptive`,
  without `devkit-spec`. No guide gains a step for a project that selected the bundle before the move.
- `.devkit/architecture.toml` declares `devkit_adaptive` and removes the `adaptive_dev` data root of the catalog.
- `scripts/releases/prepare.py` looks up a moved bundle's baseline identity by bundle name. `ARCH-07-deployment` 1.1
  already states the rule it implements, so that section needs no new sentence.

---

## 5. System Before & After Comparison (Before & After)

| Aspect | Before | After |
| --- | --- | --- |
| Owner of the `adaptive-dev` bundle | `devkit-catalog` (content only) | `devkit-adaptive` |
| Entry point | `adaptive-dev = "devkit_catalog.adaptive_dev"` | `adaptive-dev = "devkit_adaptive.bundles.adaptive_dev"` |
| Runtime requirements of the owning wheel | None | None; `PROP-adaptive-assignment-cli` adds the requirement on `devkit-docs` with the first commands |
| Python code beside the bundle | None | Three docstring-only initializers |
| Bundle name, presets, asset IDs, asset bytes | `adaptive-dev`, `core`, `agents`, `import` | Unchanged |
| Requires `devkit-spec` | No | No |
| Installation for adaptive development | devkit-docs plus `devkit-catalog` | devkit-docs plus `devkit-adaptive` |
| Installation for the `agents` and `import` presets | `devkit-dist` plus `devkit-catalog` suffice | `devkit-dist` plus `devkit-adaptive` suffice |
| Migration path for a selection made before the move | Not applicable | None: nothing uses the bundle outside this repository |
| Bundle version at the next release | `0.1.6` until its content changes | Unchanged rule: release preparation finds the moved bundle by name |
