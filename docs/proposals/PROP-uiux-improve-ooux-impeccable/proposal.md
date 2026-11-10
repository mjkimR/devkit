---
id: PROP-uiux-improve-ooux-impeccable
title: OOUX-framed UI/UX improvement and Impeccable delegation
summary: "Reorient uiux-improve as an OOUX-framed coordinator for software interfaces that guides isolated Impeccable execution, manages scaffolding via gitignore or cleansing, and qualifies the skill name without backward-compatibility burden."
status: reviewing
created_at: 2026-11-06
target_area: capabilities/delivery/
priority: high
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-catalog/src/devkit_catalog/uiux_improve/
    - packages/devkit-catalog/tests/integration/bundles/test_uiux_improve.py
    - packages/devkit-catalog/tests/e2e/bundles/uiux_improve/
    - docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
    - docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
  excludes:
    - docs/decisions/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-uiux-improve-ooux-impeccable] OOUX-framed UI/UX improvement and Impeccable delegation

## 1. Background & Hypothesis

The `uiux-improve` catalog bundle currently provides high-level guidance for UI/UX improvements, with four optional
local roles (`designer`, `unconventional-designer`, `reference-researcher`, `critic`). While its boundaries and
authority rules are well-defined (`CAP-DLV-uiux-improvement`), practical usage by AI coding agents reveals several
structural and scope challenges:

1. **Overly Broad Skill Scope & Naming**: The name `uiux-improve` suggests universal design coverage. In practice,
   the skill strictly targets **software and web application interfaces** (SaaS, dashboards, admin tools, settings,
   responsive web views) rather than presentation slide decks, game loops, or video/media production. A qualified
   skill name (e.g., `app-uiux-improve`, `software-ui-improve`, or `ooux-ui-improve`) would clarify its boundaries.
   Because **no active projects or automated workflows currently consume `uiux-improve`**, this update is completely
   free from backward compatibility constraints, deprecation aliases, or migration overhead.
2. **Structural and Mental Model Drift (IA Failure)**: Agents frequently jump directly to styling or code generation
   without modeling the underlying domain entities, their relationships, and contextual actions. This causes
   fragmented screens and disjointed flows. Object-Oriented UX (OOUX) principles prevent this by anchoring the UI in
   domain Objects, Relationships, CTAs, and Attributes before visual styling begins.
3. **Surface AI Slop (Craft Failure)**: Default agent generation tends toward generic clichés—such as cards nested
   within cards, unmotivated purple/blue gradients, overused Inter font, low-contrast secondary text, and missing
   edge states (empty, loading, error).

External toolkits like `pbakaus/impeccable` excel at eliminating AI slop through battle-tested prompt systems,
granular steering (`shape`, `critique`, `polish`, `distill`, `typeset`), and deterministic detection. However:
- Vendoring `impeccable`'s complete 24-command prompt suite inside `devkit` would create severe token overhead,
  maintenance drag, and conflict with devkit's proportionate guardrail and lightweight packaging principles.
- Running `impeccable` on its own lacks structured OOUX modeling, and its initialization generates temporary
  scaffolding (`PRODUCT.md`, `DESIGN.md`, `.impeccable/`) that can pollute repository roots if not managed.

The hypothesis is that the skill achieves the highest leverage by acting as an **OOUX-grounded coordinator
and delegation guide for software interfaces**:
1. **OOUX Grounding**: Frame the interface around domain Objects, Relationships, CTAs, and Attributes first,
   establishing structural coherence.
2. **Delegation Protocol**: Package this OOUX context into an explicit delegation payload, guiding an isolated
   `impeccable` session (via separate agent session or subagent) without duplicating external prompt text.
3. **Scaffolding Isolation & Cleansing**: Prevent repository pollution by evaluating `.gitignore` isolation as a
   low-friction default for temporary scaffolding, supported by active post-run cleansing when gitignore is not desired.
4. **Qualified Naming**: Rename the skill with an explicit qualifier reflecting its software/web application scope,
   leveraging the absence of legacy consumers to perform a clean break.

