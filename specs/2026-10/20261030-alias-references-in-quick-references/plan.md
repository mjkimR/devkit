---
id: PLAN-alias-references-in-quick-references
spec: SPEC-alias-references-in-quick-references
---

# Technical Plan: `SPEC-alias-references-in-quick-references` Check document IDs in quick references and keep rename tables intact

## 1. Constitution & Invariant Review

None. `ADR-document-id-aliases` makes an alias reference in a current document an error that `devkit rules fix`
rewrites; extending that to the quick references applies the same decision to more files without changing it.
`ADR-immutable-decisions-editable-records` already says the fix rewrites ADR and PADR alias references; the guide is
corrected to it. `ADR-rules-declare-their-input-files-undeclared-rules-always-run`: `RULE-document-reference` keeps
`inputs` unset (every file can change its findings), so a targeted run on a quick reference evaluates it and the new
pass reports and fixes only targeted files (`CAP-GOV-rule-authoring`, Optional `inputs`). No architecture `MUST`
changes, so no ADR is needed.

## 2. Architecture Overview & Impact

- `devkit_docs.features.governance.usecases.document_reference` (devkit-docs): a settings dataclass, a quick-reference
  pass in `check` and a quick-reference rewrite in `fix`. The steering pass and the indexed-document checks keep
  their behavior; the steering pass and the new pass share one cited-ID resolver.
- `bundles/docs/bundle/rules/document_reference/guide.md`: What is checked, Cause, Remediation (the stale ADR/PADR
  clause dropped, the quick-reference rewrite added) and Configuration (`quick_references`).
- `bundles/spec/bundle/skills/spec-specify/SKILL.md` (devkit-spec): the References bullet gains the rename sentence.
- Living Spec (`spec-sync`): `CAP-GOV-spec-rules` section 3.3 and catalog row; `CAP-DOCS-document-model` renaming
  step (section 3.5 item 5) only, by the agreed write scope.
- Repository content: the four alias references of the base (`docs/development/ci-cd.md`,
  `docs/development/workflow.md`, `packages/devkit-viewer/README.md` twice) rewritten by the fix; the README sentence
  that then names `ADR-viewer` twice is reworded by hand.
- No new dependency. `match_path` and `validate_pattern` come from `devkit_agt.features.rules`, as in
  `RULE-agent-guide-size`.

## 3. Component & Interface Design

### Decisions

1. **Path set as a rule setting** (preferred by the user over hard-coding): `quick_references: list[str]`, patterns in
   the `**` grammar of `[rules] exclude`, validated with `validate_pattern` in `validate_settings`
   (`RULES_SETTINGS_INVALID`). Defaults: `docs/development/**/*.md`, `guides/**/*.md`, `packages/*/README.md`,
   `tools/*/README.md`. Read per file with `ctx.settings(self, path)`, so path overrides work as for
   `RULE-agent-guide-size`'s `paths`. Nested READMEs stay out: the bundle seed READMEs ship to consumer projects.
2. **Severity error** for unresolved and ambiguous IDs, matching steering. Evidence: a scan of the base with the
   index found zero unresolved cited IDs and four alias citations in the default set, so error severity adds no
   finding the change does not fix; a consumer can narrow the setting.
3. **Placeholders and examples**: no exemption mechanism. The pass reads `visible_lines` (fenced and indented code,
   HTML comments, escapes, link labels and `~~strikethrough~~` are masked; only an inline code span holding exactly
   one ID counts), and placeholders such as `SPEC-<slug>` do not match the ID grammar inside a code span. The base
   scan above shows nothing to exempt; example IDs are written as plain text or in code blocks, as `spec-specify`
   already asks.
4. **Which files**: Markdown files listed by `ctx.cache.find_files(workspace_root)` (snapshot-aware, Git-ignored and
   dependency directories skipped) whose path matches the effective `quick_references`, that are targeted
   (`ctx.is_file_targeted`, so `[rules] exclude` applies), that no indexed document has as its path (an ID-bearing
   file is already checked once as a document) and that are not steering files (the steering pass owns those).
5. **Fix**: only an alias citation that resolves to exactly one other document is rewritten; the span is located by
   the visible line's `offset` plus the match column (masking keeps offsets), and the original text there must equal
   the alias. Unresolved IDs are never rewritten. The steering pass stays report-only (Non-Goal 2).

### Interface

```python
@dataclass(frozen=True)
class DocumentReferenceSettings:
    quick_references: list[str] = field(default_factory=lambda: list(QUICK_REFERENCES))

class DocumentReferenceRule(BaseRule):  # settings=DocumentReferenceSettings()
    def validate_settings(self, settings: DocumentReferenceSettings) -> None: ...  # validate_pattern each
    def _quick_references(self, ctx, index) -> list[str]: ...  # targeted, unindexed, matching paths
```

Messages (column = code span start + 1):

- alias, fixable: `` <alias> is an alias of <ID>; reference `<ID>` ``, remediation `` Run `devkit rules fix` to
  replace it with <ID> ``;
- unresolved: the `_resolve_problem` messages of indexed documents, remediation "Correct the cited ID or give its
  intended document a unique ID".

## 5. Error Handling & Edge Cases

- A file that is not valid UTF-8 (`read_text_strict` returns `None`) is skipped by check and fix, as in the steering
  pass.
- A citation repeated on one line is reported once per occurrence; the fix rewrites every occurrence.
- An alias that collides resolves as it would without the alias: reported as ambiguous or, when a document declares
  it as its ID, accepted; never rewritten.
- A Git snapshot run (`--staged`, `--ci`) reads the snapshot through the cache; the fix writes through
  `ctx.cache.write_text` and honors `dry_run`.

## 6. Verification & Test Plan

- Rule tests in `bundles/docs/bundle/rules/document_reference/tests/test_rule.py` (loaded as deployed):
  AC-01 (four default locations, check then fix then clean recheck), AC-02 (missing, duplicate, ambiguous alias; fix
  leaves the file unchanged), AC-03 (masked forms, files outside the set, indexed file under `docs/development/`
  reported once, targets and `exclude`), AC-04 (custom set via `settings`, empty list, invalid pattern raises
  `RulesRunError` with `RULES_SETTINGS_INVALID`).
- AC-05: `uv run devkit rules check` on the whole workspace after `devkit rules fix`.
- AC-06: `uv run devkit rules explain RULE-document-reference` read back; a guide assertion in the rule test file.
- AC-07: a guidance test under `packages/devkit-spec/tests/integration/bundles/spec/` pins the `spec-specify`
  sentence; the Living Spec wording is checked by `reconcile-reviewer`.
- Commands: `just lint devkit-docs` / `just lint devkit-spec`, `just check devkit-docs`, `just test devkit-docs <rule test>`,
  `just test-affected` (keep its `mode=full` fallback), `uv run devkit rules check`. After editing bundle sources,
  `uv run devkit sync` and commit what it writes.
