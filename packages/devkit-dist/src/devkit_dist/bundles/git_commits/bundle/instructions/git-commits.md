---
name: git-commits
description: Read before drafting or creating a commit message.
---

# Git commit conventions

Read the commit's changes before drafting (for staged work, `git diff --staged`). Claim only behavior and verification that those changes and the check results support.

## Message structure

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Write one subject line. Omit unused body and footer sections, including their placeholder text. Separate the subject, the body and the footers with one blank line each.

## Type and scope

Allowed types: `feat` (a feature or capability), `fix` (a defect), `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`, `revert` (undo an earlier change).

- `style` is formatting or whitespace only; a visual product change takes the type of its intent.
- `ci` covers continuous integration; `build` covers build tooling, packaging or dependencies.
- Choose the type of the commit's primary intent; supporting tests or documentation share the implementation commit.
- If the changes serve unrelated intents, split them into separate commits.

Scope is optional: a short component or area name in parentheses, such as `fix(parser): handle empty input`, from the repository's established scope names.

## Subject

- Use the imperative mood: `add instruction discovery`, not `added instruction discovery` or `adds instruction discovery`.
- Name the concrete change, not a vague subject such as `update stuff` or `fix issues`.
- Write the type in lowercase and end the subject without a period.
- Write in the repository's established message language; the English examples here set no language requirement.

## Body

Add a body when the subject alone does not explain the change or its motivation: what changed and why, in terms of behavior and intent, not implementation steps.

- Use `- ` for bullet points.
- Keep each sentence on one line, without hard-wrapping to a fixed column width; put newlines only between sections, paragraphs, bullets and footer entries.

## Breaking changes and footers

For a breaking change, append `!` immediately before the subject's colon, for example `feat(api)!: remove legacy response fields`, or add a `BREAKING CHANGE: <description>` footer. When affected consumers need an explanation of the incompatibility or migration, use the footer; it may accompany `!`.

Keep footer entries on separate lines. Include only metadata the repository requires and the change supports; do not invent sign-offs or approvals.

## Output format

When asked to produce a commit message, return only the message text, without introductory prose, Markdown headings or code fences.

Leave out citations, references, links and source annotations such as `[cite: 1]`, `[1]` or `(source)`, and append no references or sources section.

## Example

```text
feat(cli): add project instruction discovery

- List instruction names, descriptions and paths so agents can discover project guidance without loading every body.
- Preserve local instructions during initialization updates so project policy survives harness upgrades.
```

## Completion

- The subject matches `<type>[(scope)][!]: <description>` with an allowed type, in the imperative mood, without a trailing period.
- Every claim in the message is backed by the commit's diff or a check result.
