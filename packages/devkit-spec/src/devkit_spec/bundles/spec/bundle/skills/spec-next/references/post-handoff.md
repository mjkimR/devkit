# Post-handoff link check

Run this in the same change as `devkit spec proposal handoff <slug>`.

The handoff already did the following and reported each change as a `[REWRITTEN]`, `[DROPPED_RECORD]` or
`[CARRIED_GATE]` line; do not redo it:

- Moved the proposal into `specs/` and promoted PADRs to ADRs.
- Moved `materials/` and settled feedback to `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/`, and open feedback to the
  new spec's `feedback/`.
- Dropped the proposal's envelopes and workflow records, because Planning sweeps do not satisfy Development's own;
  carried `gate:plan-intent` and `gate:plan-accept`.
- Rewrote links, IDs and bundle-relative code-span paths under `docs/` and `specs/` (completed specs aside).

Follow the `[FIX]` of any warning; `SPEC_PROPOSAL_GATE_NOT_CARRIED` names the answer command. Then
`devkit workflow next --unit <spec dir>` shows pending checks and any gates still needing authority under their
effective policies.

1. Fix every `[UNRESOLVED_LINK]` line: point it at the new spec or the promoted ADR by full ID (`` `SPEC-<slug>` ``,
   `` `ADR-<slug>` ``), or drop it. Typical cases:
   - `reason=unmapped`: a link to a PADR that was not promoted, into a `materials/` dir that was not moved (empty, or
     junk only), or to `decisions/` itself;
   - `reason=ambiguous`: an ID several documents declare.
2. Search for Markdown links to the deleted bundle, including the relocated feedback files, and confirm none is left.
   Prose mentions of the old path need no change. Reference-style links and links inside fenced code blocks are not
   rewritten; fix those by hand if they were real references:
   ```bash
   rg -n "\]\([^)]*(PROP-<slug>/|\.\./proposal\.md)" docs specs
   ```
3. Reread every `[REWRITTEN: ... kind=id]` line outside the new spec and the promoted ADRs (the
   `SPEC_PROPOSAL_REFS_REWRITTEN` notice lists them). If a reference meant the proposal as an origin ("split off from
   `PROP-x`"), it now names the spec; reword the sentence so it stays true, for example "split off from the original
   proposal of `SPEC-x`".
4. Run `devkit rules check` and confirm `RULE-markdown-link` and `RULE-document-reference` pass.

If another branch adds a `PROP-<slug>` reference later, `devkit rules fix` (`RULE-document-reference`) rewrites it.
