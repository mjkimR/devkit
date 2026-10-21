# Post-handoff link check

Read this immediately after every `devkit spec proposal handoff <slug>`, and run it in the same change.

The handoff moves the proposal into `specs/`, promotes PADRs to ADRs, moves `materials/` and settled feedback to `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/`, moves open feedback to the new spec's `feedback/`, drops the proposal's envelopes and other workflow records (Planning sweeps do not satisfy Development's own), carries `gate:plan-intent` and `gate:plan-accept`, and rewrites links, IDs and bundle-relative code-span paths under `docs/` and `specs/` (completed specs aside). It reports each change as a `[REWRITTEN]`, `[DROPPED_RECORD]` or `[CARRIED_GATE]` line; follow the `[FIX]` of any warning (`SPEC_PROPOSAL_GATE_NOT_CARRIED` names the answer command). `devkit workflow next --unit <spec dir>` then shows pending checks and any gates still needing authority under their effective policies.

1. Fix every `[UNRESOLVED_LINK]` line. Typical cases: `reason=unmapped` for a link to a PADR that was not promoted, into a `materials/` dir that was not moved (empty, or junk only) or to `decisions/` itself; `reason=ambiguous` for an ID several documents declare. Point it at the new spec or the promoted ADR by full ID (`` `SPEC-<slug>` ``, `` `ADR-<slug>` ``), or drop it.
2. Confirm nothing is left by searching for Markdown links to the deleted bundle, including the relocated feedback files (prose mentions of the old path need no change). Reference-style links and links inside fenced code blocks are not rewritten; fix those by hand if they were real references:
   ```bash
   rg -n "\]\([^)]*(PROP-<slug>/|\.\./proposal\.md)" docs specs
   ```
3. Reread every `[REWRITTEN: ... kind=id]` line outside the new spec and the promoted ADRs (the `SPEC_PROPOSAL_REFS_REWRITTEN` notice lists them). A reference that meant the proposal as an origin ("split off from `PROP-x`") now names the spec; reword the sentence so it stays true, for example "split off from the original proposal of `SPEC-x`".
4. Run `devkit rules check` and confirm `RULE-markdown-link` and `RULE-document-reference` pass.

`PROP-<slug>` references added later on another branch are fixed by `devkit rules fix` (`RULE-document-reference`).
