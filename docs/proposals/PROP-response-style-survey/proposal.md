---
id: PROP-response-style-survey
title: Survey reply-style practice to refine response-style
summary: "Proposes one portable response style with a conclusion-first opening, arrow-marked core sentences and supporting explanation, required-format exceptions and example-based review."
status: reviewing
created_at: 2026-10-19
target_area: distribution/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - distribution/
    - packages/devkit-catalog/src/devkit_catalog/response_style/
    - packages/devkit-catalog/tests/test_bundles.py
    - scripts/smoke.sh
  excludes:
    - packages/devkit-dist/src/
    - packages/devkit-spec/src/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-response-style-survey] Survey reply-style practice to refine response-style

## 1. Background & Hypothesis

The response-style bundle combines important content obligations with recurring visual instructions. Its
block-count thresholds and fixed paragraph sizes are local editorial choices, not established determinants
of comprehension. The proposed rewrite uses a conclusion-first opening and a consistent marked-point format,
with depth and format exceptions that follow the request. Its helpfulness remains a judgment to discuss with concrete examples.

The survey inspected actual prompt/style files, license texts and published evaluation descriptions rather
than relying on repository names or stars. It is a focused review of reply instructions, not an audit of the
repositories' entire code or a reproduction of their benchmarks. Seven prompt/style repositories and three
official writing guides are recorded in `MAT-response-style-source-selection`. Popularity screens sources;
it does not establish that their rules improve devkit replies.

## 2. Proposed Direction

- **Failure conditions:** Treat missing or distorted decision-relevant information as the more serious failure.
  Also reject necessary information buried under repetition or irrelevant detail. Preserve the facts, place them
  early with their qualifications, and remove distractions. Concise reporting does not reduce required work.
- **Content and output obligations:** Preserve required facts, units, scoped conditions, material risks and
  requested formats. A style rule cannot drop a workflow field or change a supplied fact to shorten a reply.
- **First sentence:** For an ordinary reply, its first sentence states the overall answer, recommendation or
  current result, including a condition that changes that conclusion or the uncertainty that prevents it.
  A short answer may end there if complete; a long answer develops that conclusion.
- **Explanation:** Answer a narrow question directly; explain reasoning, examples and alternatives when the
  request calls for them. A long deliverable gets the space its requirements need. Do not force all replies
  into a terse mode or an educational mode.
- **Presentation:** Use `→ **Core sentence.** Supporting explanation` as the default ordinary point format,
  with blank lines between points. The bold sentence states that point's conclusion; the first point carries the
  overall answer and later points add distinct information. Use no block-count or sentence-count threshold.
  Follow required user/workflow formats, and return artifact-only requests without conversational framing.
- **Work reports:** Name the scope of what is finished and what remains, with actual verification and material
  limitations. A completed survey, edit or test does not imply completion of the whole request. Show necessary
  user decisions without appending empty offers or creating new approval requests.
- **Language and deployment:** Keep one style and the existing Jinja `vars.language` branch: `auto` follows the
  current request; a configured language supplies the default; an explicit user language request overrides either.
  Repository/task requirements govern deliverables. Retain short Korean wording guidance, opt-in packaging and
  all current projections. No presets or host-specific style variants.
- **Always-loaded guidance:** Keep one pointer within the 300-UTF-8-byte contract in `CAP-DIST-manifest-spec`.
  This applies to the guidance fragment inserted into `AGENTS.md`, not the whole file or the skill body.
  Detailed rules stay in `SKILL.md` without a new byte, word or token ceiling. Actual compaction behavior is
  unverified; this work changes no shared guidance limit.

`MAT-response-style-rewrite-draft` provides the concrete skill-body draft, pointer and four authored examples.
`PADR-response-style-adaptive-replies`, `PADR-response-style-source-selection`,
`PADR-response-style-measurement` and `PADR-response-style-guidance-budget` record the proposed choices.
These are drafts for user direction review, not a recorded `plan-accept` decision.

## 3. Review and Implementation Scope

Use the authored examples to discuss the proposed behavior for scoped facts, unfinished work, explanations and
artifact-only requests. They are illustrations, not observed before/after runs or evidence of measured quality.
Check content and format obligations separately from subjective wording, depth and readability. No numeric
score automatically selects a style. `MAT-response-style-measurement-design` defines the verification limits.

The Host withdrew its obsolete structured-cohort question; no live host, spending allowance or comparison run
was approved. Such collection is optional if a concrete need appears and is not a prerequisite for accepting
this direction. A generation quota, scorer, benchmark framework and reminder-length experiment are non-goals.

After the user's design acceptance, normal handoff creates the Development Unit. Development writes its spec,
plan and tasks, then implements the accepted bundle text, adjusts the existing deployment tests and smoke
assertions, and reflects its current behavior in `CAP-DIST-content-packages`. Keep source references and design
rationale in materials rather than copying them into runtime instructions. Shared distribution validation,
workflow report formats and unrelated bundle behavior stay outside the scope.

Verify language/template behavior and existing native projections, relevant lint and type checks,
`just test-affected`, consumer smoke and repository rules. Use independent medium Development review and the
required Living Spec reconciliation. Report what those checks establish: correct text deployment and reviewed
behavioral instructions, without claiming universal conversational improvement.

## 4. Acceptance and Lifecycle

Planning provides a concrete rewrite recommendation, complete source notes and reviewable examples, resolves
independent criticism and presents the direction to the user. Only explicit user acceptance records
`plan-accept`; it neither authorizes final integration nor asserts a measured quality gain. Handoff promotes
the appropriate materials and PADRs through the normal workflow. At completion retain the checks actually run,
the chosen behavior and its limits. Rejection preserves open feedback before normal retirement.
