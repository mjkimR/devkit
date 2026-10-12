# [RULE-skill-document-size] Skill document size warning

A skill or playbook Markdown file larger than the effective `max_bytes` receives
a warning with its size, the limit and a summary of the restructuring steps. The
rule never rewrites files. It runs under `devkit rules check --phase hygiene`
only.

## Restructuring

Follow Step 2 of the `skill-authoring` playbook of the `authoring` bundle
(`uv run devkit playbook search "restructure a large skill"`): compress, split
conditional content into `references/`, keep `SKILL.md` a thin router, then
review supporting files. Never hide always-required safety or boundary
constraints in a rarely read file, and do not shrink a file by joining lines.
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
