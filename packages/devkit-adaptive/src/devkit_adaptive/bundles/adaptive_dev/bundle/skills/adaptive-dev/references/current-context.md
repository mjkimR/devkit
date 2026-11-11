# Current facts, resume and voluntary adoption

1. Before resuming, read project-owned `.devkit/adaptive-dev.md` if it exists and check its next action against the current files and source/artifact identity.
2. If it is absent or stale, recover current facts from the implementation, run instructions and the user, not by reconstructing discarded experiments or the conversation.
3. Create or update it from `.devkit/managed/adaptive-dev/templates/current-context.md` (read it, never execute it): fill each template section, never overwrite existing project content wholesale, and record references instead of secrets or PII.
4. Remove superseded choices and experiments that no longer inform the product; keep an uncertainty, research-note link, surviving alternative or reopening condition while it informs the next decision. Link a retained research material by its `MAT-<slug>` ID, never a copy.
5. Before pausing or handing off, the Host updates changed resume facts even when checks fail (source identity, retained commits, dirty/unmerged worktrees, active ownership, failed checks, next recovery action) and collects or stops children, preserving their results before cleanup.
6. While a failed approach affects the next action, keep its reason, source identity, owner, surviving hypothesis, retry condition and next recovery action; recheck them on resume.
7. On an explicit SDD adoption request, explain preparing the spec package/assets while the effective approach stays adaptive-dev. Once the `sdd-baseline` playbook in `spec:core` is available and invoked or confirmed, route the retained current facts to it; it owns readiness, exact activation effects and recovery.
8. Never activate SDD from this skill, infer graduation from size, time or experiment count, or reconstruct earlier delivery records; existing documents, context or the spec package are no activation decision.

On resume, run `uv run devkit adaptive assignment list` beside reading current context.
In a new context every `open` assignment is interrupted; no earlier agent still runs.
For each ID inspect `worktree_state`, `commits`, `dirty` and `attention`, read its goal, stop condition, commit grant, governing documents and checks with `uv run devkit adaptive assignment show <id>`, then record a return from retained state, dispatch it again or close it as abandoned.
Before pausing, name outstanding assignment IDs and next recovery actions in current context; the ledger holds their scope, base and checks.
An ID absent from the ledger is stale context.
