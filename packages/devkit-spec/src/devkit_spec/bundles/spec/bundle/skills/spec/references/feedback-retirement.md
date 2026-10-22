# Feedback preservation before proposal deletion

Read before deleting a proposal without handoff: rejected-proposal hygiene, Backlog decomposition, supersede, abandon or the session reclassification of a queued draft. A normal handoff routes the feedback itself.

The Host owns this operation. A rejection starts no worker and keeps the feedback in the proposal until later cleanup. Draft branch guards, rejection ADR requirements and deletion authority still apply.

1. Inspect the proposal's direct `feedback/*.md` before deleting anything:
   - Validate readable frontmatter, the path-derived ID, a known status (`open|promoted|resolved|dismissed|forwarded`) and safe source and destination paths.
   - Keep invalid or unknown input in place and report it; never infer that it is settled.
   - Note the source Git revision and paths for context.
2. Plan each `status: open` file into `specs/<current-YYYY-MM>/feedback/<today-YYYYMMDD>-<name>.md`, preserving its ID, status and observation date. Settled records stay in Git history.
   - Check all destination paths and repository-wide IDs before any move; never overwrite a file or duplicate an observation across decomposed children.
   - On a conflict, leave the source proposal intact until it is resolved.
3. Inspect incoming references from retained feedback and other current documents to the retiring proposal, its PADRs and settled sibling feedback:
   - Convert only historical context or evidence mentions to `~~strikethrough~~` reference syntax, keeping the source Git revision and path.
   - Update relative context links for moved files; use stable Git-history references when the target is deleted.
   - Never turn a live dependency or target into a historical mention. When that dependency cannot remain valid, keep the proposal and report it.
4. Apply the preservation and the authorized proposal deletion in the same commit:
   - Inspect all planned moves before applying them. If a move fails, restore the earlier moves and keep the proposal.
   - Run `devkit rules check` on the retained files and the deletion before committing. If it fails, correct the cause or restore the source.
   - Never commit a dangling current reference or lose retrievable context.

Done when the commit passes `devkit rules check` and the cleanup report names the actual preservation paths.
