# Post-handoff link check

Run after `devkit spec proposal handoff <slug>`, after following each warning's `[FIX]`. The plain handoff commits
nothing: commit these fixes with its writes. The composed handoff (`--effort`, `accept --mode accept_and_handoff`)
already committed its transaction (`commit=`): when it reports unresolved links or rewritten references
(`SPEC_PROPOSAL_LINK_UNRESOLVED`, `SPEC_PROPOSAL_REFS_REWRITTEN`; JSON `handoff.unresolved`, `handoff.rewritten`)
outside the new spec and promoted ADRs, commit these fixes on `dev-<slug>` as a later Host commit before a worker
starts.

1. Fix each `[UNRESOLVED_LINK]`: point it at the new spec or promoted ADR by full ID (`` `SPEC-<slug>` ``,
   `` `ADR-<slug>` ``), or drop it.
2. Fix by hand the links handoff does not rewrite (reference-style links, links in fenced code) until
   `rg -n "\]\([^)]*(PROP-<slug>/|\.\./proposal\.md)" docs specs` returns nothing.
3. Reread each `[REWRITTEN: ... kind=id]` line outside the new spec and promoted ADRs; where it meant the proposal as
   an origin, reword it to stay true ("split off from the original proposal of `SPEC-x`").
4. `devkit rules check` passes.

## Sibling drafts

The handoff also rewrites a sibling draft's `depends_on` and ID references to the handed-off proposal, even when the
sibling is in its own Planning: a skipped `depends_on` would dangle once `dev-<slug>` lands. When the sibling's
Planning merges into the base first, merging the base into `dev-<slug>` conflicts in
`docs/proposals/PROP-<other>/`. Take the base version of each conflicting file
(`git checkout --theirs -- <path>` while merging the base), run `devkit rules fix <path>`, which rewrites each
citation the reference rule reports as `PROP-<slug> was handed off` to `SPEC-<slug>`, and commit the merge.
