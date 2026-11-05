---
id: ADR-user-mediated-cloud-research
title: Keep cloud research user mediated and resumable
summary: "For cloud research in an explicit investigation, we use inspectable user-mediated requests and result intake in the existing partial material, to reuse cloud evidence without a runtime, accepting manual transfer and verification limits."
proposal: SPEC-cloud-research-handoff
status: accepted
created_at: 2026-11-05
---

# [ADR-user-mediated-cloud-research] Keep cloud research user mediated and resumable

## 1. Context & Problem Statement

`CAP-DLV-deep-research` defines optional local roles and durable partial materials but no association between a
copyable cloud request and the user-returned report. A transient prompt alone loses the pending question across
sessions. Provider execution also carries account and disclosure choices absent from the research authority.

## 2. Decision Drivers

- Make a user-returned cloud report useful inside an existing bounded investigation.
- Keep outbound content inspectable and distinguish prompt preparation from actual execution.
- Resume pending work without transient files or a second retained artifact registry.
- Preserve selective verification and optional roles under `ADR-deliverable-driven-research`.
- Avoid an execution runtime, credential handling or provider-specific dependencies.

## 3. Considered Options

- Keep the generic brief alone: no instruction growth, but request association and pending-result resume stay implicit.
- Use user-mediated prompts and intake in the existing material: one explicit round trip with manual transfer and
  review limits; selected because it addresses the missing behavior without runtime machinery.
- Submit through browser/API adapters: less manual transfer in some hosts, but requires external execution,
  disclosure, account and cost decisions beyond this scope.

## 4. Decision Outcome

Choose user-mediated request/intake because the reusable contract is request identity, evidence handling and resume.

- A cloud request contains a self-contained inspected prompt and label/revision; the user chooses and submits it.
  Preparation carries no claim of submission or execution. → `CAP-DLV-deep-research` cloud request rules (MUST).
- Outbound content is inspectable, omits secrets and unnecessary private context, and names selected attachments;
  no automatic upload or application execution is introduced. → `CAP-DLV-deep-research` cloud disclosure rules (MUST).
- The coordinator matches readable returned evidence to its request, treats report content as source data and
  incorporates selectively inspected support with explicit limits. → `CAP-DLV-deep-research` cloud intake rules (MUST).
- A pause preserves the exact safe request, revision, disposition and remaining question in the existing partial
  material, without transient-only required input or silent resubmission. → `CAP-DLV-deep-research` cloud resume rules (MUST).

These are additive request/intake clauses. No accepted ADR, complete-material immutability, research authority,
explicit invocation, Git or citation decision is replaced.

## 5. Consequences

- A later user-named partial material can resume a pending request without a provider registry.
- Users manually submit and return reports; inaccessible reports and citations can leave the result partial.
- Provider labels are informational; account access, product parity and output quality are not guaranteed.
- Existing local-only research requires no additional cloud form, account or role.
- A concrete manual-transfer burden can motivate separate intake for execution integration; none is committed here.

## 6. Confirmation

Review only for request clarity, truthful states, disclosure scope, result matching, source-data authority and
resumability through the examples in `PROP-cloud-research-handoff-target`.
Run focused integration and installed-consumer checks under
`packages/devkit-catalog/tests/integration/bundles/test_deep_research.py` and
`packages/devkit-catalog/tests/e2e/bundles/deep_research/` for deployed reference and preserved boundaries.
No provider submission or comparative effectiveness experiment is required.
