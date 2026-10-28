---
id: ADR-document-and-sdd-bundles
title: Separate document assets from SDD assets
summary: "For repositories using documents without SDD, we ship document assets in a docs bundle and retain lifecycle assets in spec, to select guidance independently, accepting two context reads for SDD."
proposal: SPEC-document-bundle-split
status: accepted
created_at: 2026-10-28
---

# [ADR-document-and-sdd-bundles] Separate document assets from SDD assets

## 1. Context & Problem Statement

`ADR-document-package` separates implementations but leaves every distributable document asset in spec. A
consumer that installs only devkit-docs lacks document guidance and rule deployment. Selecting spec introduces
SDD entry obligations. `MS-idea-incubation` needs the document formats independently of that lifecycle.

## 2. Decision Drivers

- Document-only installations carry no implicit SDD entry, approval or history obligations.
- Existing SDD installations retain their lifecycle guidance and default behavior.
- Each asset has one owning wheel and bundle; generic distribution semantics remain unchanged.

## 3. Considered Options

- Keep spec unchanged: no distribution cost, but docs-only consumers lack its corresponding guidance and rules.
- Add document/lifecycle presets within spec: fewer bundle names, but a docs-only install still depends on the
  SDD wheel and its runtime extensions or duplicates document assets across wheels.
- Separate docs and spec bundles: aligns with wheel ownership and enables independent selection; requires context,
  reference, seed and test repairs and a second context read in SDD sessions.

## 4. Decision Outcome

Recommend separate docs and spec bundles. This is a proposed direction pending Host/user acceptance.

1. devkit-docs owns the auto-selected `docs:core`, all shared writing instructions, document rules and templates,
   the document-only constitution/pointer, steering context discovery and opt-in `docs:docs-skeleton`.
2. devkit-spec retains auto-selected `spec:core`, lifecycle templates/rules/workflows/roles/skills/playbooks,
   the SDD pointer and lifecycle obligations. It requires the docs context rather than copying its instructions.
3. Package installation selects both bundles for SDD by default through the existing package dependency and
   auto_select semantics. Explicitly deselecting a bundle changes assets, not installed Python extensions.
4. Shared writing policy describes document structure and current-state authoring. SDD retains accepted-decision
   supersession, completed-artifact preservation and mandatory reconciliation in its own guidance.
5. No migration shim, cross-bundle dependency engine or runtime lifecycle bypass is introduced. The supported SDD
   setup includes docs; the supported clean document-only setup omits the devkit-spec distribution.

## 5. Consequences

- Positive: document-only consumers install rule assets, formats and guidance without SDD lifecycle entry assets.
- Negative: all moved asset citations and tests must track their owning bundle; SDD sessions read two contexts.
- Risk: copied seeded READMEs or neutral-looking instructions can retain SDD directives. Semantic review and
  isolated wheel installation smoke cover this risk. Existing consumer seeded files remain project-owned.
- Follow-up: incubation runtime policy, orchestration and optional verified SDD adoption stay under
  `MS-idea-incubation`; this decision does not satisfy those milestone exits.

## 6. Confirmation

Development adds bundle inventory/reference assertions and an isolated consumer installation smoke without
installed devkit-spec. It verifies default SDD selection, explicit spec deselection, opt-in seeding and preservation
of existing seeded bytes. `devkit sync --check` verifies this repository's projected assets. The feature's
acceptance scenarios AC-01 through AC-06 define the verification boundary; exact test paths are set in its plan.
