---
name: project-structure
description: Read before adding or moving repository Python modules or changing package dependencies.
---

# Package and Layer Boundaries

The root `AGENTS.md` defines package ownership, import limits and the use case contract. `RULE-architecture` and
`RULE-usecase-boundaries` enforce them; `devkit rules explain <RULE-id>` gives each fix. This instruction adds:

- Layer directions: `models` and `errors` are contracts; `repositories` use contracts; `services` use contracts and
  repositories; `usecases` coordinate services and repositories; transports (`cli`, `mcp`, `http`) call usecases
  and contracts.
- A package `base` imports no features, utils, adapters or core implementations; `utils` imports no features.
- A declared root `adapters/` holds transport boundaries shared by features; lower layers never import it.
- Declare source roots, features, resource areas, package and feature dependencies and adapter exceptions in
  `.devkit/architecture.toml`.

Done when `uv run devkit rules check` reports no `RULE-architecture` or `RULE-usecase-boundaries` violation for the
changed modules.
