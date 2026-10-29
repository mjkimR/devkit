# Playbooks found at intake

Read this only on a match, after intake discovery (`spec` skill, routing step 1) selected a candidate; the trigger,
skip cases, search and selection rule stay in the skill.

## 1. Offer and confirmation

- Name the candidate as `<bundle>/<playbook>` with what it does, in one line next to the classification statement:
  "Playbook `spec/adr-compaction` consolidates ADRs; confirm to use it, or decline to continue as ordinary work."
- The confirmation grants what an explicit invocation grants, no more: workflow gates, permissions and user
  constraints still apply; confirming `spec/adr-compaction` authorizes its deletions at `session` depth.

## 2. Classification and records

- Classify with the confirmed playbook's stated depth and scope: a playbook that runs at `session` depth needs no
  Unit, and a Unit or a proposal under review is never lowered for it.
- When the task continues to a Unit or proposal, record the playbook ID in the `plan-intent` note and the Unit's or
  proposal's records, so a worker that skips discovery still follows it. Records name the ID, never the conversation.

## 3. Use the playbook

1. Run `devkit get-context <bundle>` for the playbook's bundle unless already loaded in this agent context.
2. Read the selected playbook body at the path the search returned, or with `devkit playbook get <bundle>/<playbook>`;
   read linked resources only when a step needs them.
3. Check its prerequisites: a failed one stops the playbook and is reported; the task continues as ordinary work only
   on the user's decision.
4. Follow the procedure through its completion conditions with fresh progress. A step inside it runs no nested
   playbook search.
