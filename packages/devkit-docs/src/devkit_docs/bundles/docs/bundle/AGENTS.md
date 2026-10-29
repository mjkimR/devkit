# Document System

Document formats impose no delivery lifecycle: the project's development approach defines approvals, change
records, decision revision and artifact retention.

- Read this context once before document work, and each relevant instruction before its action.
- `docs/` describes current behavior, structure and choices; keep it aligned with the implementation being retained.
- Refer to ID-bearing documents by full ID (`devkit docs resolve <ID>`, `devkit docs refs <ID>`).
- `docs/steering/` holds project-wide background; `devkit get-context docs` lists each file's title and summary under `documents`. Read a file's body before a wording, naming, interface or content decision its summary covers.
- Read the glossary before naming a domain concept; find existing documents with `devkit docs list` and `devkit docs search` before writing another.
- Run `devkit rules check` for document identity, frontmatter, structure and reference checks.
- Templates: `.devkit/managed/docs/templates/{capability,usecase,ux,decision,milestone}.md`.
- Change managed assets through `devkit override` or their source bundle, never by editing `.devkit/managed/`.
