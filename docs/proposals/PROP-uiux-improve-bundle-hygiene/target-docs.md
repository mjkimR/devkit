---
id: PROP-uiux-improve-bundle-hygiene-target
title: app-uiux-improve hygiene target documents
summary: "Maps the settled pilot instruction fixes to capability rules, use case examples, bundle assets and verifiable acceptance scenarios."
status: draft
created_at: 2026-11-13
targets:
  - file: docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
    status: modified
  - file: docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
    status: modified
---

# [PROP-uiux-improve-bundle-hygiene-target] Target documents and verification

Planning input: source HEAD `aa6c51dc3148efba121bc54c8e582a59aacd11d1`. The proposal changes instruction content,
not runtime behavior. No product screen is drafted.

## Living Spec changes

| Document | Retained change |
| --- | --- |
| `CAP-DLV-uiux-improvement` rule 4 | A task focus orders work; only user-stated constraints and explicit deferrals become non-goals. |
| `CAP-DLV-uiux-improvement` rule 11 | Inspect and verify the changed branch build; name mocked coverage; compute and report color contrast for key pairs when changing color. |
| `CAP-DLV-uiux-improvement` rule 16 | Carry brief precedence and absolute read-only paths for local-only context files. |
| `CAP-DLV-uiux-improvement` rule 17 | Accept a change only after checking both the permitted edit list and the approved goal scope. Report excluded changes without unsolicited reversion or deletion. |
| `CAP-DLV-uiux-improvement` rule 18 | Preserve consumer ownership and upstream retention guidance for context files. |
| `UC-improve-an-interface-and-user-flow` | Clarify steps 2 and 6 and extensions 2a and 6b; add acceptance examples for mocked branch verification, an in-list/out-of-scope change, focus versus constraint, and measured contrast. Preserve predecessor decisions on steps 1 and 5 and Impeccable routing. |

The capability's verification rule should state these obligations conditionally:

- When a branch build can run locally, inspect that build before and after the change. A deployed environment may
  supply a baseline; it does not verify the branch result.
- When a live backend is costly or shared, a repeatable mocked backend may drive the local branch build. The report
  names the mock, task, states, capture method and unavailable real-backend coverage. It never calls mocked coverage
  an end-to-end check.
- When changing color, compute contrast from the effective foreground and background colors with color-space
  conversion; account for opacity and compositing when present. Record each key pair, its states and numeric ratio,
  and compare with the consumer's applicable criteria. An estimate or an aesthetic judgment is not a measurement.

## Bundle edits

All paths below are under `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/`.

| Path | Instruction change |
| --- | --- |
| `skills/app-uiux-improve/SKILL.md` | Steps 1/5 retain focus as ordering; steps 2/8 name the changed local branch build and repeatable mocked checks; completion distinguishes measured checks and unavailable coverage. |
| `skills/app-uiux-improve/references/orchestration.md` | Brief states goal scope, only explicit non-goals, precedence over craft defaults and read-only absolute paths for local-only `PRODUCT.md`/`DESIGN.md`. Acceptance compares goal scope as well as the file list; reports out-of-scope changes without treating them as accepted. |
| `skills/app-uiux-improve/references/design-guidance.md` | Baseline craft checks require computed contrast and numeric ratios for key pairs during color work, with color-space conversion and effective composited colors. |
| `skills/app-uiux-improve/roles/designer.md` | For color work, return key foreground/background pairs, measured ratios and missing measurement coverage; suggestions remain read-only. |
| `skills/app-uiux-improve/roles/unconventional-designer.md` | Apply the same measured-color check when a proposed color change is in the assignment; retain the bounded read-only role. |
| `README.md` | Explain local branch/mock verification and scope-aware acceptance; replace the unconditional child-host limitation in Troubleshooting with a check that the plugin is enabled for the consumer project. Route details follow the routing predecessor; no plugin-cache file read is prescribed. |

If the session runs elsewhere, the coordinator passes absolute paths for untracked or excluded `PRODUCT.md` and
`DESIGN.md` as read-only sources. The report applies upstream retention guidance and does not commit, ignore,
remove or copy those files merely to make them visible. The consuming project's task settings choose its checkout.

## Acceptance and check mapping

Each automated check goes in `packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py`.
Use localized semantic assertions consistent with that file; do not require incidental sentence order.

| ID | Given / When / Then | Automated instruction assertion | Behavior verification |
| --- | --- | --- | --- |
| AC-H01 | Given a deployed baseline and an executable local branch build, when checking the change, then inspect the branch build before and after; if a mocked backend is used, label the result as mocked and name missing live coverage. | Add focused verification assertions for SKILL steps 2/8 and design guidance; preserve existing qualified-completion checks. | Walk through the same task and states in a local branch build with a repeatable mock; record capture method and limits. A live consumer run is not a Planning prerequisite. |
| AC-H02 | Given a focus such as color first, when writing the brief, then preserve it as ordering and add only user-stated constraints or explicit deferrals as non-goals. | Extend brief assertions with focus/constraint distinction. | Walk through color-first with a useful in-scope interaction refinement; check that no invented interaction prohibition appears. |
| AC-H03 | Given a craft default conflicting with the approved brief or consumer specification, when applying it, then follow the authorized source; if authorized sources conflict with each other, return that decision. | Extend brief assertions with explicit precedence and conflict handling. | Review a conflicting craft default against the supplied brief/specification. |
| AC-H04 | Given a listed file change outside the approved goal, when accepting a session return, then report it and exclude it from accepted work without unsolicited reversion or deletion. | Extend coordinator-acceptance assertions to require both edit-list and goal-scope checks. | Walk through an in-list dependency bump unrelated to the approved goal. |
| AC-H05 | Given color work, when inspecting or proposing key color pairs, then compute effective-color contrast with conversion and report numeric ratios and missing coverage. | Add assertions for design guidance and both designer roles covering computed contrast, conversion and ratio reporting. | Review one opaque and one translucent pair with the consumer's calculation tool; record effective colors, state, result and applicable criterion. Static text does not prove the math or model obedience. |
| AC-H06 | Given local-only context files and a session elsewhere, when briefing the session, then pass absolute read-only paths and preserve consumer ownership and retention choices. | Extend brief and project-file assertions for absolute paths, read-only use and unchanged retention authority. | Walk through an excluded context file and confirm no new copy/commit/ignore action is inferred. |
| AC-H07 | Given a plugin-load failure or workflow-neutral installation, when reading the guide and skill bodies, then check current-project enablement and prescribe no cache fallback or devkit-spec policy dependency. | Extend guide troubleshooting assertions and scan agent-read bodies for concrete policy syntax and workflow-specific commands, alongside the existing standalone-ID/SDD checks. | Review the guide against the predecessor's native-load-only route; test allowed generic words such as branch/worktree separately from forbidden policy syntax. |

Instruction assertions and document rules validate the authored contract. They do not establish model obedience,
native isolation, visual quality or real-user usability. Keep such limits in the Development report.

## Development verification

Run the focused integration test file after instruction edits, then the repository's required lint, type checks
and `just test-affected` with full fallback. Preserve the installed-consumer isolation test as coverage of rule 13;
run it when the affected-test selector includes it or a change touches installation behavior. No new test tier,
frontend, runtime dependency or feature edge is planned. Before editing bundle assets, load the authoring context
and apply `agent-asset-writing`; sync projected outputs if the selected source change requires them.

Refresh this mapping after the two predecessors land; verify rule references and scope against that input before
Development starts. This document gives no acceptance, handoff, commit, integration or publication authority.
