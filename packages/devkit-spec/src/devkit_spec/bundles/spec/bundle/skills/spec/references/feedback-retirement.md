# Feedback preservation before proposal deletion

Read before the Host deletes a proposal without handoff: rejected-proposal cleanup, decomposition, supersede, abandon or the session reclassification of a queued draft. A handoff carries the feedback itself.

1. Run `devkit rules check` on the proposal's `feedback/*.md`. Keep a file that fails or has an unknown status in place and report it; never assume it is settled.
2. Move each `status: open` file to `specs/<current-YYYY-MM>/feedback/<today-YYYYMMDD>-<name>.md`, keeping its ID, status and observation date; settled records stay in Git history. Check every destination path and ID first; on a collision keep the proposal. Never duplicate an observation across decomposed children.
3. In retained documents, turn historical mentions of the proposal, its PADRs and settled feedback into `~~strikethrough~~` references with the source Git revision, and fix relative links of moved files. If a live dependency on the proposal cannot stay valid, keep the proposal and report it.
4. Once `devkit rules check` passes on them, commit the moves and the deletion together; if a step fails, restore the earlier moves and keep the proposal.

Done when that commit exists and the cleanup report names the preservation paths.
