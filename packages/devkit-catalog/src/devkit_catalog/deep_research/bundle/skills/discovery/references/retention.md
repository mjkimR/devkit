# Retain a requested discovery result

1. Preserve the requested destination and format under project writing rules; use one indexed material when durable
   discovery evidence is requested without another format. Create no delivery Unit, approval or envelope.
2. Before writing, run `uv run devkit get-context docs` and apply relevant instructions; if unavailable, report the
   blocked write and keep the result in conversation.
3. For any destination, retain useful proposals, decisions, reasons, sources/limits, assumptions, outcome and next
   route proportionately; require no fixed sections and leave no necessary input only in transient scratch.
4. Inspect the result and report its actual path or blocked write; write no implementation, settings, commit or publication.

## Indexed materials

1. For a new material, run `uv run devkit docs resolve MAT-<slug>` and check
   `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/` is absent. `DOCS_ID_UNRESOLVED` establishes the missing ID;
   another lookup error leaves verification incomplete. Choose another slug if the ID or directory exists.
2. Create `<YYYYMMDD>-<slug>.md` there with frontmatter `id: MAT-<slug>` and `created_at`, H1
   `# [MAT-<slug>] <title>` and relative links to any retained supporting notes.
3. End with `Status: complete` or `Status: partial` for investigation coverage, separately from the discovery outcome.
   A rejected idea can have complete evidence.
4. Resume only a user-named partial material from the same inquiry in place; never rewrite a complete material.
   A later inquiry creates a new material citing it.
5. Report the path, ID and coverage status; leave it uncommitted and tell the owner to commit it through project
   Git policy before downstream documents cite its ID.
