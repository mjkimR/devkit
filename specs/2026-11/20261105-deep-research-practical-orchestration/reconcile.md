---
reconcile_id: REC-deep-research-practical-orchestration
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-deep-research.md
    resolution: modified
  - file: docs/usecases/delivery/UC-research-an-idea-and-shape-a-roadmap.md
    resolution: modified
  - file: docs/decisions/2026-11/20261105-deliverable-driven-research.md
    resolution: modified
---

# Reconcile `SPEC-deep-research-practical-orchestration`

| Contract target | Agreement with implementation |
| --- | --- |
| `CAP-DLV-deep-research` | Rules 25–31 match entry intake/usefulness, assignment contribution, selective fold-back, technical retrieval recovery, refusal/ambiguity handling, recovery provenance and declined-validation follow-up. Existing rules and deployment authority remain intact. |
| `UC-research-an-idea-and-shape-a-roadmap` | Steps 3, 5 and 7 reflect artifact framing, targeted verification and useful retention. Extensions 3b, 5d–5f, 6a and 7c and scenarios 14–19 cover the six semantic examples. |
| `ADR-deliverable-driven-research` | Final rule traces replace proposed clause names; bounded recovery remains permitted rather than mandatory, and refusal/provenance/follow-up obligations match the source. No earlier decision is superseded. |

The entrypoint remains the existing deep-research SKILL.md; helpers and role files are not new doorways. No new
domain term, screen, architecture/dependency edge or behavior outside this capability is introduced. All approved
scope is delivered; no deferred feature or source feedback needs a follow-up destination.

The source review passed AC-01 through AC-06 by semantic walkthrough and AC-07 with existing distribution and
installed-consumer checks. These establish instruction consistency and packaging, not empirical effectiveness.

Independent reconcile review identified one P2 in generic output descriptions. The implementer qualified both
capability rows and reverified them against the unchanged planner/synthesis instructions; reconcile-check-02
records zero remaining findings. No waiver was used.
