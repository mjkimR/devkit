# devkit-cli

The agent-first command-line boundary of `devkit`, for any click tool: `devkit_cli`. A command wrapped by it
reports the way `devkit` does (`ARCH-08-1-agent-output`): its result on stdout as `[KIND: ...]` lines or one JSON
object under `--format json`, errors, warnings and notices as Agent Advisory Protocol blocks on stderr, exit codes
`0` success, `1` negative result, `2` could not run, and `-q`/`-v`/`--strict` on every command. Requires Python 3.12
or later, `click` and `devkit-advisory`; it imports nothing else, so it adds only click's own import time.

`devkit-dist` builds the `devkit` command line on it, and tools in other repositories depend on it at runtime, so it
is a semver contract released in lockstep with the other devkit wheels (`ARCH-07-deployment`). The behavior is
specified in `CAP-CLI-agent-cli-toolkit`; the opt-in `cli-tool` bundle of `devkit-catalog` is the structure guide
and rules for a tool built on it.

## Install

No package index hosts the wheel; install it by URL from a GitHub Release (with the `devkit-advisory` wheel of the
same release), or from Git with `subdirectory = "packages/devkit-cli"`:

```bash
base=https://github.com/mjkimR/devkit/releases/download/v<version>
uv add "devkit-cli @ $base/devkit_cli-<version>-py3-none-any.whl" \
  "devkit-advisory @ $base/devkit_advisory-<version>-py3-none-any.whl"
```

## Use

```python
import click
from devkit.advisory import AdvisoryError
from devkit_cli import FORMAT_OPTION, Boundary, LazyGroup, echo_json, echo_notices, exit_on_warnings

boundary = Boundary("mytool")  # logger "mytool"; MYTOOL_QUIET, MYTOOL_VERBOSE, MYTOOL_STRICT


@click.group(cls=LazyGroup, lazy_commands={"report": "mytool.features.report.cli:report"})
def cli() -> None:
    """mytool: ..."""


@cli.command()
@FORMAT_OPTION
@boundary
def scan(output_format: str) -> None:
    result = ScanUseCase().execute()  # returns data and its notices; raises AdvisoryError on failure
    if output_format == "json":
        echo_json({"files": result.files, "notices": [n.to_dict() for n in result.notices]})
    else:
        click.echo(f"[SCAN: files={len(result.files)}]")
    echo_notices(result.notices)
    exit_on_warnings(result.notices)
```

| Name | Purpose |
| --- | --- |
| `Boundary(name, *, env_prefix=None, log=None)` | The decorator (`@boundary`, `@boundary(json_only=True)`): output options, error rendering, `[INFO]` logs under `-v`, UTF-8 output, exit `2` on a closed reader |
| `FORMAT_OPTION`, `is_json` | `--format text\|json` |
| `echo_json`, `render_json`, `echo_notices`, `exit_on_warnings` | One compact JSON object (and its text, for size budgets); returned warnings and notices after the result; `--strict` |
| `exit_on_problems`, `highest_exit_code`, `report_exit_code` | Exit codes of commands that collect problems |
| `OutputSettings`, `output_settings`, `Reported` | The running command's options; an error whose JSON result is already printed |
| `LazyGroup` | Subcommands imported only when they run |
| `devkit_cli.testing.invoke` | Tests: run a command and read `exit_code`, `stdout`, `stderr`, `json()` and `codes()` |

Semantic argument checks raise `devkit.advisory.ArgumentError` (`ARGUMENT_INVALID`) through the boundary; click
parses syntax only.
