# Document System

Use devkit documents with the project's selected development approach. Document formats do not impose a delivery lifecycle.

- Read this context once before document work and read each relevant instruction before its action.
- `docs/` describes current behavior, structure and choices. Keep it aligned with the implementation being retained.
- Refer to ID-bearing documents by full ID (`devkit docs resolve <ID>`, `devkit docs refs <ID>`).
- `docs/steering/` holds project-wide background; `devkit get-context docs` lists each file's title and summary under `documents`. Read a file's body before a wording, naming, interface or content decision its summary covers.
- Read the glossary before naming a domain concept. Use `devkit docs list` and `devkit docs search` to find existing documents before writing another.
- Apply document identity, frontmatter, structure and reference checks through `devkit rules check`.
- The selected development approach defines approvals, change records, decision revision and artifact retention.
- Templates: `.devkit/managed/docs/templates/{capability,usecase,ux,decision,milestone}.md`.
- Change managed assets through `devkit override` or their source bundle; never edit `.devkit/managed/` directly.
