# devkit-advisory

The Python library of the [Agent Advisory Protocol](../../docs/advisory/protocol.md): `devkit.advisory`, agent-directed
errors, warnings and notices with stable codes and deterministic `[ACTION]` directives. Requires Python 3.12 or
later and nothing else: standard library only, no entry points, no CLI.

It is the one part of devkit that other repositories import at runtime, so it ships on its own: a service or
library depends on `devkit-advisory`, and its development tooling on `devkit-agt`, which depends on the same version
of this package. `devkit` is a namespace package shared by both distributions, so the import is
`from devkit.advisory import AdvisoryError` either way.

## Install

No package index hosts the wheel; install it by URL from a GitHub Release (or a built wheel by path), or from Git
with `subdirectory = "packages/devkit-advisory"`:

```bash
uv add "devkit-advisory @ https://github.com/mjkimR/devkit/releases/download/v0.1.0/devkit_advisory-0.1.0-py3-none-any.whl"
```

The API, its compatibility promise and the guide bundle that `devkit` deploys for it are documented in
[docs/advisory](../../docs/advisory/reference.md).
