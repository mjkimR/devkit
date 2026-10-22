# Post-handoff link check

Run in the same change as `devkit spec proposal handoff <slug>`, after following the `[FIX]` of each warning.

1. Fix each `[UNRESOLVED_LINK]`: point it at the new spec or promoted ADR by full ID (`` `SPEC-<slug>` ``,
   `` `ADR-<slug>` ``), or drop it.
2. Fix by hand the links handoff does not rewrite (reference-style links, links in fenced code):
   `rg -n "\]\([^)]*(PROP-<slug>/|\.\./proposal\.md)" docs specs` returns nothing.
3. Reread each `[REWRITTEN: ... kind=id]` line outside the new spec and promoted ADRs. Where the reference meant the
   proposal as an origin, reword it to stay true ("split off from the original proposal of `SPEC-x`").
4. `devkit rules check` passes.
