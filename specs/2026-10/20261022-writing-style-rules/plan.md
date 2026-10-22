---
id: PLAN-writing-style-rules
spec: SPEC-writing-style-rules
---

# Technical Plan: `SPEC-writing-style-rules` Writing style rules and layout-free guidance tests

## 1. Constitution & Invariant Review

None. The rule follows the authoring bundle pattern of `RULE-skill-document-size` (`CAP-GOV-rule-authoring`): a
bundle-owned `BaseRule` with its guide and tests, hygiene phase, warning severity, never rewriting files.

## 2. Architecture Overview & Impact

- **Impacted Components**:
  - `packages/devkit/src/devkit_agt/bundles/authoring/bundle/rules/agent_asset_wording/`: new rule, guide and tests.
  - `packages/devkit/src/devkit_agt/bundles/authoring/bundle/bundle.toml`: asset `agent-asset-wording` in preset
    `skill-authoring`.
  - `packages/devkit/src/devkit_agt/bundles/authoring/bundle/instructions/agent-asset-writing.md`: the completion
    check names the rule.
  - `packages/devkit/tests/integration/bundles/authoring/test_bundle.py`: preset membership and deployment.
  - `packages/devkit-spec/tests/support/spec_support/bundle_text.py`: shared bundle reader.
  - `packages/devkit-spec/tests/integration/bundles/spec/*.py`: use the shared reader.
  - Docs: `docs/development/reference/rules.md` (authoring table), `ARCH-08-2-resource-taxonomy` (skill-authoring
    preset sentence).
- **New Dependencies**: None.

## 3. Component & Interface Design

### Rule

```python
@dataclass(frozen=True)
class AgentAssetWordingSettings:
    hedges: list[str]          # case-insensitive whole words or phrases
    emphatic: list[str]        # exact-case words or phrases
    time_relative: list[str]   # case-insensitive whole words or phrases
    suffixes: list[str]        # [".md", ".md.jinja"], matched with str.endswith
    paths: list[str]           # project skills and bundle skills, playbooks, instructions, subagents
```

- Scan: per line, skipping fenced code blocks (```` ``` ```` or `~~~`), multi-line HTML comments and multi-line Jinja
  comments; within a line, blank out inline code spans, straight and curly double-quoted spans, HTML comments and
  Jinja tags before matching. Column positions are not reported, only lines.
- One `Violation` per match: `message` `"<Category> \"<word>\""`, e.g. `Hedge "might"`, with a category-specific
  remediation (state the condition / give force through condition and reason / name the version, date or ID; quote
  or backtick a word that is mentioned, not used).
- Skips symbolic links and receipt-owned files, honours `ctx.is_file_targeted`, settings per file (`ctx.settings`).
- Validation: each word non-empty after strip, single line; suffixes literal and dot-prefixed; paths validated.

### Test support

`spec_support/bundle_text.py`:

```python
BUNDLE: Path                                   # devkit-spec spec bundle source
def raw(path: str | Path, environment: str = "local") -> str   # renders .jinja (or the .jinja sibling)
def text(path: str | Path, environment: str = "local") -> str  # raw() with whitespace collapsed to one space
def flat(value: str) -> str                    # collapse whitespace of any string (sections, payloads)
```

Tests assert phrases against `text()`/`flat()`; they use `raw()` only where structure matters (frontmatter, headings,
table rows, line-anchored regexes).

## 4. Error Handling & Edge Cases

- A quoted word spanning a line break is not recognized as quoted: the rule scans per line. Writers keep a quoted
  mention on one line or put it in backticks; the remediation says so.
- An odd number of quote marks on a line leaves the tail unmasked; acceptable for a warning.

## 5. Verification & Test Plan

- Rule tests in `rules/agent_asset_wording/tests/test_rule.py` cover AC-01 to AC-05.
- `test_bundle.py` covers the preset and deployment (AC-06); `devkit rules check --phase hygiene` on this repository
  reports no violation of the rule after `devkit sync`.
- AC-07: rewrap the backlog phrase temporarily and run `just test devkit-spec tests/integration/bundles/spec`, then
  restore; `rg` for per-file readers and `" ".join(` in the folder returns nothing.
- `just test-affected`, `just lint-check`, `just check`, `devkit rules check --ci --base <base>`.
