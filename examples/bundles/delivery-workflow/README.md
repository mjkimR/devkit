# delivery-workflow example bundle

A minimal bundle that ships one `kind = "workflow"` asset for
`devkit.workflow`. Synchronizing it installs the definition under
`.devkit/managed/delivery-workflow/workflows/direct-delivery.md`, records it in
the installation receipt, and generates the shared `devkit-workflow` entry
skill for every selected agent. Repositories that do not select this bundle
see neither the definition nor the skill.

```bash
uv run devkit bundle validate examples/bundles/delivery-workflow
uv run devkit workflow validate examples/bundles/delivery-workflow/workflows/direct-delivery.md
```

The definition declares four stages (intent, build-verify, review, integrate)
with two approval gates, `direction` and `integration`, whose policies a
consumer sets in `.devkit/config.toml` under `[workflow.approvals]`.

The review stage names the `reviewer` role with `isolation: preferred`. The
bundle ships that role as a host-neutral contract
(`subagents/reviewer.md`, a `kind = "subagent"` asset): `devkit sync` renders
`.claude/agents/reviewer.md` from its `hosts.claude-code` block and
`.codex/agents/reviewer.toml` from `hosts.codex` and `.agents/agents/reviewer.md`
from `hosts.antigravity`, so `[DELEGATE: role=reviewer]` resolves to a real
subagent on each host.
