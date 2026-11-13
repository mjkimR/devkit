# Retain a requested discovery result

1. Preserve the requested destination and format under project writing rules; default to one indexed material when
   the owner requests durable discovery evidence without another format. Create no delivery Unit, approval or envelope.
2. Before document work, run `uv run devkit get-context docs` and apply relevant writing instructions. If that
   capability is unavailable, report the blocked retention and keep the result in conversation.
3. For a new material, verify `uv run devkit docs resolve MAT-<slug>` finds no document and
   `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/` is absent; if either identity exists, choose another slug.
   Treat a failed lookup as missing verification rather than permission to overwrite.
4. Create `<YYYYMMDD>-<slug>.md` in that directory with frontmatter `id: MAT-<slug>` and `created_at`, and H1
   `# [MAT-<slug>] <title>`; link any useful retained notes relatively from this index.
5. Preserve the problem and use scene, actual decisions, compared proposals, recommendation, sources and limits,
   assumptions, discovery outcome, unresolved question and next route proportionately; require no fixed sections.
6. End the material with `Status: complete` or `Status: partial`; this records investigation coverage separately
   from the discovery outcome. A rejected idea can have complete evidence; validation-needed can have partial evidence.
7. Resume only a user-named partial material from the same inquiry by updating its index in place; never rewrite a
   complete material. A later inquiry creates a new material citing the earlier one.
8. Retain only useful synthesis and necessary evidence; resolve links without transient-only required inputs.
9. Inspect the written result and report its path, ID, coverage status and discovery outcome; leave it uncommitted.
   Tell the owner to commit it through project Git policy before a downstream document cites its material ID.

A destination request grants only the result write, not implementation, settings changes, staging, commit or publication.
