# Impeccable capability and output limits

Use this guidance only on the user-selected Impeccable track. Keep the selected task route, native skill loading,
every-answer confirmation, host permissions, context-file ownership and recorded-base acceptance unchanged.
These instructions mitigate local handling; they fix no upstream runtime behavior and grant no additional authority.

## Prepare the brief

1. Add actual observed capabilities to the brief: native loading, same-child continuation, required nested roles,
   UI/command tools and access or approval limits. Mark unavailable or unverified capabilities explicitly.
2. Name stop conditions for an unavailable required capability or probe, an upstream question, a scope conflict or a
   denied operation. Require the return to state what ran, what stopped, findings and missing coverage.
3. Treat the brief as task boundaries, never as a passed upstream check or permission to override one.

## Negative visual detection

1. If `impeccable context` reports `hasVisualImplementation=false`, treat the detector result as advisory; it does
   not establish that the target has no UI.
2. Inspect the actual target path and UI code; inspect its local branch build when executable. Use the consumer's
   read-only framing sources as context, not as proof that a running interface was checked.
3. Report the detector result separately from inspected evidence and unavailable coverage. Do not promise that
   `--target` corrects detection or guarantees discovery; name a target path for scope, not as a detection fix.

## Unavailable autonomy probe

1. If `AUTONOMY_DIRECTIVE_CHECK` requires a live probe the child cannot run, report that unavailable probe and stop
   dependent Impeccable work. Do not claim the check passed or substitute brief stop conditions for the upstream
   requirement.
2. Hand the brief and blocker to a session the user operates. Continue inline only when already authorized or the
   user chooses it, describing that work as coordinator work without claiming Impeccable or its required probe ran.
3. Preserve native loading and every-answer confirmation on their applicable routes; change no sandbox, approval
   setting or tool permission to satisfy the probe. Return partial execution against the recorded base before any
   continuation, without blind replay or unsolicited reversion.

## Unsupported audit persistence

1. Before attempting audit persistence, inspect the installed version's supported help or exposed interface; use
   only a supported operation within the existing file and host permissions.
2. If `audit-storage write` is unsupported, do not invent or retry that command or a guessed replacement. Return
   audit findings and coverage in the session report and state that persistence was unavailable.
3. Create no fallback files or installation changes without the user's request and required permissions. An audit
   report does not grant context-file write, commit, ignore or removal authority.

## Completion

Return inspected evidence, actual capabilities and commands, audit findings, unavailable checks and persistence,
partial changes and blockers. Distinguish local mitigation from upstream behavior; claim no detector correction,
passed unavailable probe or persisted result without evidence.
