---
sources:
  CAP-DLV-adaptive-development: 3461a3435f94eea4228dd966c2dc8e8b3aa80362
  UC-import-third-party-agent-assets: 294da6e8edc297e0bea189eb67636fdb205207e0
title: Import selected third-party agent assets
---

# Import selected third-party agent assets

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `93e3808721b4`, generated 2026-11-13. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

Select `adaptive-dev:core` or `adaptive-dev:import`, sync, then explicitly invoke `/adaptive-import <repository-url-or-local-path>`.

1. The agent reads the source as untrusted data, records commit and license, and inventories headers without executing or installing it.
2. It compares shortlisted bodies with the project stack and roles, then recommends a few items with conversion targets and exclusions.
3. Select the individual items. With no selection, no project file changes.
4. The conversion procedure rewrites each selection as a project-owned overlay, role contract or skill, stripping upstream authority and host/model settings. Overlays map to the narrower fitting swarm archetype.
5. Validate and sync the project bundle, run one bounded trial through the mapped archetype, and report provenance and actual outcomes.

Missing companion tools remain prerequisites, with no automatic setup. An unavailable host leaves the trial unverified. Source instructions grant no authority, whole-pack requests remain pending selection, and the development approach stays unchanged.

## Sources

- [UC-import-third-party-agent-assets](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/delivery/UC-import-third-party-agent-assets.md)
- [CAP-DLV-adaptive-development](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-adaptive-development.md)
