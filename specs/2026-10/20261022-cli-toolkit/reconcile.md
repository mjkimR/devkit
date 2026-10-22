---
reconcile_id: REC-cli-toolkit
status: resolved
targets:
  - file: docs/capabilities/cli/CAP-CLI-agent-cli-toolkit.md
    resolution: modified
  - file: docs/capabilities/README.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
    resolution: modified
  - file: docs/development/reference/advisory.md
    resolution: modified
  - file: docs/development/reference/core.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
  - file: docs/development/reference/README.md
    resolution: modified
  - file: docs/architecture/ARCH-01-introduction-and-goals.md
    resolution: modified
  - file: docs/architecture/ARCH-03-context.md
    resolution: modified
  - file: docs/architecture/ARCH-05-1-containers.md
    resolution: modified
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
  - file: docs/architecture/ARCH-07-deployment.md
    resolution: modified
  - file: docs/architecture/ARCH-08-1-agent-output.md
    resolution: modified
  - file: docs/architecture/ARCH-05-3-command-plugins.md
    resolution: modified
---

# Reconcile: `SPEC-cli-toolkit`

`CAP-CLI-agent-cli-toolkit` (new area `cli`, registered in the capabilities README) is the contract of the
`devkit-cli` package (AC-01 to AC-08, AC-10, AC-11) and of the `cli-tool` bundle (AC-12 to AC-15): its rules 1 to 15
restate the boundary behavior that `ARCH-08-1-agent-output` already specifies for devkit, now parameterized by the
tool's logger and prefix, and name the test or rule that enforces each.

Architecture:

- `ARCH-01-introduction-and-goals` and `ARCH-03-context`: `devkit-cli` is a published runtime library next to
  `devkit-advisory`; the mission list and the system's In-Scope list name the CLI toolkit and its bundle.
- `ARCH-05-1-containers`: the `devkit-cli` container (section 2.3.1), its edges (dist depends on it, it depends on
  advisory, click tools depend on it at runtime) and the lockstep summary.
- `ARCH-05-2-components`: `devkit_cli` in the component graph and the module table; `ArgumentError` among the
  `devkit.advisory` exports.
- `ARCH-07-deployment`: the release assets now list `devkit_core`, `devkit_cli` and `devkit_mcp` (the first and last
  were already built by `scripts/release.sh` but missing from the list), and the Git and wheel installation sentences
  name `devkit-core` and `devkit-cli`.
- `ARCH-08-1-agent-output`: the contract is unchanged (AC-10, non-goal 4); the introduction and the implementation
  map name `devkit_cli` as the implementation and `devkit_dist.adapters.cli` as devkit's binding of it.

`CAP-DIST-content-packages`: its release-wheel install command and the sentence listing the wheels a `devkit-agt`
installation names now include `devkit-core` (already required, previously missing) and `devkit-cli` (AC-11).

AC-09 (`devkit.advisory.ArgumentError`) is an additive change to the advisory API. `CAP-ADV-agent-advisory-protocol`
specifies the protocol, not the library's classes, so it does not change; the library reference
(`docs/development/reference/advisory.md`) and the `agent-advisory-python` instruction document the class, and
`docs/development/reference/core.md` its devkit-core subclass and the adapter binding. The reference index
(`docs/development/reference/README.md`) lists `devkit_cli`, and `docs/development/reference/distribution.md` names
the `devkit-core` and `devkit-cli` wheels in its install command and wheel sentence.

No other Living Spec document changes:

- `CAP-HARN-command-mount` cites `devkit_dist.adapters.cli` for plugin commands; that module keeps every name it
  cites. `ARCH-05-3-command-plugins` does too; only its sentence on the lockstep versions changed (now naming
  `devkit-core` and `devkit-cli` and pointing to `ARCH-07-deployment`).
- `CAP-GOV-rule-authoring`: the three rules use the plugin-package contract unchanged, one directory per rule.
- No story covers command-line tooling; no ADR is required: no `MUST` of an existing contract changes, and
  `devkit-cli` joins the lockstep release under the existing `ADR-independent-package-namespaces-and-feature-layout`.
- Glossary: no new domain term; "boundary" is used as in `ARCH-08-1-agent-output`.

Repository guides kept in step (not Living Spec): `AGENTS.md`, `README.md` (including the release procedure's six
lockstep packages), `docs/development/ci-cd.md`, the package READMEs, `guides/` (install commands and the `cli-tool`
recommendation) and the `devkit-dev` `project-structure` instruction.
