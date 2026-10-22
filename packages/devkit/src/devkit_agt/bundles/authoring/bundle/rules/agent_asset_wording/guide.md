# [RULE-agent-asset-wording] Agent Asset Wording

## 1. Overview

An agent acts on every sentence of a skill, playbook, instruction or role contract. A hedge leaves the directive's
condition unstated, emphatic capitals make models over-apply a directive, and a time-relative word stops being true
after the next release. The rule warns on each occurrence so the `agent-asset-writing` criteria hold without a
line-by-line review.

- **Phase and severity**: `hygiene`, `warning`; runs under `devkit rules check --phase hygiene` only. Shipped by the
  opt-in `authoring` bundle (preset `skill-authoring`).
- **What is checked**: files ending in one of `suffixes` (default `.md`, `.md.jinja`) under `paths`: project skills
  (`.agents/skills/**`, `.claude/skills/**`) and bundle sources (`**/bundle/skills/**`, `**/bundle/playbooks/**`,
  `**/bundle/instructions/**`, `**/bundle/subagents/**`). Files the installation receipt owns (agent projections) and
  symbolic links are skipped: fix the bundle source instead.
- **Not checked**: fenced code blocks, inline code (also wrapped within a paragraph), text in straight or curly
  double quotes on one line, HTML comments and, in `.jinja` files only, Jinja tags and comments. These mention a word
  rather than use it. A prohibition without its alternative stays a review item.

## 2. Cause of Violation

One violation per occurrence, at its line:

| Message | Default words | Matching |
| --- | --- | --- |
| `Hedge "<word>"` | likely, might, probably, perhaps, maybe, possibly, consider | any case, whole word |
| `Emphatic capitals "<word>"` | CRITICAL, IMPORTANT, ALWAYS, NEVER, ONLY, NOTE, WARNING, DO NOT | exact case, whole word |
| `Time-relative word "<word>"` | recently, currently, nowadays, as of now, at the moment, for now | any case, whole word |

A word joined to another by `-` or `_` is not matched (`READ-ONLY`, `INTEGRATION_NOT_READY`). RFC 2119 keywords
(`MUST`, `SHOULD`, `MAY`) are not in the default list.

## 3. Remediation

- Hedge: state the condition under which the directive applies ("If the branch exists, ...").
- Emphatic capitals: give the rule its force through its condition and reason, in ordinary case.
- Time-relative word: name the version, date or ID.
- A word the text mentions rather than uses (an example of what not to write): put it in backticks, or in double
  quotes on one line; quotes split across a line break are not recognized.

Read the `agent-asset-writing` instruction for the full writing criteria. The rule never rewrites files.

## 4. Configuration

| Setting | Type | Default | Meaning |
| --- | --- | --- | --- |
| `hedges` | list of words or phrases | above | Hedges; an empty list turns the category off. |
| `emphatic` | list of words or phrases | above | Emphatic capitals, matched in exact case. |
| `time_relative` | list of words or phrases | above | Time-relative words. |
| `suffixes` | list of literal suffixes | `[".md", ".md.jinja"]` | Files checked. |
| `paths` | list of patterns | the six locations above | Where agent assets live. |

```toml
[rules.settings.RULE-agent-asset-wording]
paths = [".agents/skills/**", "docs/runbooks/**"]
time_relative = ["recently", "currently", "nowadays"]

# A quoted protocol uses its own capitals.
[[rules.settings.RULE-agent-asset-wording.overrides]]
path = ".agents/skills/release/references/protocol.md"
emphatic = []
```

Patterns are workspace-relative; a standalone `**` matches zero or more path segments.

## 5. Exceptions

Rewrite the sentence or quote the word. For a file that legitimately uses a listed word (a quoted external text),
record an exact-path override with the reason in a comment directly above it.
