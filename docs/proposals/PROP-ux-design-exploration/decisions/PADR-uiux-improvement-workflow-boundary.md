---
id: PADR-uiux-improvement-workflow-boundary
title: Keep UI/UX improvement opt-in and within the project delivery workflow
summary: "For reusable UI/UX improvement, we ship an explicitly invoked skill with local roles and reuse the consumer delivery workflow, to carry changes through existing checks, accepting host-dependent tools and implementation boundaries."
proposal: PROP-ux-design-exploration
status: draft
created_at: 2026-11-05
---

# [PADR-uiux-improvement-workflow-boundary] Keep UI/UX improvement opt-in and within the project delivery workflow

## 1. Context & Problem Statement

UI/UX improvement can need diagnosis, independent design perspectives, implementation and usage verification.
The reusable skill must preserve those outcomes without installing a competing delivery lifecycle or loading
design-only role instructions into unrelated work. Consumers can use different development approaches and tools.

## 2. Decision Drivers

- Carry an authorized improvement through actual changes and proportionate verification.
- Preserve consumer workflow authority and keep installation content-only.
- Load specialist role bodies only during their selected assignments.
- Keep small requests inexpensive and make no unmeasured quality guarantee.

## 3. Considered Options

- Register global specialist agents and a dedicated implementation workflow: native role settings become possible,
  but unrelated work sees role metadata and the skill competes with the consumer's delivery process.
- Ship an explicitly invoked skill with local roles and retain the consumer workflow: preserves focused loading
  and existing approvals, but role restrictions and available tools depend on the invoking host.

## 4. Decision Outcome

- `uiux-improve` is an opt-in catalog bundle with a user-invoked entry and local role documents. It registers no
  global specialists and supplies no always-loaded design instruction.
- The coordinator chooses useful perspectives, owns synthesis and continues requested implementation through
  the consumer's existing development workflow. Selecting the bundle or invoking the skill changes no workflow
  policy and grants no commit, integration or publication authority.
- The skill can finish a narrow request inline. Research, alternatives and critique are optional means of
  improvement rather than a required cast, report, score or experiment.
- A fresh child receives only its bounded assignment and selected role instructions where the host supports it.
  Those instructions confer no native permission or shared-resource isolation.

The prospective capability named in `target-docs.md` will restate these boundaries with normative strength during
Development; exact rule traces are added when that document exists. This decision does not supersede the
research-specific `ADR-skill-local-research-roles`.

## 5. Consequences

The skill can support existing consumer delivery processes without requiring devkit-spec or devkit-docs.
The coordinator remains responsible for actual implementation and check evidence. Native host settings, tools
and approvals remain external constraints; a missing tool can limit what was verified.

## 6. Confirmation

Focused catalog integration tests will check opt-in selection, explicit-invocation projections, skill-local role
files and absent global role projections. An installed-consumer test will check wheel contents and CLI selection
without spec tooling. Review only: instruction usefulness, proportionate delegation and compatibility with the
consumer workflow. No test claims measured aesthetic quality or advantage over one agent.
