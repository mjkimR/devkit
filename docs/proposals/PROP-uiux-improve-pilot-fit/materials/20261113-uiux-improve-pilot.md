---
id: MAT-uiux-improve-pilot
created_at: 2026-11-13
---

# [MAT-uiux-improve-pilot] app-uiux-improve consumer pilot evidence

Observations from one run of `app-uiux-improve` 0.1.6 in a consumer repository on 2026-11-12 and 2026-11-13. The
consumer is an SDD project (`worktree=auto`) with a SvelteKit SPA under a monorepo subdirectory, a FastAPI backend on a
shared remote database, and OOUX documents (glossary, object register, `docs/ux/`). The request was a whole-surface
color-system refresh of the web UI. Impeccable was installed mid-session as a Claude Code plugin, and the user selected
the Impeccable track. Paths and identifiers of the consumer are masked.

## 1. Run shape

1. Setup: `devkit add app-uiux-improve`; Impeccable plugin install; `PRODUCT.md` and `DESIGN.md` kept local-only
   through `.git/info/exclude` (`.impeccable/` was already ignored).
2. Impeccable `init` in a child agent, split into two phases (finding A1).
3. Inspection of the running UI (finding A3), then independent designer, unconventional-designer and critic first
   passes in fresh children.
4. Direction synthesis and user picks, before any Unit existed.
5. A `spec`-depth SDD Unit: `specify` (spec, Screens drafts, `ux-review` rounds 1-2), `build-verify` (one Impeccable
   child running `colorize`, `polish` and `audit` from a brief), `review-refine` (`review-01`, `reverify-01`),
   `living-spec-draft` (`reconcile-check-01`, `reconcile-check-02`), `collect-feedback`, `final-change-report`, local
   integration.

## 2. Workflow cost and fit

- The dev branch carried 18 commits plus the merge commit. Eight commits each record one envelope (`ux-review-01`,
  `ux-review-02`, `review-01`, `reverify-01`, `reconcile-check-01`, `reconcile-check-02`, `feedback-01`,
  `final-report-01`) and two more change only the spec status. Product code, tests and the UI README changed in
  four commits; the rest wrote `spec.md`, `plan.md`, `tasks.md`, a steering style file, UX document updates and
  `reconcile.md`.
- The design direction emerged iteratively: role passes, then user picks, then reviewer findings, then polish. The
  up-front `spec.md` contract needed amendments during `build-verify`. Code review raised a P3 that the contract was
  amended during build without named authority; a later commit recorded user authority for the build amendments.
- The coordinator turned the user's task focus ("color first") into a prohibition on interaction and layout changes.
  The spec author hardened it into a Non-Goal, although `PRODUCT.md` stated only use-case coverage as a constraint.
  The reviewer then had to request a scope exception, and the Non-Goal was lifted mid-way.
- Value the workflow added: the UX reviewer found a semantic defect (an answered but unapplied decision displayed as
  done); code review found a test gap (hard-coded tint alphas instead of values derived from the badge component);
  reconcile kept the UX documents in step with the change.

## 3. Findings

| ID | Observation | Workaround that worked |
| --- | --- | --- |
| A1 | Impeccable `init` asks the user a question round; the skill routes it to a user-operated session. | Child phase 1 scanned and drafted the question round without writing; the coordinator pre-filled answers from the OOUX documents, asked the user only the gaps, then resumed the same child for phase 2 (writes). The user answered every question that the documents did not settle. |
| A2 | A fresh child on Claude Code could not load the plugin-installed Impeccable through the Skill tool (the plugin skill was not listed in the child). `ADR-impeccable-session-authority` records this as unverified. | Twice, the child read `SKILL.md` and `reference/*.md` from the plugin cache instead. |
| A2b | Impeccable's `AUTONOMY_DIRECTIVE_CHECK` asks for a live probe a subagent cannot perform. | Child proceeded under the brief's stop conditions. |
| A2c | `impeccable context` at the repository root reports `hasVisualImplementation=false` for a UI under a monorepo subdirectory; with `--target <ui path>` it still reported `false`. | Brief named `--target`; framing came from the OOUX documents. |
| A3 | SKILL step 2 says "using the running UI when available". The coordinator first chose the deployed environment, which cannot show branch changes before a deploy. | Local dev server of the branch build with Playwright API mocking (no shared database), and a re-runnable before/after screenshot harness. The harness also found an out-of-scope 390 px horizontal overflow. |
| A4a | Task focus became a Non-Goal (section 2). | User caught it; Non-Goal lifted. |
| A4b | Impeccable's craft floor (no colored `border-left` wider than 1 px on list items) conflicted with the spec's 3 px attention rule. | The child applied "brief wins" on its own judgment; the brief did not state precedence. |
| A4c | The child fixed the out-of-scope 390 px overflow inside a file on the edit list. Acceptance compared `git status` with the edit list and could not tell an in-list but out-of-scope change. | Coordinator compared the diff with the spec's acceptance criteria by hand. |
| A5 | `PRODUCT.md` and `DESIGN.md` were local-only (git-excluded), so an SDD worktree would not contain them; Impeccable `init` advises committing them. | Under `worktree=auto` with a clean checkout, an in-place branch (`--no-worktree`) kept them visible; the brief passed main-checkout absolute paths read-only and told the session to skip the commit advice. |
| A6 | The skill projects with `disable-model-invocation: true`. After a mid-session install, the user agreed to proceed in natural language, but the coordinator could not invoke the skill. | The coordinator followed the projected `SKILL.md` text manually. "Run only when the user explicitly invokes this entry" did not say whether that counts. |
| A7 | Designer-role contrast estimates (an L^3 approximation) passed a light-theme attention color that measured 2.06:1 on a card. | A computed OKLCH to sRGB contrast check during `specify` caught it. |

## 4. What worked

- Independent first passes converged on the same core (one attention token, split routine and attention states); they
  diverged only on the primary hue and a failed-state mapping, which became a clean user decision.
- The Impeccable child stayed inside a 34-file edit list; acceptance (`git status` against the list, HEAD unchanged)
  was clean.
- Running direction synthesis before the consumer workflow's first step meant `spec.md` captured an already-approved
  direction.
