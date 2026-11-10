# Optional design perspectives

Read before delegating. Resolve paths from the directory containing the invoked `SKILL.md`, not the working
directory or this reference. If its location is unavailable, locate and verify the invoked skill first.
Verify the selected role file exists and pass its resolved absolute path to a general subagent with the directive
to read that file before acting. Do not load every role into the coordinator.

## Select assignments

| Local role | Useful assignment |
| --- | --- |
| `roles/designer.md` | Improve a concrete task flow, hierarchy or interaction state. |
| `roles/unconventional-designer.md` | Explore a different interaction or composition mechanism serving the same goal. |
| `roles/reference-researcher.md` | Find a precedent or evidence that changes a design choice. |
| `roles/critic.md` | Find consequential breakdowns or unnecessary burdens in supplied artifacts or a proposed direction. |

Prefer the smallest useful assignment. Research and criticism can be skipped; a critic can return zero findings.
Use separate instances only when their questions or design premises differ. Do not require a role count or debate.

## Dispatch and receive

1. Give the child the user goal, relevant artifacts, hard constraints, open preferences, one concrete assignment,
   allowed reads/actions, an observable stop condition and its expected return. Include the absolute local role path.
   Pass task-relevant facts instead of the coordinator's full conversation.
2. Where supported, use a fresh context without parent conversation inheritance. If fresh children are unavailable,
   perform useful passes inline and disclose that they were not independent contexts. Preserve host restrictions;
   a role prompt supplies no enforcement guarantee or access permission.
3. Keep peer conclusions out of independent first-pass payloads. After returns arrive, provide only the material
   a selected refinement or critic needs. Do not wait for consensus before making an in-scope design choice.
4. Let roles return suggestions, sketches or evidence; keep product source edits with the coordinator through
   the existing workflow. Roles leave the index and HEAD unchanged and do not write retained artifacts.
5. Validate that a return identifies its inspected artifacts, actual work, assumptions, limitations and any failed
   or unavailable action. A failed or missing role contributes no findings; continue inline when useful and report
   missing coverage. Reinvoke only after the input or cause changes.
6. Check consequential claims or conflicts selectively. Do not repeat a well-supported investigation in full.
   Distinguish inspected evidence from analogy, taste and assumptions before synthesis.
7. Keep one useful critique/refinement pass as the default. Stop when the requested outcome and applicable checks
   are satisfied; do not iterate to prove benefit, fill an issue quota or reach agreement.

Example assignment:

```text
Read <absolute-skill-directory>/roles/unconventional-designer.md first.
Goal: make conflicts in a mobile calendar understandable and recoverable.
Artifacts: supplied conflict states; preserve attendees and event details.
Assignment: explore a decision-inbox flow instead of a calendar-grid interaction.
Actions: read the supplied artifacts; return suggestions only, no source or retained-file edits.
Stop: return one concrete task sequence, affected states, expected benefit, tradeoff and weakest assumption.
```

The example is illustrative. Assign a different mechanism only when it can serve the actual user task.
