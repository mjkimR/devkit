---
id: PLAN-ux-coverage-explicit-exceptions
spec: SPEC-ux-coverage-explicit-exceptions
---

# Technical Plan: `SPEC-ux-coverage-explicit-exceptions` Recognize explicit global and off-screen UX coverage exceptions

## 1. Constitution & Invariant Review

- `ADR-ux-screens` is superseded in part by `ADR-explicit-ux-coverage-exception-notation` (coverage exceptions and
  the off-screen phrase) and `ADR-ux-coverage-step-targeting` (uncited-step targeting); both ADRs and the
  "Superseded in part by" pointers landed with the handoff. No further ADR is needed.
- `CAP-GOV-spec-rules` 3.15 (`RULE-ux-links`) keeps every MUST; 3.16 (`RULE-ux-coverage`) changes its SHOULD and
  the section 3.1 row, restated at `living-spec-draft`.
- `ARCH-05-2-components`: the change stays inside the `governance` feature of `devkit-docs` (services, usecases) and
  the `docs` bundle's rule, instruction and template assets; no new feature edge. `ux_links.py` logic is a non-goal.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `devkit_docs.features.governance.services.ux` | Parses both markers once: `Interaction.global_reason` (`None` unclassified, `""` without a reason, else the reason) from a cell whose stripped text matches `^global:` (`re.IGNORECASE`), returned by `_step_refs` as `()` pairs and valid; `Step.off_screen` (same tri-state) from the first step line matching `\boff[ -]screen:` (`re.IGNORECASE`), the reason being the rest of the line with trailing whitespace and one trailing `)` dropped. `step_empty`, `step_valid`, `steps`, `screens`, `entries`, `terminal` and `reachable` are unchanged. |
| `devkit_docs.features.governance.usecases.ux_coverage` | Skips a row with a non-empty `global_reason` and a step with a non-empty `off_screen` and no screens; adds the three defective-form reports; places every step report on the use case when the run targets it, else on the first listing UX document the run targets (reversing today's order). |
| `devkit_docs.features.governance.usecases.ux_links` | Text only: the module docstring and the invalid-cell remediation name `global: <reason>` beside the empty cell. |
| `bundles/docs/bundle/rules/ux_coverage/{guide.md,tests/test_rule.py}` | Guide: causes, remediation, an Exceptions section with both markers, the defective forms and the targeting; tests: the AC fixtures. |
| `bundles/docs/bundle/rules/ux_links/{guide.md,tests/test_rule.py}` | Guide: the classified cell as an accepted Step cell; tests: the mixed and misspelled cells, the global row beside existing errors (AC-07, AC-08). |
| `bundles/docs/bundle/instructions/{ux-writing,usecase-writing}.md`, `templates/ux.md` | One complete example each; the template's Interactions comment shows the `global:` form. |
| `docs/capabilities/governance/CAP-GOV-spec-rules.md` | 3.1 rows, 3.15 Step cell sentence, 3.16 exceptions, defective forms and targeting, with why the two rules target differently. |
| `.devkit/managed/docs/` | Regenerated copies (`devkit sync`, `devkit generated regen`), never edited. |

No new dependency.

## 3. Component & Interface Design

Normative model fields (`services/ux.py`):

```python
@dataclass(frozen=True, slots=True)
class Step:
    ...
    off_screen: str | None   # None: no phrase; "": phrase without a reason; else the reason

@dataclass(frozen=True, slots=True)
class Interaction:
    ...
    global_reason: str | None  # None: not classified; "": `global:` without a reason; else the reason
```

Cell grammar: `cell.strip()` matching `^global:\s*(.*)$` (case-insensitive) is a classification; `_step_refs`
returns `((), True)` for it, so `RULE-ux-links` sees a valid, pair-less cell. Any other cell keeps today's parse, so a
cell starting with pairs and holding `global:` later fails the separators check as before.

Step phrase: over the step's raw lines in order, the first match of `\boff[ -]screen:[ \t]*(.*)$`
(case-insensitive); the reason is the group with trailing whitespace stripped and one trailing `)` removed, then
stripped again.

Coverage reports (messages are the contract; line placement per `ADR-ux-coverage-step-targeting`):

| Condition | Message | Where |
| --- | --- | --- |
| `step_empty` | `interaction has no Step` | UX document, row line |
| `global_reason == ""` | `interaction is classified global without a reason` | UX document, row line |
| no screens, `off_screen is None` | `<UC> step <key> cites no UX document` | use case at the step line if targeted, else first listing UX document at its `usecases` entry with ` (<UC path>)` |
| no screens, `off_screen == ""` | `<UC> step <key> is classified off screen without a reason` | same |
| screens and `off_screen is not None` | `<UC> step <key> is classified off screen but cites <UX>` (first cited ID) | same |

## 5. Error Handling & Edge Cases

- A reason containing `|` ends the cell at the bar (Markdown); the rest is the next cell. Not special-cased.
- A step with two phrases: the first decides. A phrase inside an inline code span counts (assumption in the spec).
- A `global:` row on a modal or panel is accepted; element checks are `RULE-ux-links`'s and unchanged.
- The targeting change moves only the use-case-side reports; `interaction has no Step` and the new
  `classified global` report stay on the UX document.

## 6. Verification & Test Plan

- `uv run devkit rules test RULE-ux-coverage RULE-ux-links` (the deployed copies' tests, AC-01 to AC-08, AC-10).
- `just test devkit-docs` (package tests, including the existing parser integration tests, AC-09).
- `just lint devkit-docs`, `just check devkit-docs`.
- `uv run devkit rules check docs/` and `uv run devkit generated check`, `uv run devkit sync --check` (AC-09, AC-11).
- The AC-11 `grep` lines.
- `just test-affected` before the final change report.
