# Feedback preservation before proposal deletion

Read before deleting a proposal without handoff: rejected-proposal hygiene, Backlog decomposition, supersede or abandon.
The Host owns this operation; a rejection starts no worker and retains feedback in the proposal until later cleanup.
A normal handoff routes the feedback itself.

1. Inspect direct `feedback/*.md` before deleting anything. Validate readable frontmatter, path-derived ID,
   known status (`open|promoted|dismissed|forwarded`), and safe source/destination paths. Keep invalid or unknown
   input in place and report it; never infer that it is settled. Preserve the source Git revision and paths for context.
2. Plan each `status: open` file into `specs/<current-YYYY-MM>/feedback/<today-YYYYMMDD>-<name>.md`, preserving its
   ID, status and observation date. Settled records remain in Git history. Check all destination paths and
   repository-wide IDs before moves; never overwrite or duplicate an observation across decomposed children. A
   conflict leaves the source proposal intact until resolved.
3. Inspect incoming references from retained feedback and other current documents to the retiring proposal, PADRs and
   settled sibling feedback. Convert only historical context/evidence mentions to `~~strikethrough~~` reference
   syntax, retaining the source Git revision/path. Update relative context links for moved files, using stable
   Git-history references when the target is deleted. Never turn a live dependency/target into a historical mention:
   keep the proposal and report it when that dependency cannot remain valid.
4. Apply preservation and the authorized proposal deletion in the same commit. Inspect all planned moves before
   applying them; if a move fails, restore any earlier moves and keep the proposal. Run `devkit rules check` on
   retained files and the deletion before committing. If validation fails, correct it or restore the source; never
   commit a dangling current reference or lose retrievable context. Draft branch guards, rejection ADR requirements
   and deletion authority still apply.

Record the actual preservation paths in the cleanup report.
