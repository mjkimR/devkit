# Source feedback

Read when the agreed work addresses named feedback (FB IDs), at entry and again before reporting completion.

Only `open` feedback is actionable. `promoted`, `resolved`, `dismissed` and `forwarded` are terminal: their references stay as traceability and need no disposition, re-verification or edit.

## At entry

- Record the full FB IDs and the intended scope in a `Source feedback` section of the proposal or spec body; a session keeps them in the agreed conversational scope. Handoff carries the section and never resolves it.
- Before planning boundaries, resolve open direct-fix sources to actual files and include the paths needing completion updates in delegated write scope.
- Do not infer sources from a matching target alone.

## At completion

Review only the explicitly linked open sources the task addresses directly, against the final diff and verification. Record outcomes in `reconcile.md` at `living-spec-draft` for a spec, or at `report-session` before the commit for a session (no new artifact). This applies even with requested-only capture or `collect-feedback` off.

- Set `resolved` only when the authorized implementation fully addresses the source and tests or review verify it. Append a Disposition naming the SPEC ID (or changed session paths), the outcome and the verification evidence.
- Keep partial, deferred or unverified fixes open and report the remaining scope and destination; required work in the agreed scope cannot be deferred to claim completion.
- Never convert `promoted` to `resolved`, and never resolve unrelated feedback a sweep found.
- Handoff, planning, document checks or integration alone are not fix verification.
- If later changes invalidate the evidence of a resolution this task made, set the source back to `open` and explain the remaining work.
- The Host handles a disposition outside a delegated write boundary.