### Scope and non-goals

- In-scope:
  - Qualify the skill name and identifiers to communicate its software/app focus, removing legacy aliases.
  - Update `SKILL.md` to structure the improvement procedure into OOUX Framing, Craft Execution, and Scaffolding Hygiene.
  - Update `references/design-guidance.md` with practical OOUX (ORCA) modeling rules and core anti-slop baselines.
  - Update `references/orchestration.md` with an Impeccable delegation payload template and session execution steps.
  - Define scaffolding handling options: compare `.gitignore` pattern isolation against active post-run cleansing.
  - Update Living Spec `CAP-DLV-uiux-improvement` and use case `UC-improve-an-interface-and-user-flow`.
  - Update tests in `packages/devkit-catalog/tests/` to verify self-containment, reference constraints, and boundaries.
- Non-goals:
  - Vendoring or bundling `impeccable` source code, prompt files, or npm packages into `devkit`.
  - Adding Node.js or npm runtime dependencies to `devkit-catalog` or `devkit-dist`.
  - Supporting non-software design domains (presentation decks, 3D/game graphics, video editing pipelines).
  - Preserving backward compatibility or migration bridges for the old `uiux-improve` name.
  - Mandating numeric scorecards, fixed heuristic point quotas, or comparative experiments.

## 2. Technical Spike Questions

- **Q1 — Qualified Skill Naming**: What qualified skill name best captures its software/web application focus and
  OOUX foundation (e.g., `app-uiux-improve`, `software-ui-improve`, `ooux-ui-improve`)? Confirm zero external
  breakage across all packages.
- **Q2 — OOUX Framing Depth**: How should the skill guide agents to extract domain Objects, Relationships, CTAs,
  and Attributes concisely without overwhelming the context window or demanding formal UML diagrams?
- **Q3 — Delegation Payload Format**: What structured payload should the coordinator generate for an isolated
  session or subagent executing `impeccable`? How does it enforce file boundaries and forbid unauthorized schema changes?
- **Q4 — Scaffolding Management (.gitignore vs. Cleansing)**: How should external temporary files (`PRODUCT.md`,
  `DESIGN.md`, `.impeccable/`, audit dumps) be isolated? Is adding recommended `.gitignore` patterns sufficient and
  lower-friction than requiring manual deletion after every run? When is active post-run cleansing required?
- **Q5 — Inline Fallback Execution**: When the user or environment does not have `impeccable` installed, what
  essential anti-slop rules should `references/design-guidance.md` provide directly?
- **Q6 — Packaging & Test Verification**: How will catalog integration tests verify that all files remain under the
  12KB limit, maintain self-containment without governance tokens, and preserve consumer delivery workflow authority?

## 3. Proposed Design & Impact

### 3.1 Skill naming qualification & compatibility clean break

Because no existing repository workflows or projects consume `uiux-improve`:
- The skill identifier and folder can be renamed cleanly (e.g., `app-uiux-improve`) to signal its scope: software
  applications, dashboards, and tools.
- No legacy redirection, aliases, or backward-compatibility adapters will be retained.
- The corresponding bundle metadata in `bundle.toml` and documentation will update cleanly in place.

### 3.2 Three-phase improvement procedure

Refactor `SKILL.md` into three distinct phases:
1. **Phase 1: OOUX Framing**:
   - Identify core domain Objects represented by the software interface.
   - Map Relationships between objects (parent/child, associations).
   - Define primary and secondary Call-to-Actions (CTAs) anchored to each object.
   - Enumerate key Attributes and representative states (empty, loading, populated, error).
2. **Phase 2: Craft Execution (Delegated or Inline)**:
   - *Track A (Delegated Impeccable)*: Generate a structured delegation payload containing the OOUX specification,
     target file boundaries, and step-by-step guidance for running an isolated `impeccable` session.
   - *Track B (Inline Fallback)*: Apply the design guidance directly with the existing local roles (`designer`,
     `unconventional-designer`, `critic`) when external delegation is not selected.
