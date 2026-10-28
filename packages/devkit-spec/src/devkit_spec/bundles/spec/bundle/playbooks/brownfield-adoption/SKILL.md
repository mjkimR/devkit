---
name: brownfield-adoption
description: Adopt spec-driven development in an existing repository that already has code and docs or specs Markdown; install devkit-spec and roll out its rules, contain legacy documents and rule violations so the checks pass, then migrate legacy content into the Living Spec through normal work.
---

# Brownfield adoption

The spec rules check the Markdown already under `docs/` and `specs/` (paths, frontmatter, number-based IDs such as
`ADR-0001`). This playbook contains that debt so `devkit rules check` passes; legacy content then moves into the
Living Spec as work touches it ([migration](references/migration.md)).

Contain debt without editing a rule: move legacy files to `docs/materials/`, which the spec rules leave free-form,
and record any other deferral as a `.devkit/config.toml` entry the user decided.

## Prerequisites

- The user invoked or confirmed this playbook; that invocation authorizes the moves.
- The project uses `uv`, and the current state is committed as a rollback point.

## Step 1: Install and take the legacy set

```bash
uv add --no-build-package pyyaml --dev "devkit-spec @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-spec"  # brings devkit-docs and devkit-agt
uv run devkit sync
uv run devkit rules check
git ls-files -- 'docs/*.md' 'specs/*.md' > /tmp/legacy.txt
```

- Remove from the set the paths `spec:docs-skeleton` seeded, if it was added, and files already shaped like the
  Living Spec; those stay in place and are fixed as ordinary work.
- Review a long or mixed set with the user.

## Step 2: Contain

Choose per group with the user:

| Situation | Containment |
| :--- | :--- |
| Legacy Markdown under `docs/` or `specs/` | Move it to `docs/materials/_legacy/<original path>` (default) |
| A file a tool needs at its path (an ADR tool, a docs-site build) | Reconfigure the tool, or list the path under `[rules] exclude` |
| A linter rule whose debt is fixed in place, area by area | `[rules.phase_overrides]` `RULE-<id> = "hygiene"` |
| A rule severity that does not fit the project yet | `[rules.severity_overrides]` |

```bash
while IFS= read -r f; do
  mkdir -p "docs/materials/_legacy/$(dirname "$f")"
  git mv "$f" "docs/materials/_legacy/$f"
done < /tmp/legacy.txt
```

- Update references to the moved paths outside the legacy tree: `rg -n --hidden 'docs/|specs/' --glob '!.git/**'
  --glob '!docs/**' --glob '!specs/**' --glob '!.devkit/**'`.
- A moved file's relative link out of `_legacy/` now fails `RULE-markdown-link`: prefix it with `../../../`, or, with
  the user's decision, exclude `docs/materials/_legacy/**`.
- Write each deferral's reason as a comment directly above it:

  ```toml
  # Brownfield adoption: the ADR tool reads docs/decisions/NNNN-*.md (user decision).
  [rules]
  exclude = ["docs/decisions/0*.md"]
  ```

Propose the containment as one commit before any migration, so moves and content edits are reviewed apart.

## Step 3: Docs skeleton, policy and commit gate

- **Docs skeleton** (optional): `uv run devkit add spec:docs-skeleton`. Point a link to a legacy index such as
  `docs/README.md` at its `_legacy/` copy when the reader needs the old content.
- **Policy**: show `uv run devkit spec policy` and record the user's decisions in `.devkit/config.toml`.
- **Commit gate**: the `rules-check` gate refuses a commit touching a file with an error finding. The user chooses to
  fix, park or lower the rule, or set `enabled = false` in `[gates.settings.rules-check]`.

## Completion conditions

- `uv run devkit rules check` and `uv run devkit gate status` exit `0`, and every `.devkit/config.toml` entry added
  carries its reason.
- One small real change has gone through the `spec` skill; an empty `_legacy/` is not required.
- The commits are proposed: containment, then any migration.
