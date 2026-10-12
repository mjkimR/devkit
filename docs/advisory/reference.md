# devkit.advisory

Python implementation of the **Agent Advisory Protocol** plus the built-in `advisory` bundle that installs its authoring guide.

## Scope

This module implements the Agent Advisory Protocol and nothing else. It is not a home for general agent-facing features.

- **Current scope**: error advisories, meaning failures that direct the agent's next action through `[ACTION]` modes.
- **Out of scope until the protocol is extended**: non-error advisories such as warnings and notices. Extending the protocol (for example, adding a non-blocking mode or a `[WARN]`/`[NOTICE]` headline) belongs here, because it reuses the same `Advisory`, modes, and renderers. Ship it as new bundle assets and presets beside `error-advisory`.
- **Never here**: anything that is not this protocol. Put it in a separate module.

## Contents

- **Runtime**: `devkit.advisory` (standard library only): `AdvisoryError`, `Advisory`, `Actor`, `Retry`, `ActionMode`, `ExitCode`, and renderers for CLI/MCP text, JSON, and RFC 7807.
- **Bundle** `advisory` (`default_preset = "core"`), built into `devkit` and therefore selected by default:

| Preset | Assets | For |
| --- | --- | --- |
| `core` | `error-advisory` (language-agnostic protocol and authoring rules) | Any repository |
| `python` | `error-advisory` + `error-advisory-python` (library guide) | Python repositories using `devkit.advisory` |

## Python repositories

Use the library at runtime and select the Python preset of the guide:

```bash
uv add devkit
uv run devkit add advisory:python
```

## Other repositories

Only the guide is needed. `devkit sync` deploys the `core` preset by default:

```bash
uvx --from devkit devkit sync
```

Opt out with `[presets] advisory = false` in `.devkit/config.toml` (or `devkit remove advisory`). The runtime module is inert unless imported.

## Specification

The `error-advisory` instruction in the `advisory` bundle is the canonical specification of the protocol, and this module implements it: the `[ACTION]` texts (a test keeps the guide and `ACTION_TEXT` identical), the mode derivation order, `INPUT_ERROR`, the strict use of `HALT`, and continuation lines for multi-line values. `to_problem_details()` takes the HTTP `status` from the caller; the library never maps codes or exit codes to statuses.

## Python API notes

- Every `AdvisoryError` field can be a class-level default on a subclass (`code`, `actor`, `retry`, `guardrail`, `input_error`, `retry_after`, `fix`, `what_to_report`, `target_files`, `exit_code`); a keyword argument other than `None` overrides it per raise, and the factories (`blocked`, `interaction`, `auto_fix`, `invalid_input`) keep the subclass's defaults for the fields they do not set.
- Positional details are converted to `str`, so `to_dict()` and `to_problem_details()` are always JSON-serializable.
