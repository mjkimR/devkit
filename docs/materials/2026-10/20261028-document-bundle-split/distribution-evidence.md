# Distribution evidence for document-only assets

Baseline: `26a3c494` plus the proposal's Planning records. This is a source inspection, not an installation smoke.

| Evidence | Observation | Design consequence |
| --- | --- | --- |
| `packages/devkit-docs/pyproject.toml` | Has docs command/config entrypoints and no bundle entrypoint; depends on agt, not spec. | Add a bundle to the existing owner wheel; no extra wheel is needed. |
| `packages/devkit-spec/pyproject.toml` | Depends on devkit-docs and registers the auto-selected spec bundle. | Two auto-selected bundles preserve default SDD installation. |
| `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/bundle.toml` | Owns all eight authoring instructions, nine document rules and five lifecycle rules, templates and opt-in docs-skeleton; declares steering context. | Move document assets once, retain lifecycle assets in spec. |
| `packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/manifest.py` | Manifest declares auto_select, default_preset, assets and presets; no cross-bundle dependency field. | Do not invent cross-bundle preset references or expand generic distribution. |
| `packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/config.py` | default_selection adds installed auto-selected bundles unless explicitly opted out. | docs is automatically selected alongside spec, or alone with the docs wheel. |
| `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/commands.py` | RemoveSelection records auto-selected bundles as opted out. | remove spec provides explicit asset-only deselection; it does not uninstall runtime extensions. |
| `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/seed/docs/README.md` | Explicitly requires /spec and spec-sync; several per-kind READMEs cite managed/spec templates. | Moving files unchanged would leak SDD into the document-only skeleton. |
| `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/instructions/living-spec-writing.md` | Requires supersession ADRs and completed spec preservation. | Preserve these in SDD guidance and remove them from shared authoring policy. |

No timing or citation-count improvement is claimed. Development can reproduce both baseline ownership and the
post-change installation from its own checkout without checking out a different revision. Consumer smoke must
verify that devkit-spec is absent, rather than merely hiding its selected bundle in the monorepo environment.

Alternatives: one bundle with presets keeps the document distribution inside the spec wheel; keeping unchanged
assets provides commands without document guidance; two bundles align wheel ownership with independent selection.
The two-bundle option adds a second context read for SDD and requires citation/test fixture repairs.
