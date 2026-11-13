---
id: PROP-skip-empty-bundle-context-target
title: Target Living Spec for Skipping Empty Bundle Context Loads
status: draft
proposal: PROP-skip-empty-bundle-context
created_at: 2026-11-13
targets:
  - file: docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md
  - file: docs/capabilities/distribution/CAP-DIST-workspace-ownership.md
  - file: docs/capabilities/distribution/CAP-DIST-agent-projections.md
---

# [Blueprint] PROP-skip-empty-bundle-context: Target Living Spec

## 1. Capability Changes

- `CAP-DIST-context-and-playbooks`: define the loading requirement from a constitution, selected instructions or
  declared context documents. Document the playbook retrieval signal chosen during Planning. Preserve explicit
  empty context inspection and runtime document-provider behavior.
- `CAP-DIST-workspace-ownership`: describe the root guidance rule that requires loading only for bundles with
  context sources, including mixed selections and selections without any such bundle.
- `CAP-DIST-agent-projections`: align skill prerequisite generation with that same source-presence criterion,
  including bundles whose only context source is a declared document directory.

## 2. Architecture and Use Cases

The change stays within the existing distribution feature and adds no package, layer or user workflow. No new
architecture or use case document is proposed. Planning settles playbook metadata compatibility before acceptance.

## 3. Guides and Distribution Assets

Update the devkit bundle's consumption instruction, generated playbook entry skill and relevant devkit-dist README
guidance to honor the loading requirement. Change source assets; sync generates managed and projected copies.

## 4. Before and After

| Case | Before | Proposed behavior |
| --- | --- | --- |
| Bundle without context sources | Root guidance and playbook retrieval require an empty load | Generated requirements permit execution without a context call |
| Constitution or selected instructions | Context required | Context required |
| Only declared context documents | Root guidance requires loading; skill prerequisite is absent | All generated entry paths agree that context is required |
| Explicit context inspection without sources | Successful empty JSON result | Same successful empty JSON result |
