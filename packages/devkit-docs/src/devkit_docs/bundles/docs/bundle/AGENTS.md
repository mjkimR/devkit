# Document System

Document formats impose no delivery lifecycle: the project's selected development approach defines approvals, change
records, decision revision and artifact retention.

- Read this context once before document work and read each relevant instruction before its action.
- `docs/` describes current behavior, structure and choices. Keep it aligned with the implementation being retained.
- Refer to ID-bearing documents by full ID (`devkit docs resolve <ID>`, `devkit docs refs <ID>`).
- `docs/steering/` holds project-wide background; `devkit get-context docs` lists each file's title and summary under `documents`. Read a file's body before a wording, naming, interface or content decision its summary covers.
- Read the glossary before naming a domain concept. Find existing documents with `devkit docs list` and `devkit docs search` before writing another.
- Apply document identity, frontmatter, structure and reference checks through `devkit rules check`.
- Templates: `.devkit/managed/docs/templates/{capability,usecase,ux,decision,milestone}.md`.
- Change managed assets through `devkit override` or their source bundle; never edit `.devkit/managed/` directly.
