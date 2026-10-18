---
id: PLAN-bundle-templates
spec: SPEC-bundle-templates
---

# Technical Plan: Configurable bundle templates

## Constitution and invariant review

No layering changes or bundle code execution. Template rendering occurs during inventory planning before transaction
writes. Native host files remain verbatim. Existing receipt schema records final bytes without a version bump.

## Components and contracts

- bundles/templates.py: variable declarations, exact scalar types, destination mapping and function-local Jinja imports.
- bundles/manifest.py: declarations, template scope and source collision validation; defer template content checks.
- installation/config.py: strict per-bundle variable tables.
- installation/inventory.py and overrides.py: raw override resolution, rendered managed destinations and validation.
- installation/sync.py: pass project variables into planning, including guidance previews and locked sync.
- devkit-catalog: independent opt-in response-style instructions and short guidance pointer.
- Canonical distribution contracts, references, authoring instructions and installation recommendations.

Jinja2 is a runtime dependency, imported only by the rendering function. Use sandboxing, StrictUndefined, no globals,
no loader and no object attributes or calls. UTF-8 text retains final newlines; HTML autoescaping is disabled.

## Verification

Integration tests cover defaults, invalid variables, context, override lifecycle, previews, locked sync, collisions,
invalid rendered headers/fragments and rollback-before-write. Subprocess tests prove ordinary CLI and non-template
inventory avoid Jinja imports. Run lint, Pyright, distribution/catalog tests, layering, governance and smoke.
