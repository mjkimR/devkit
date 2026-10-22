---
id: SPEC-response-style-skill
title: Templated response-style skill deployment
summary: "Render skill Markdown templates before validation and native projection, keeping configured response language inside the skill."
status: completed
created: 2026-10-19
related_capabilities: [CAP-DIST-manifest-spec, CAP-DIST-agent-projections, CAP-DIST-sync-and-transactions]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-response-style-skill] Templated response-style skill deployment

## Problem and scope

Skill sources currently reject templates, forcing response-style language configuration into root guidance.
Support Markdown templates inside skill directories, including SKILL.md.jinja, so configured communication
instructions live in the skill and root guidance only requests that skill. Existing plain skills remain supported.

## Non-goals

- **Scope Excluded**: New variable types, native YAML templates, templates for other asset kinds, schema versions,
  communication-policy changes, and integration of the activity branch.

## Acceptance Criteria

### [AC-01] Render skills before deployment
- **Given** a skill directory with exactly one entry, SKILL.md or SKILL.md.jinja, and optional Markdown templates.
- **When** synchronization resolves declared bundle variables.
- **Then** managed files and all native projections contain rendered Markdown without .jinja suffixes, preserve
  supporting executable files, and retain context prerequisites and manifest-owned user invocation settings.

### [AC-02] Validate before mutation
- **Given** duplicate entries, colliding rendered destinations, malformed rendered frontmatter, forbidden native
  invocation keys, or a rendering error in a skill or its override.
- **When** a bundle is loaded or synchronization is planned, according to whether the error requires rendering.
- **Then** BUNDLE_INVALID is raised before deployment writes, and an existing installation is preserved.

### [AC-03] Preserve overrides and synchronization semantics
- **Given** a deployed templated skill with a project override or a changed variable.
- **When** synchronization, locked restoration, or override removal runs.
- **Then** raw template paths remain the override source and digest input, consumers read rendered managed paths,
  unchanged runs converge, and locked synchronization refuses changed committed state.

### [AC-04] Keep response language in the skill
- **Given** response-style with language auto or ko.
- **When** the bundle is synchronized.
- **Then** its rendered skill contains the corresponding existing language instruction, while AGENTS.md contains
  only the response-style skill reminder and no bundle-specific language instruction.

## Assumptions

- Continue the existing activity branch and checkout while raising session work to spec depth.
- Use the existing scalar template sandbox and optional skill frontmatter contract; no new renderer is introduced.
