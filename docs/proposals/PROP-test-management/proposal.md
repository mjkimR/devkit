---
id: PROP-test-management
title: Evidence-based test management playbook
summary: "Evaluate a reusable test-management playbook for consumer repositories using a preserved implementation draft. Establish evidence, scope and verification criteria before adopting runner, tiering or integration guidance."
status: draft
created_at: 2026-11-05
target_area: capabilities/delivery/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/
    - packages/devkit-catalog/tests/integration/bundles/test_bundles.py
    - docs/capabilities/delivery/
    - docs/usecases/
  excludes:
    - packages/devkit/src/
    - .devkit/config.toml
    - .github/workflows/
    - justfile
    - scripts/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-test-management] Evidence-based test management playbook

## 1. Background & Hypothesis

Research about test practices for devkit and other reference repositories produced an implementation-shaped
playbook instead of the requested proposal. The available input contains four playbook files, bundle registration
and integration-test edits. It contains no source bibliography, reference-repository inventory, measured baseline
or trial report. Preserve that work as a candidate design without treating its directives as accepted policy.

The hypothesis is that an opt-in test-management playbook can help agents assess test boundaries, isolation and
runner costs across consumer repositories, then propose changes grounded in the consumer's own contracts.
The existing draft combines these concerns with branch promotion and verification policy; Planning must decide
whether that latter scope belongs in the same playbook.

The original text and registration/test diff are preserved byte-for-byte in [materials](materials/README.md).
They are research inputs, not deployed assets or passing-check evidence. The source playbook and its registration
have been removed from the distributable bundle; existing bundle behavior is unchanged.

## 2. Technical Spike Questions

- **Q1 — Scope and reuse:** Which assessment steps are independent of Python, pytest, `just` and devkit?
  Should pytest guidance be a conditional reference? Does integration-policy design belong here or in separate
  future work? Compare overlap with `CAP-DLV-performance-pass` and `CAP-DLV-review-refactor`.
- **Q2 — Repository contracts:** How does the playbook discover and preserve the consumer's existing test-tier,
  affected-selection and integration requirements? Compare the draft against `ARCH-05-2-components` and
  `ADR-post-merge-verification` as devkit-specific counterexamples, not universal consumer rules.
- **Q3 — Evidence:** What measurements justify parallel execution, worker count, recipe separation and duration
  thresholds? Validate tool-specific commands and examples against official documentation for the tested versions.
  Record startup/collection cost and resource isolation before recommending configuration changes.
- **Q4 — Safe execution:** How can baseline measurement avoid contacting live services or modifying shared data?
  Define preflight discovery, unavailable-environment handling and the boundary between assessment and authorized
  changes. Avoid classifying all integration tests as necessarily in-memory or all subprocess tests as e2e.
- **Q5 — Transfer:** Which actual reference repositories motivated the draft, and can they be inspected?
  Obtain their identities and research sources before claiming cross-repository validation. If unavailable,
  record that limitation and use explicitly labelled examples.

## 3. Proposed Design & Impact

### Candidate direction

Retain an explicitly invoked or confirmed maintenance playbook as the initial candidate. Its core would inspect
repository contracts and commands, establish a bounded baseline, report evidence and uncertainties, and present
proposed changes for a decision. Load runner-specific references only when the inspected repository uses them.
Planning may revise this structure or choose narrower additions to existing assets.

Treat the draft's fifteen-second split, two-second serial threshold, eight-worker cap, automatic marker mapping,
blanket e2e exclusion and database/environment fixtures as hypotheses. Do not carry them into adopted guidance
without evidence and conditions. Existing consumer requirements take precedence over illustrative recipes.

The integration-policy reference requires separate scope review. Nightly verification cannot replace a required
check of the integrated result, and passing a full suite cannot guarantee a permanently stable branch. This
proposal does not authorize changes to devkit's branch model, CI cadence or final verification policy.

### Expected scope if accepted

- A bounded opt-in catalog asset, with its registration/preset chosen during Planning.
- Packaging and behavior-oriented checks for selection, conditional loading and authorization boundaries.
  The archived string-presence tests are examples of intended coverage, not evidence of procedural correctness.
- A capability and linked use case for retained behavior; related documentation updates only where necessary.
- No new feature dependency edges or runtime implementation are proposed.

### Candidate acceptance evidence for Development

Planning must refine these into verifiable spec criteria before implementation:

- With the asset unselected, bundle resolution and deployment remain unchanged.
- On assessment, the agent identifies the repository's actual commands and policies before executing tests;
  unavailable prerequisites or unsafe external-resource configuration produce an explicit limitation.
- Before an authorized change, the report separates observations, measured results, proposed changes and
  unresolved assumptions; an unattended run applies no changes.
- A walkthrough in devkit preserves its affected-test selection, full fallback and final integrated-head checks.
- A contrasting non-pytest example avoids imposing pytest, `just` or devkit-specific document IDs.
- Runner-specific recommendations have versioned primary references and measured applicability; synthetic
  examples are labelled and never reported as validation of an unidentified reference repository.
- Bundle checks and relevant affected tests pass; claimed performance improvements include comparable evidence.

### Non-goals

Installing or activating this draft; rewriting the repository's test layout or runner; repairing application
bugs; changing branch promotion, CI or verification policy; adding runtime frameworks or defensive governance
layers. Any independent integration-policy redesign requires separately scoped work before implementation.

## 4. Lifecycle & Retirement Criteria

Keep this proposal in `draft` until Planning resolves the scope and evidence questions. The preserved draft grants
no direction acceptance or Development handoff. Continue with `/spec-next` for `PROP-test-management` when selected.

On acceptance, use the proposal lifecycle to record the chosen direction and hand off to a feature spec before
changing shipped assets. Preserve useful source material through handoff. If rejected, retain the user's reason
through the normal proposal retirement process. Do not restore the archived implementation automatically.
