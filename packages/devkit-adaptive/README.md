# devkit-adaptive

Opt-in adaptive development guidance, with no runtime dependencies or commands.

```bash
uv add --dev "devkit-adaptive @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-adaptive"
```

## Adaptive development

`uv run devkit add adaptive-dev` explicitly selects the `adaptive-dev` bundle. Install devkit-docs alongside devkit-adaptive for
shared document formats; devkit-spec is not required. `/adaptive-dev` checks the effective development approach through
`uv run devkit config show` before product actions. Selection changes assets, not project policy.

The coordinator adapts clarification, research, implementation and actual-usage verification to the next useful
action, with optional product-clarifier, product-researcher and usage-reviewer assignments and no required team
size or role sequence. A small question can stay inline.

The coordinator keeps mutable current facts, retained note links and useful alternative reopening conditions in
project-owned `.devkit/adaptive-dev.md`; sync never seeds or overwrites it.
No per-change SDD Unit, envelope or immutable experiment history is required. Independent project checks still run.
An explicit adoption request prepares spec assets while keeping adaptive development active, then uses the separately
delivered `sdd-baseline` playbook for readiness and activation.

`/adaptive-import <Git URL or local path> [conditions]` declares `invocation = "user"` and runs only when the user
invokes it; no other asset of the bundle names or suggests it. It reads a third-party repository of subagents or
skills as untrusted data in a temporary clone, executes nothing from it, recommends at most five fitting items and
stops for one selection round. The selection invokes the `agent-asset-conversion` playbook
(`uv run devkit playbook get adaptive-dev/agent-asset-conversion`), which rewrites each selected item, by default as a
role overlay for `swarm-planner`, `swarm-worker` or `swarm-verifier`, without the source's authority, model or
host-specific content, and places it in the project's own in-repository bundle with a provenance line. It never
imports a whole pack, needs no approach check and changes no approach or host setting.
`uv run devkit add adaptive-dev:import` adds the two assets to a project that selects only `adaptive-dev:agents`.
`CAP-DLV-adaptive-development` holds the contract.

