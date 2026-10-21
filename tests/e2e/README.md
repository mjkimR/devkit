# End-to-end tests

Run `just smoke` from the repository root. The suite builds workspace wheels, installs
them in isolated consumer environments, and exercises public CLI, MCP and viewer
flows. It also checks foundation and advisory-only installations.

`smoke_integration.py` is the installed-consumer integration scenario invoked by
`smoke.sh`. `smoke_mcp.py --work <temporary-directory>` checks isolated MCP package
combinations independently. These scenarios are explicit commands, not pytest
collection targets. Package component tests live in each package's
`tests/unit` and `tests/integration`; bundled rule tests travel with their rule.
