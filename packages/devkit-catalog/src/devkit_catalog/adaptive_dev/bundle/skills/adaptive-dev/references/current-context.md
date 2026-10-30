# Current facts, resume and voluntary adoption

1. Before resuming, read project-owned `.devkit/adaptive-dev.md` if it exists and check its next action against the current files and source/artifact identity.
2. If it is absent or stale, recover current facts from the implementation, run instructions and the user; do not reconstruct discarded experiments or the whole conversation.
3. Create or update it from `.devkit/managed/adaptive-dev/templates/current-context.md` (read the template, never execute it); never overwrite existing project content wholesale, and record references instead of secrets or PII.
4. Record the goal, users, constraints and representative flow, keeping retained user decisions, implementation choices and assumptions needing evidence apart; then setup/run/check instructions, observed results with their source/artifact identity, limitations, open questions and the next useful action.
5. Remove superseded choices and experiments that no longer inform the product; keep an uncertainty while it affects the next action. Retain research-note links, useful surviving alternatives and conditions that would reopen a choice when they inform the next decision; link a retained research material by its `MAT-<slug>` ID, never a copy of it.
6. Before pausing or handing off, update changed resume facts and explain unverified evidence.
7. On an explicit SDD adoption request, explain preparing the spec package/assets while the effective approach stays adaptive-dev. Once the `sdd-baseline` playbook in `spec:core` is available and invoked or confirmed, route the retained current facts to it; it owns readiness, exact activation effects and recovery.
8. Never activate SDD from this skill, infer graduation from size, time or experiment count, or reconstruct earlier delivery records; existing documents, context or the spec package are no activation decision.
