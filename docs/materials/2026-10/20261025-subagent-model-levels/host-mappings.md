# Host capability evidence and proposed default mappings

Documentation inspected on 2026-10-25 by a read-only Scout. These are requested deployment settings, not
benchmarked equivalences or guarantees about the runtime's account, provider or organization policy.

| Level | Claude Code model / effort | Codex model / effort | Antigravity model / effort |
| --- | --- | --- | --- |
| `inherit` | omit / omit | omit / omit | omit / unavailable |
| `light` | `haiku` / `low` | `gpt-6-luna` / `low` | `flash` / unavailable |
| `standard` | `sonnet` / `medium` | `gpt-6.1-sol` / `medium` | `pro` / unavailable |
| `deep` | `opus` / `high` | `gpt-6-astra` / `high` | `pro` / unavailable |

This policy increases requested resources through low/medium/high and selects lightweight/general/reasoning
families. It does not assert identical compute or quality between providers. Deep selects Opus as a maintained
family default, not a claim that Opus is the provider's strongest available model. Families and effort values
remain project-overridable. The default path does not select any of these models: it inherits.

## Claude Code

- [Custom subagents: model and effort](https://code.claude.com/docs/en/sub-agents): native `model` accepts family
  aliases including `haiku`, `sonnet`, `opus`, `fable`, full identifiers and `inherit`. Per-invocation model wins
  over frontmatter, followed by the subagent model environment default and parent; forced environment settings
  can override that order. Per-invocation effort wins over frontmatter; `CLAUDE_CODE_EFFORT_LEVEL` wins over both.
- [Model configuration](https://code.claude.com/docs/en/model-config): supported effort values include `low`,
  `medium`, `high`, `xhigh`, `max` for documented 5.5 models. Alias resolution differs across providers; older
  models can lack effort support. Haiku 5.5 requires Claude Code v2.1.293. Invocation effort requires v2.1.292.
- A requested alias plus effort is not proof that the host honored that effort. Document the baseline and provider
  limits rather than changing environment variables or forcing a host upgrade during sync.

## Codex

- [Custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents): custom-file model and
  `model_reasoning_effort` take precedence over resolved spawn/default/parent settings. Before the file is applied,
  each setting resolves through explicit spawn values, global agents defaults and parent values. A model-only
  custom file preserves resolved effort, which can be incompatible with the selected model.
- [Codex models](https://learn.chatgpt.com/docs/models): supported identifiers include `gpt-6-luna`,
  `gpt-6.1-sol`, `gpt-6-astra`, subject to account, client and rollout availability. Bare `luna`, `sol`, `astra`
  aliases are not established by these sources.
- [Luna](https://developers.openai.com/api/docs/models/gpt-6-luna),
  [Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol),
  [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra): the default `low`, `medium`, `high` requests
  above are within the documented effort values. This is syntax/capability evidence, not proof of local entitlement.
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference): reasoning effort is
  model-advertised and can depend on the client. Custom project model strings remain host-owned identifiers.
- Official model guidance favors starting Luna at high and Astra at low for task tuning. This proposal instead
  chooses a predictable ascending resource preset; tune through config overrides when task evidence warrants it.

## Antigravity

- [Custom subagents](https://www.antigravity.google/docs/subagents/): frontmatter `model` values are `inherit`,
  `flash`, `pro`, defaulting to inherit. No per-subagent effort field is documented. Both standard and deep therefore
  use pro without effort; an explicit non-inherit effort override is invalid.
- Subagent conversation history is isolated. This is separate from inheriting model selection. The docs do not
  establish inherited per-subagent effort; do not claim that omitted effort guarantees the parent's effort here.

## Evidence limits

No live native subagent was launched and no provider API or credential was accessed. Account entitlements,
installed versions, organization allowlists and arbitrary gateway/custom model capabilities remain unverified.
Acceptance tests prove configuration resolution and rendered bytes; optional manual native smoke checks report
observed model/effort separately and are not prerequisites for offline sync.
