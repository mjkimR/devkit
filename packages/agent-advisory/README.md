# agent-advisory

Python implementation of the **Agent Advisory Protocol** plus a devkit bundle that installs its authoring guide.

## Scope

This package implements the Agent Advisory Protocol and nothing else. It is not a home for general agent-facing features.

- **Current scope**: error advisories, meaning failures that direct the agent's next action through `[ACTION]` modes.
- **Out of scope until the protocol is extended**: non-error advisories such as warnings and notices. Extending the protocol (for example, adding a non-blocking mode or a `[WARN]`/`[NOTICE]` headline) belongs here, because it reuses the same `Advisory`, modes, and renderers. Ship it as new bundle assets and presets beside `error-advisory`.
- **Never here**: anything that is not this protocol. Put it in a separate package.

## Contents

- **Runtime**: `agent_advisory` (standard library only): `AdvisoryError`, `Advisory`, `Actor`, `Retry`, `ActionMode`, `ExitCode`, and renderers for CLI/MCP text, JSON, and RFC 7807.
- **Bundle** `agent-advisory` (`default_preset = "core"`):

| Preset | Assets | For |
| --- | --- | --- |
| `core` | `error-advisory` (language-agnostic protocol and authoring rules) | Any repository |
| `python` | `error-advisory` + `error-advisory-python` (library guide) | Python repositories using this package |

## Python repositories

Use the library at runtime and install the guide with the Python preset:

```bash
uv add agent-advisory
uv add --dev devkit-distribution
uv run devkit add agent-advisory:python
```

## Other repositories

Only the guide is needed. Run the devkit CLI with this package in the same tool environment:

```bash
uvx --from devkit-distribution --with agent-advisory devkit add agent-advisory
```

The wheel still carries the small runtime module. It is inert unless imported.

## Specification

The protocol originates in specrig's `error-advisory` instruction and its Go `advisory` package. This package follows that specification, including the `[ACTION]` texts, the mode derivation order, `INPUT_ERROR`, and the strict use of `HALT`. One deliberate difference: `to_problem_details()` takes the HTTP `status` from the caller instead of using the process exit code.
