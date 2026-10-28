---
id: ADR-own-development-approach-policy-outside-sdd
title: Own development approach policy outside SDD
summary: "For projects that build without SDD, we own an explicit development approach in devkit-dist and apply it across guidance and runtime consumers, to preserve independent checks, accepting an additional shared configuration key."
proposal: SPEC-incubation-lifecycle-policy
status: accepted
created_at: 2026-10-28
---

# [ADR-own-development-approach-policy-outside-sdd] Own development approach policy outside SDD

## 1. Context & Problem Statement

Independent document assets do not deactivate installed SDD runtime extensions. An application-specific reader
cannot be the authority for a development approach that must remain inspectable without that application.
Existing SDD consumers must retain their defaults, while incubation omits per-change lifecycle obligations.

## 2. Decision Drivers

- Shared project intent stays available without devkit-spec and does not depend on managed-file freshness.
- Independent document/project checks and generic integration safeguards remain active.
- A task branch cannot weaken retained-base readiness; SDD history is not reopened automatically.
- Successor incubation guidance can plan against a small stable interface without fixing its product flow now.

## 3. Considered Options

- Keep behavior and rely on removing assets: cannot coordinate installed runtime extensions and misrepresents omitted checks.
- Infer from installed packages or selected assets: fewer keys, but installation and synchronization state become policy authority.
- Put the setting in `[tool.spec]`: cheapest local change, but a doc-only consumer cannot inspect its policy without SDD.
- Own explicit `[development] approach` in devkit-dist: one common contract and snapshot authority, with additional consumer wiring.

## 4. Decision Outcome

Use the devkit-dist option. The shared values are `sdd` and `incubation`,
with `sdd` when absent. `devkit config show` reports the effective approach and source. No local or environment
override is supported. SDD remains default; incubation is an explicit project choice.

SDD-specific consumers apply lifecycle knowledge, while generic rules reporting exposes omissions and devkit-agt
provides independent project readiness. Explicitly bound historical SDD artifacts retain their checks. The retained
committed target governs integration readiness; a source-only policy change cannot select a weaker path.
Project/session readiness first detects touched prior/proposed workflow-owned Units regardless of the caller's
label, refusing unless the matching lifecycle validator runs. Missing optional SDD tooling cannot weaken retained
history checks; untouched history does not require that tooling.

No dependency resolver, mandatory iteration Unit, new application package or broad structural refactor is introduced.
`SPEC-incubation-lifecycle-policy` defines the applicability and verification boundary.

## 5. Consequences

- Positive: common inspection, runtime behavior and conditional guidance can agree independently of asset selection.
- Cost: devkit-dist configuration, generic applicability reporting, project readiness and SDD consumers must be verified together.
- Risk: a global skip or live-tree read can bypass existing history or snapshot authority; retained-binding and policy-change tests are required.
- Follow-up: entry/support/context and verified adoption are distinct proposals; their Planning can begin using accepted policy interfaces.

## 6. Confirmation

Development tests default/explicit/invalid config, local override refusal, doc-only and installed-spec consumers,
rule omission versus execution, direct/composed command refusal, retained-history changes/deletions, session
integration claims and source/target/result policy changes. Independent code review and reconcile verification
compare every consumer against the proposal's table. Planning source evidence is in `docs/materials/2026-10/20261028-incubation-lifecycle-policy/consumer-inventory.md`.
