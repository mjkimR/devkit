# Project documents

1. Keep the project's existing document destinations and formats; read `uv run devkit get-context docs` and the relevant writing instruction before authoring, and locate documents with `uv run devkit docs search|list|resolve|refs`. If the project opted out of the docs bundle, follow its own document conventions.
2. If the project has no document yet, record that in current context and seed no document tree; write the first document only when a retained subject warrants one, in the document system's kind and destination.
3. Before partitioning a multi-writer build, find the documents that govern the goal: structure or architecture, glossary or steering, capability or use-case contracts and decisions.
4. Pass them as each assignment's governing documents, by ID or by absolute path where a document has no ID, or `none`; pass the same values as `--governing` when recording the assignment.
5. Require each assignee to treat governing documents as constraints and return a conflict with one to the Host instead of resolving it silently.
6. If a shared interface outlives its assignment, record it in its current-state document (architecture or capability), marked agreed and awaiting implementation, before dependent concurrent writes; its interface identity is that document's ID plus source identity. Remove the mark once the implementation is integrated. If a shared interface is short-lived, keep it in the assignment.
7. When the Host integrates a retained result, update current-state documents where the subject warrants: retained behavior in a capability or use case, structure and boundaries in architecture, and a retained choice in a decision when its reason or reopening condition matters later.
8. Describe the current state, not iteration history; write nothing for a discarded experiment.
9. Delegate document writing as its own assignment only after the code it describes is integrated, with exclusive document paths as write scope, the described source identity, governing document IDs and one owner per document.
10. Compare a returned document with the implementation at its described source identity; a document describing unimplemented behavior is a defect unless it is a shared interface marked agreed.
11. Include `uv run devkit rules check` on changed documents, plus any document checks the project defines, in combined checks; report a check that could not run as unverified.
12. In `.devkit/adaptive-dev.md`, map each retained behavior, structure or choice to its document ID, or its path where it has no ID, or mark it `undocumented`. Link the document, never copy its content; keep `undocumented` entries, since they show a later SDD adoption which retained items lack a document.
13. Add no per-change record, SDD Unit, approval or envelope for document work.

Example map: `shared list editing: CAP-<AREA>-<slug>`, `storage boundary: docs/architecture/storage.md`, `last-write-wins merge: undocumented`.
