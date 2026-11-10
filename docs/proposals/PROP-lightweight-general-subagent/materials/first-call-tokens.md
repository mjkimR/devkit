# First-call input tokens by Claude Code subagent type

Method: read this repository's retained Claude Code subagent transcripts
(`~/.claude/projects/*devkit*/<session>/subagents/agent-*.jsonl` with their `.meta.json`). For each child, take the
first assistant message's `usage` and add `input_tokens`, `cache_read_input_tokens` and
`cache_creation_input_tokens`. This total is everything the child received before its first action: system prompt,
tool schemas, skill listing, project instruction files, the subagent body and the Host's prompt. The prompt size is
the character length of the child's first user message. Statistics cover each type's 15 most recent children.
Measured on 2026-11-10 on the repository owner's machine; Claude Code's own prompts and tool schemas change between
releases, so these are a same-machine snapshot, not a stable constant.

| Type | Children | Claude Code tools | Min | Median | Max | Median prompt chars |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `general-purpose` | 307 | all (`*`), MCP included | 35,986 | 36,136 | 36,589 | 3,006 |
| `fork` | 19 | inherits the parent context | 28,948 | 30,181 | 344,356 | 2,832 |
| `development-worker` | 65 | Read, Grep, Glob, Write, Edit, Bash, Agent | 14,202 | 14,817 | 16,477 | 4,686 |
| `planning-worker` | 77 | Read, Grep, Glob, Write, Edit, Bash, Agent | 12,643 | 14,903 | 16,744 | 5,266 |
| `Explore` | 10 | read-only built-in set | 13,158 | 14,349 | 17,513 | 1,959 |
| `challenger` | 91 | Read, Grep, Glob, Bash | 11,713 | 13,597 | 14,528 | 7,512 |
| `scout` | 49 | Read, Grep, Glob, WebFetch, Bash | 11,970 | 13,039 | 13,991 | 5,018 |
| `code-reviewer` | 91 | Read, Grep, Glob, Bash | 10,593 | 12,201 | 14,402 | 3,967 |
| `reconcile-reviewer` | 60 | Read, Grep, Glob, Bash | 10,450 | 11,249 | 11,887 | 2,782 |

## Findings

- `general-purpose` starts at about 36k tokens with a prompt of about 1k tokens. Its spread is under 2%, so the load
  is fixed, not caused by the Host's prompt.
- `development-worker` and `planning-worker` already use the proposed tool shape apart from WebSearch and WebFetch,
  including `Agent`, and start at about 15k tokens despite their long role contracts and longer prompts. The `Agent`
  tool's agent-type listing therefore costs at most a few thousand tokens.
- Read-only subagents without `Agent` start at 11k to 14k, which bounds the base system prompt, the remaining tool
  schemas and the project instruction files (about 3.5k tokens) from above.
- Expected `role-worker` first call: about 13k to 16k tokens, a reduction of 20k or more (about 55% to 65%) per child.
  This is an estimate from tool-shape neighbors; Development measures the projected `role-worker` itself on the same
  machine against this table's `general-purpose` row.
- `fork` is not a cheaper alternative: it carries the parent conversation and grows with it (344k maximum).

## Not measured

- The cost of `WebSearch` and `WebFetch` alone; `scout` carries `WebFetch` and stays at about 13k.
- Codex and Antigravity: Codex has no tool allowlist in subagent projection (`sandbox_mode` only), so no reduction is
  claimed there.
