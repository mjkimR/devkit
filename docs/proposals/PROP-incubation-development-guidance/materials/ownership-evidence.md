# Incubation guidance ownership evidence

Scout at `b07a6a9e` inspected the existing bundle mechanism without edits. Pre/post snapshot was
`0679d653a086538c09230ce703b4805ad06fdfb0`; HEAD was unchanged.

| Option | Evidence | Cost and risk |
| --- | --- | --- |
| catalog opt-in bundle | `packages/devkit-catalog/pyproject.toml:2-13` registers independent bundles; catalog has no runtime dependencies; response-style manifest is an opt-in example. | No new wheel. Consumers also install document/runtime dependencies; selection must remain explicit. |
| docs bundle | `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/bundle.toml:1-6` auto-selects shared document assets. | Incubation-specific entry would pollute generic document installation. |
| dedicated wheel | `docs/architecture/ARCH-07-deployment.md:18-35,39-63` and `scripts/release.sh:70-74` enumerate release/install wiring. | Independent ownership but another release artifact without a distinct runtime requirement. |
| spec bundle | `ARCH-05-2-components` separates document foundation from SDD extension. | Installing the SDD wheel undermines the clean incubation path. |

`packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/discovery.py:13-17,64-104`
discovers any installed `devkit.bundles` entry point. No generic distribution change is required.

Scout did not execute consumer installs. Built-wheel isolation and semantic guidance evaluation remain Development
checks. `.devkit/incubation.md` is a proposed project-owned Markdown artifact, not a currently implemented service.
