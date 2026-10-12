# [RULE-skill-document-size] Skill document size warning

A skill or playbook Markdown file larger than the effective `max_bytes` receives
a warning with its size, the limit and the restructuring steps. The rule never
rewrites files. Its value is the remediation it delivers at the moment a skill
grows; the full procedure is the `skill-authoring` playbook of the `authoring`
bundle (`uv run devkit playbook search "restructure a large skill"`).

This is a hygiene rule: it runs under `devkit rules check --phase hygiene` only.

## Restructuring steps

1. **Compress**: remove repeated explanation, long background and overlapping
   examples. Keep execution conditions, required constraints and verification
   criteria. Joining lines to shrink a file is not a fix.
2. **Split conditional content**: move recovery procedures, tool-specific
   instructions, detailed schemas of one stage and rare long examples to
   `references/`, and state when each file is read.
3. **Thin router**: `SKILL.md` keeps purpose and trigger, shared constraints,
   task branches and situational reference paths. Telling the agent to read
   every reference at start removes the benefit.
4. **Review supporting files**: apply the same steps to large references. Avoid
   many tiny files and reference chains.

Never hide always-required safety or boundary constraints in a rarely read file.
Size is a signal for review, not a goal.

## Configuration

Size is measured in UTF-8 bytes, which tracks token cost for English and Korean
better than line or character counts. Defaults: `max_bytes = 8192`,
`extensions = [".md"]`, and `paths` selecting project-native skills
(`.agents/skills/**`, `.claude/skills/**`) and bundle sources
(`**/bundle/skills/**`, `**/bundle/playbooks/**`). Files the installation
receipt owns, such as agent projections of bundle skills, are skipped: change
the bundle source instead. Symlinks are skipped, so each original is reported
once.

Record a justified exception as an exact-path override in
`.devkit/config.toml`, with the reason in a comment directly above it:

```toml
[rules.settings.RULE-skill-document-size]
paths = [".agents/skills/**", "tools/agents/**"]

# Read as one procedure; split deferred.
[[rules.settings.RULE-skill-document-size.overrides]]
path = ".agents/skills/release/SKILL.md"
max_bytes = 12288
```

Update or remove the entry when the file moves or shrinks. `max_bytes` must be a
positive integer, `extensions` literal dot-prefixed strings and `paths`
workspace-relative patterns where a standalone `**` matches zero or more
segments.
