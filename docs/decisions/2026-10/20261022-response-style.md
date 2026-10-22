---
id: ADR-response-style
title: Response style for adaptive agent replies
summary: "For agent replies, we use one conclusion-first, arrow-marked response style with a 300-byte pointer, synthesized from screened sources and verified by example review and bundle checks, to keep replies consistent and faithful, accepting no measured quality gain or long-session retention claim."
status: accepted
created_at: 2026-10-22
aliases:
  - ADR-response-style-adaptive-replies
  - ADR-response-style-guidance-budget
  - ADR-response-style-measurement
  - ADR-response-style-source-selection
---

# [ADR-response-style] Response style for adaptive agent replies

- **Status**: Accepted
- **Date**: 2026-10-22
- **Deciders**: @minjae
- **Involved Components/Capabilities**: the `response-style` bundle, `capabilities/distribution/`
  (`CAP-DIST-content-packages`, `CAP-DIST-manifest-spec`)

---

## 1. Context & Problem Statement

The previous style combined content obligations with recurring visual instructions. Block-count thresholds and fixed
paragraph sizes are separate choices from a consistent point format; none establishes measured reading benefits. The
selected presentation preference uses a complete core sentence followed by supporting explanation. A successful edit
or survey also needs to remain distinct from completion of the whole task in a progress report. The existing
`SKILL.md.jinja` already named omission and overload, limited brevity to reporting rather than work, and rendered
`vars.language` into a concrete instruction; the rewrite preserves these behaviors and does not replace language
rendering with a generic instruction to use an unspecified configuration.

`CAP-DIST-manifest-spec` limits each guidance fragment to 300 UTF-8 bytes. A statement that a once-read skill fades in
a long session is a hypothesis, not an observed reload or compaction failure. More always-loaded text affects every
bundle sharing the distribution contract.

A small numeric score cannot decide how much a reply helps a particular reader. A controlled live comparison also
needs deliberate isolation and a chosen execution budget, neither of which is needed to discuss concrete proposed
wording. Native role inheritance alone cannot provide an unstyled baseline.

One author's prompt and repository popularity cannot show whether response-style rules work. Widely copied prompts
can create false corroboration, and a repository license does not establish website reuse terms.

---

## 2. Decision Drivers

- Preserve meaning and required formats, adapt depth to the request, keep a portable bundle, and give users clear
  scope and verification in work reports.
- Avoid rules that confuse a subjective presentation preference with an objective quality guarantee.
- Keep portable asset behavior and a bounded prompt budget. Change a shared contract only when the missing
  always-loaded information causes a measured failure before ordinary skill discovery can address it.
- Use reviewable examples, distinguish illustrations from observations, and keep verification proportionate to a
  response-style bundle change.
- Use relevant first-party instructions, established projects, observable maintenance, diverse response goals,
  traceable pins and original expression. Keep source-practice claims separate from measured effectiveness.

---

## 3. Considered Options

### Reply format (`ADR-response-style-adaptive-replies`)

- **Retain every visual rule and polish wording**: small edit; preserves the rigid presentation without testing its
  need. Rejected.
- **Select several source-inspired presets**: exposes preferences; adds configuration and review combinations without
  a demonstrated need. Rejected.
- **One style with conclusion-first, arrow-marked core sentences and explicit exceptions** (Selected): consistent
  ordinary replies with adaptable depth and preserved output contracts; a user preference requiring example-based
  review, with no universal quality gain claimed.

### Guidance budget (`ADR-response-style-guidance-budget`)

- **Keep one <=300-byte pointer and the discoverable skill** (Selected): existing supported contract, smallest change;
  does not assume complete long-session retention.
- **Raise the limit for all bundles**: simple validator change; unmeasured aggregate context growth. Rejected.
- **Add a per-bundle exception**: limits the immediate relaxation; new manifest policy and exception maintenance.
  Rejected.
- **Split one instruction across fragments**: existing syntax may allow more text; evades the intended budget without
  evidence. Rejected.

### Measurement (`ADR-response-style-measurement`)

- **Source survey alone**: establishes published practices; does not show the proposed text or any local behavior.
  Rejected.
- **Authored examples plus normal implementation verification** (Selected): a concrete design and evidence that its
  text is deployed correctly; does not measure reader comprehension or model-wide quality.
- **Repeated live benchmark and scorer**: observations for the selected cohort; more collection/setup cost, and proxy
  scores still do not settle preference. Rejected.

### Source selection (`ADR-response-style-source-selection`)

- **Highest-star repositories only**: recognizable projects; stars do not measure style effectiveness or expose actual
  instructions. Rejected.
- **Arbitrary rule/AGENTS collections**: broad coverage; weak provenance, duplicated opinions and uncertain default
  behavior. Rejected.
- **Relevant established prompt sources plus official guides** (Selected): auditable source practice and contrasting
  intent types; needs source and ancestry checks, with no automatic quality guarantee.

---

## 4. Decision Outcome

### Reply format

- `MAT-response-style-rewrite-draft` supplies reviewable text, a <=300-byte pointer and clearly labelled authored
  examples. (ADR-response-style-adaptive-replies)
