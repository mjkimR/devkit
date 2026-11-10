# Project documents

1. Use the project's existing document destinations and formats; when the docs bundle is selected, read `uv run devkit get-context docs` and the relevant writing instruction before authoring, and locate documents with `uv run devkit docs search|list|resolve|refs`.
2. If the project maintains no document tree, record that in current context and create no document system unprompted.
3. Before partitioning a multi-writer build, find the documents that govern the goal: structure or architecture, glossary or steering, capability or use-case contracts and decisions.
4. Pass them in each assignment as its governing documents, by ID or by absolute path where a document has no ID; pass `none` when no document governs the assignment.
5. Require each assignee to treat governing documents as constraints and to return a conflict with one to the Host instead of resolving it silently.
6. If a shared interface outlives its assignment, record it in its current-state document (architecture or capability), marked as agreed and awaiting implementation, before dependent concurrent writes; use that document's ID plus source identity as the interface identity, and remove the mark when its implementation is integrated.
7. If a shared interface is short-lived, keep it in the assignment.
8. When the Host integrates a retained result, update current-state documents where the subject warrants: retained behavior in a capability or use case, structure and boundaries in architecture, and a retained choice in a decision when its reason or reopening condition matters later.
9. Describe the current state, not iteration history; write nothing for a discarded experiment.
10. Delegate document writing as its own assignment only after the code it describes is integrated; supply exclusive document paths as write scope, the described source identity and governing document IDs, and name one owner per document.
11. Compare a returned document with the implementation at its described source identity; a document describing unimplemented behavior is a defect, unless it is a shared interface marked as agreed.
12. Include the project's document checks in combined checks when it defines them; report an unavailable document check as unverified.
13. In `.devkit/adaptive-dev.md`, map each retained behavior, structure or choice to its document ID, or to its path where the document has no ID; mark one without a document `undocumented`.
14. Link the document in that map, never copy its content; keep `undocumented` entries, because they show a later SDD adoption which retained items lack a document.
15. Add no per-change record, SDD Unit, approval or envelope for document work.

Example map: `shared list editing: CAP-<AREA>-<slug>`, `storage boundary: docs/architecture/storage.md`, `last-write-wins merge: undocumented`.