3. **Phase 3: Scaffolding Hygiene & Verification**:
   - Verify the visual and functional changes against project checks and responsive/keyboard states.
   - Ensure temporary scaffolding is either cleanly isolated by `.gitignore` or purged/assimilated.
   - Reintegrate clean code diffs into the consumer repository.

### 3.3 OOUX guidance in `references/design-guidance.md`

Add a dedicated OOUX section outlining the ORCA (Objects, Relationships, CTAs, Attributes) approach for software:
- Objects: Domain nouns users think in, distinct from UI widgets (e.g., "Invoice", not "Table").
- Relationships: How objects connect, establishing natural navigation paths.
- CTAs: What users do to each object, placed contextually rather than collected into global menus.
- Attributes: Information hierarchy within each object card/view, separating core identifiers from metadata.
- Baseline Anti-Slop: Minimum contrast requirements, typographic scale rhythm, and rules against arbitrary
  gradients and nested container boxes.

### 3.4 Delegation instructions in `references/orchestration.md`

Provide an explicit delegation template for external design sessions:
- Step 1: Check environment or guide user setup (`npx skills add pbakaus/impeccable` or local installation).
- Step 2: Pass the OOUX brief as the initial boundary prompt so the external session respects domain structure.
- Step 3: Recommend the execution sequence (e.g., `shape` with OOUX context -> `critique` -> `polish`).
- Step 4: Instruct the external session to touch only target UI components and avoid schema or business logic edits.

### 3.5 Scaffolding isolation options (.gitignore vs. Cleansing)

Evaluate two cooperative strategies for external tool scaffolding:
- **Strategy A (.gitignore isolation)**: Recommend adding external scaffolding entries (`PRODUCT.md`, `DESIGN.md`,
  `.impeccable/`, `*.audit.md`) to `.gitignore`. This allows developers to run Impeccable repeatedly across sessions
  without re-initialization overhead and prevents accidental commits without requiring manual cleanup steps.
- **Strategy B (Active Cleansing)**: When `.gitignore` modification is undesirable or restricted, the coordinator
  actively detects temporary files, prompts the user if key decisions should be recorded into commit messages or
  project docs, and deletes temporary files before reporting completion.

### 3.6 Expected acceptance scenarios

- **AC-1:** Given a UI improvement request for a software interface, the agent extracts domain Objects, Relationships,
  CTAs, and Attributes before proposing layout or styling changes.
- **AC-2:** Given a request with external tool delegation, the agent provides a self-contained delegation brief
  specifying target boundaries, OOUX constraints, and suggested `impeccable` command sequences.
- **AC-3:** Given an environment without external tools, the agent completes the improvement inline using the OOUX
  framing and built-in anti-slop design guidance.
- **AC-4:** Given external scaffolding files (`PRODUCT.md`, `DESIGN.md`), the agent either verifies they are safely
  isolated by `.gitignore` or cleanses them prior to completion, preventing untracked file pollution.
- **AC-5:** The updated qualified skill name clearly reflects its software interface scope, and tests verify zero
  unresolved references without requiring legacy compatibility aliases.
- **AC-6:** All bundled skill and reference markdown files remain under 12,288 bytes, contain no governance IDs,
  and pass catalog integration tests.
- **AC-7:** The skill retains existing consumer delivery authority; it grants no automatic commit or publishing rights.

## 4. Lifecycle & Retirement Criteria

Retain this proposal under `docs/proposals/PROP-uiux-improve-ooux-impeccable/`.
Planning resolves the six technical spike questions, selects the qualified skill name, formalizes the `.gitignore`
isolation vs. cleansing trade-off, and updates the draft Living Spec blueprint.
Upon acceptance through `devkit spec proposal accept uiux-improve-ooux-impeccable`, hand off to `specs/` for
implementation in `packages/devkit-catalog/src/devkit_catalog/uiux_improve/`.
Retire the proposal bundle upon graduation and Living Spec reconciliation.
