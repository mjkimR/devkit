---
id: UX-<slug>
title: Element Title (what the person sees, e.g., Sign-in Screen)
summary: "One or two English sentences: which element this is and the task a person completes on it"   # required, English; quote it, it may contain ": "
area: <area>              # Must match parent directory docs/ux/<area>/
element: screen           # screen | modal | panel
status: draft             # draft | active | deprecated
usecases:                 # the use cases whose steps cite this element; each is named by a Step cell below
  - UC-<slug>
capabilities:             # the capabilities whose state or operations this element presents
  - CAP-<AREA>-<slug>
---

# [UX-<slug>] Element Title

<!-- File path is docs/ux/<area>/UX-<slug>.md and id matches file name. No sequence numbers. Write it with the
ux-writing instruction; visual style lives in the project's steering style files, cited, never restated here. -->

## 1. Purpose

- **Primary task**: <!-- one verb phrase: the task a person completes here -->
- **Facts to commit**: <!-- what the person must see to commit to the task -->
- **Secondary items**: <!-- where each secondary item goes: below, behind a control, another element (`UX-<slug>`) -->

---

## 2. Content
<!-- Prose region rules (relative: primary, secondary, beside, below), then a content tree. Each node names the
glossary object and the representation it shows, with its condition beside it. No character-cell layouts. A panel
this element shows is named here by its UX ID. -->

- **Primary region**: <!-- ... -->
- **Content tree**:
  - <!-- Object (representation) -->
    - <!-- Child node; shown when <condition> -->

---

## 3. States
<!-- Lower-case state names: populated plus each of empty, loading and error that applies, and any other state.
Each state offers a next action or says why none exists. -->

- **populated**: <!-- ... -->
- **empty**: <!-- ... -->

---

## 4. Interactions
<!-- One row per trigger. Step: the served use case step as `UC-<slug>` <key> (`3`, `2a`, `*a`), empty only for a
global control. From and To: states. Target: the UX ID of the element it opens, close, back or end; empty when it
stays here. Capability: the CAP that owns the operation. Feedback: what the person sees. -->

| Trigger | Step | From | To | Target | Capability | Feedback |
| --- | --- | --- | --- | --- | --- | --- |
| <!-- Press Sign in --> | `UC-<slug>` 2 | populated | loading | `UX-<slug>` | `CAP-<AREA>-<slug>` | <!-- ... --> |

---

## 5. Evidence
<!-- Optional: the path or link of the project's own wireframe, mock-up or screenshot; the reviewer reads it when
present. Drop the section when there is none. -->