- Respect user/repository output contracts; preserve decision-relevant facts and material limits; distinguish a
  finished step from a finished request. (ADR-response-style-adaptive-replies)
- For an ordinary reply, the first sentence gives the overall answer or explicitly unknown result. Use
  `→ **Core sentence.** Supporting explanation` for each ordinary explanatory point, with blank lines between points
  and no fixed point or sentence count. The bold lead is a complete conclusion, not a topic label; supporting text
  carries needed reasons and conditions. (ADR-response-style-adaptive-replies)
- Presentation-preference authority: user. Requested artifacts and required reports follow their own formats.
  (ADR-response-style-adaptive-replies)
- Keep the language variable, its Jinja `auto`/configured-language branches and short Korean-specific wording
  guidance. An explicit user language request overrides the conversation default; repository and task requirements
  govern deliverables. (ADR-response-style-adaptive-replies)
- State omission/distortion and obscurity as failure conditions, with omission the more serious failure. Required
  content stays present and discoverable; concise reporting never reduces required work.
  (ADR-response-style-adaptive-replies)
- Add no presets or extra decorative marks. (ADR-response-style-adaptive-replies)
- The draft supplied a direction for user review rather than an approval or deployed instruction; deployment follows
  the delivery workflow. A source citation or illustrative reply does not establish observed runtime quality.
  (ADR-response-style-adaptive-replies)

### Guidance budget

- Retain the 300-byte contract and one response style with the existing language variable. Do not implement presets,
  new variables, per-host variants, manifest exceptions or fragment splitting. A candidate may improve the pointer
  within the current limit; `MAT-response-style-rewrite-draft` supplies a candidate pointer that fits this budget.
  (ADR-response-style-guidance-budget)
- No reminder-length experiment is required. An actual limit expansion needs observed host behavior, an aggregate
  guidance budget and a new accepted design. The current scope promises no unimplemented distribution change and
  claims no measured long-session effect. (ADR-response-style-guidance-budget)
- The cap is a per-guidance-fragment cap for text inserted into `AGENTS.md`, not a total-file or skill-body cap.
  Detailed guidance stays in `SKILL.md`, and no byte, word or token ceiling is introduced for that body.
  (ADR-response-style-guidance-budget)
- The canonical bundle contract reflection goes in `CAP-DIST-content-packages`; the manifest contract stays unchanged.
  (ADR-response-style-guidance-budget)

### Measurement

- `MAT-response-style-rewrite-draft` contains the proposed wording and four illustrative request types;
  `MAT-response-style-measurement-design` states what review and deployment checks do and do not prove. Show the
  examples and rationale for subjective judgment. (ADR-response-style-measurement)
- Apply the normal independent Development review, Living Spec reflection, relevant tests, lint, types, smoke and
  rules before completion. (ADR-response-style-measurement)
- No generation quota, scoring tool or large benchmark is a required phase. The Host withdrew its obsolete cohort
  question without selecting a host or recording user approval. A later live comparison needs its own explicit
  conditions and execution allowance; it is not a dependency of `plan-accept` for this design.
  (ADR-response-style-measurement)

### Source selection

- Use the explicit screen and exclusions in `MAT-response-style-source-selection`. Seven repositories have pinned
  prompt/license sources and current metadata, including Attention Span as a dedicated reply-style project; all are
  evaluated by the same relevance and evidence criteria. Three official writing guides are a separate class with
  their own license gaps. (ADR-response-style-source-selection)
- Record each source, its scope and limitations; do not count shared or unverified ancestry as independent votes.
  (ADR-response-style-source-selection)
- Transfer ideas using original wording, never source examples, structure or copyleft/unknown-license expression.
  Track each candidate rule to a source idea or explicit local requirement and the agreed example review. Link
  observed results when an optional live comparison is undertaken. (ADR-response-style-source-selection)

---

## 5. Consequences

- **Negative / Risks**:
  - Shorter text cannot remove mandatory workflow fields, tables, numbers or risks. Writing rules describe form;
    workflow and user requirements supply required content. Facts, required formats and workflow reports cannot be
    waived by style preference.
  - Report a reviewed rewrite and the checks actually performed, rather than an unverified quality gain.
  - Smaller but directly relevant gptme qualifies; the higher-star Cline remains a reserve because its production
    prompt path was not confirmed. Goose supplies a minimal-style contrast rather than a vote for brevity. Missing
    reuse terms restrict source-expression reuse but do not create an evidence claim or implementation requirement.
- **Follow-ups**:
  - Development changes the bundle and existing deployment assertions, stays in the response-style bundle, its
    existing deployment checks and review materials, and reflects the behavior in `CAP-DIST-content-packages`.
  - Required report fields stay intact. Rewriting the shared distribution guidance contract or changing workflow
    report schemas is outside this direction; a necessary report-schema change would be separate work.
  - There is no additional approval gate, headless-launcher implementation or automatic style-selection rule.

---

## 6. Confirmation

The repository's normal checks (relevant tests, lint, types, smoke and rules), the existing response-style deployment
assertions, independent Development review, and the example review recorded in `MAT-response-style-measurement-design`.
