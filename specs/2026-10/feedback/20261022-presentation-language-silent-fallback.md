---
id: FB-presentation-language-silent-fallback
title: Unsupported presentation.language silently renders as en
scope: repo
kind: friction
category: tool-error
target: devkit sync (presentation.language, devkit_dist.features.project.services.presentation.resolve_language)
skill: spec-orchestrate
agent: claude-code
origin: user
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-22
---

# [FB-presentation-language-silent-fallback] Unsupported presentation.language silently renders as en

## 1. Friction / Question (friction, question)

- **Context**: A workspace set `[presentation] language` in `.devkit/config.local.toml` to a spelled-out language name and ran `devkit sync` to re-render the `response-style` skill.
- **Expectation**: Either the value takes effect, or configuration validation or `devkit sync` reports that the value is unsupported, with a stable code and a fix naming the accepted values.
- **Actual**: `validate_runtime_tables` accepts any string. `resolve_language` maps every value other than `auto`, `en` or `ko` to `en` with `fallback=True`, but no command reports the fallback: the only consumer of the result is `devkit config show`'s `presentation_language` field. Sync succeeded and rendered `Use en as the default conversation language` into every projected copy, so the agent replied in English while the configuration appeared to request another language. The cause was found only by reading the source.
- **Workaround (or Interpretation Chosen)**: Set the value back to `ko` and re-run `devkit sync`; the projections then rendered `ko`.
- **Suggestion**: Reject unsupported values at configuration validation (`CONFIG_INVALID`-style error naming `auto`, `en`, `ko`), or at least return a `WARNING` notice from `devkit sync` and `devkit status` whenever `fallback` is true. Accepting common aliases (`korean`, `english`) is optional; an explicit refusal is enough. Assessment: a silent fallback contradicts the agent-first output contract (anything an agent must act on carries a code and a directive), and the cost of the check is one branch in `validate_runtime_tables` or one notice in sync.

## Diagnostic Details

- **Reproduction**: Set `[presentation] language = "korean"` in `.devkit/config.local.toml`, run `uv run devkit sync`, then read line 48 of `.claude/skills/response-style/SKILL.md`.
- **Expected / Actual**: Expected an error or a warning for the unsupported value; actual is a successful sync that renders `en`.
- **Versions**: devkit 0.1.1 at main 542f4461.
- **Conditions**: Local configuration only; `response-style` selected with preset `all`; the template variable uses `default_from = "presentation.language"`.
- **Workarounds Attempted**: Changing the value to `ko` and re-syncing worked.
- **Related Assets**: `packages/devkit-dist/src/devkit_dist/features/project/services/presentation.py` (`resolve_language`), `packages/devkit-dist/src/devkit_dist/features/project/repositories/local_config.py` (`validate_runtime_tables`), `packages/devkit-catalog/src/devkit_catalog/response_style/bundle/` (`bundle.toml`, `SKILL.md.jinja`).

## Evidence

```text
presentation.py: fallback = requested not in ("auto", "en", "ko")
                 return PresentationLanguage(requested, "en" if fallback else requested, source, fallback)
rg "\.fallback\b" packages/*/src  -> no matches (the flag is never read)
local_config.py: ("presentation", "language", "auto", str)  -> only the type is checked
After sync with the unsupported value, .claude/ and .agents/ response-style SKILL.md line 48:
  "Use en as the default conversation language ..."  (identical sha256 in .devkit/transient/local-render.json)
After setting the value to ko and re-syncing: "Use ko as the default conversation language ..."
```

## Disposition

Directly resolved by `SPEC-feedback-quick-fixes` with the suggestion's warning option, by user decision, keeping the English fallback that `ADR-configuration-language-and-rendering` decides. Any `[presentation] language` other than exactly `auto`, `en` or `ko` still resolves to `en` with `fallback=true`, but `devkit sync`, `devkit status` and `devkit config show` now return a `PRESENTATION_LANGUAGE_UNSUPPORTED` `WARNING` under `notices` for each shared or local file whose value fell back, naming the file and the value, with a `[FIX]` naming the accepted values `auto`, `en` and `ko` and the file to edit. The warning changes no exit code except under `--strict`. No aliases are accepted.

Verification: `test_presentation.py` covers the warning for the shared file, the local file and both, and none for supported values; the sync scenario in `distribution/test_local_config.py` renders `en` for an unsupported value and expects the warning from `sync_project`, `config show` (exit 0, exit 1 under `--strict`), `status` and `devkit sync` stderr. A manual `uv run devkit sync` with `language = "korean"` in `.devkit/config.local.toml` printed the `[WARN]` block on stderr and exited 0. `just test-affected` ran the full suite: 4462 passed, 14 skipped. Integration remains a separate Host step.
