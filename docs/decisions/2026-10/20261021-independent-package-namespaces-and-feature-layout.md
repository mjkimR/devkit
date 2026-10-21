---
id: ADR-independent-package-namespaces-and-feature-layout
title: Independent package namespaces and feature layout
summary: "Application wheels own independent Python namespaces and feature layers; devkit_core separates shared contracts from primitives while devkit.advisory preserves its public API."
status: accepted
created_at: 2026-10-21
supersedes: [ADR-dist-module-split]
---

# [ADR-independent-package-namespaces-and-feature-layout] Independent package namespaces and feature layout

## 1. Context & Problem Statement

The shared `devkit` namespace obscures which wheel owns an import and makes package-specific dependency
checks depend on a list of module names. Application packages also group similar operations differently.
The shared foundation is now owned by `devkit-core`, so retaining a second package-level core obscures
whether a helper is generic infrastructure or feature behavior.

`devkit.advisory` has runtime consumers outside this repository and remains a compatibility contract.
CLI names, bundle IDs and entry-point group names identify integration contracts independently of Python imports.

## 2. Decision Drivers

- Make wheel ownership visible from application import paths.
- Give packages a common feature structure without requiring unused layers.
- Keep use case coordination separate from CLI/MCP transport and external IO.
- Check layer direction and package isolation without adding CRUD or transaction abstractions.
- Preserve the externally consumed advisory API and existing command and plugin discovery contracts.

## 3. Considered Options

- Keep the shared `devkit` namespace and normalize only its internal folders. Ownership still depends on a module allowlist.
- Give every wheel a regular package and organize applications by feature. Selected for explicit ownership and local boundaries.
- Copy a complete application framework into each package, including mandatory services, repositories and units of work. This would require abstractions without a corresponding operation or resource lifecycle.

## 4. Decision Outcome & Rationale

`devkit-dist` owns `devkit_dist`; `devkit-agt` owns `devkit_agt`. Application extensions use their own
regular packages. `devkit-advisory` retains the public PEP 420 `devkit.advisory` API and does not ship
`devkit/__init__.py`. No installed path belongs to two wheels.

Applications organize behavior under `features/<feature>/`. A feature adds `cli`, `mcp`, `usecases`,
`services`, `repositories` and `models` only when the corresponding responsibility exists. Adapters call
use cases; use cases coordinate services and repositories; lower layers never import their callers.
Feature dependencies follow an explicit acyclic graph. Package-level `base` contains shared contracts;
optional `utils` contains technical helpers. Small layers may be single modules. Shared transport
adapters require explicit package ownership; dist declares its common CLI boundary under `adapters`.
Application packages do not introduce package-level `core`.

`devkit_core` is the foundation exception: `base` owns errors and SDK-free MCP contracts; `core` owns
generic implementations and may depend on base. Base never imports core or application code. Project
configuration, receipts and execution binding behavior remain in the distribution's project feature.

Bundle-only packages may keep only bundle assets. Repository-specific structure and layering rules
belong to the `devkit-dev` bundle under `tools/devkit-dev`, initially without application layers.

The executable remains `devkit`; bundle IDs and entry-point groups retain their names. Entry-point
targets move to the owning package. `devkit-dist` remains independent of the harness and MCP SDK;
optional providers cross that boundary through existing entry-point groups. No compatibility wrappers
are introduced for application module paths that have no external consumers.

## 5. Consequences

Imports, dynamic module paths, wheel resource targets, tests and current documentation move together.
Package isolation remains covered by independent-wheel tests, while structure rules check folder and
layer boundaries. Feature graph tests cover package-specific dependencies. This supersedes the shared
namespace and whole-module layout decision of `ADR-dist-module-split`; distribution responsibility and
command composition remain governed by their existing contracts.
