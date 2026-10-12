---
name: git-commits
description: Read before drafting or creating a commit. Defines commit message types, optional scope, imperative subjects, body and footer formatting, and clean message output.
---

# Git commit conventions

Apply these conventions to commit messages after reading the changes included in the commit. Describe those changes accurately; do not claim behavior or verification that the staged changes and check results do not support.

## Message structure

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Use one subject line. Omit unused body and footer sections, including their placeholder text. Separate the subject from the body with a blank line, and separate footers from the preceding section with a blank line.

## Type and scope

Allowed types: `feat` (a feature or capability), `fix` (a defect), `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`, `revert` (undo an earlier change). Where the boundary is not obvious:

- `style`: formatting or whitespace only, without changing behavior; visual product changes use the type that describes their intent.
- `refactor`: restructure code without adding a feature or fixing a defect.
- `chore`: maintenance that does not fit a more specific type.
- `ci`: continuous integration workflows or configuration; `build`: build tooling, packaging or dependencies.

Choose the type that describes the primary intent of the commit. Supporting tests or documentation can share the implementation commit. Split unrelated changes into separate commits when practical.

Scope is optional. When useful, use a short component or area name in parentheses, such as `fix(parser): handle empty input`. Follow established repository scope names rather than inventing a scope for every commit.

## Subject

- Use the imperative mood, such as `add instruction discovery`, rather than `added instruction discovery` or `adds instruction discovery`.
- State the concrete change concisely; avoid vague subjects such as `update stuff` or `fix issues`.
- Use a lowercase type, followed by the optional scope, a colon and one space before the description.
- Do not end the subject with a period.
- Follow the repository's chosen message language; do not introduce a language requirement solely from these examples.

## Body

Use a body when the subject alone does not explain the change or its motivation. Explain what changed and why it was needed, focusing on behavior and intent rather than step-by-step implementation details.

Use `- ` for body bullet points. Keep each sentence on one physical line and let the editor wrap it visually: never break a line in the middle of a sentence or hard-wrap to a fixed column width. Newlines belong only between sections, paragraphs, bullets and footer entries.

## Breaking changes and footers

For a breaking change, append `!` immediately before the subject's colon, for example `feat(api)!: remove legacy response fields`, or add a `BREAKING CHANGE: <description>` footer. Use the footer when affected consumers need an explanation of the incompatibility or migration. It may accompany `!`.

Keep footer entries on separate lines. Include only applicable metadata required by the repository and supported by the actual change; do not invent sign-offs or approvals.

## Output format

When asked to produce a commit message, return only the message text without introductory prose, Markdown headings or code fences.

Do not include citations, references, links or source annotations such as `[cite: 1]`, `[1]` or `(source)` in the subject, body or footers. Do not append a references or sources section.

## Example

```text
feat(cli): add project instruction discovery

- List instruction names, descriptions and paths so agents can discover project guidance without loading every body.
- Preserve local instructions during initialization updates so project policy survives harness upgrades.
```
