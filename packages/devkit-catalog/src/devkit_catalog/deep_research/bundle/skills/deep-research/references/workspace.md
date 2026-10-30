# Allocate and promote research work

1. After the research question and bound are set, allocate a new run directory under `.devkit/transient/deep-research/`; use a collision-free name and do not reuse an existing run. Read an earlier run directory only when the user names it as an input source.
2. In a Git project, verify the exact chosen path is ignored and contains no tracked files before writing scratch content; report an ignore/tracking conflict and stop allocation rather than editing ignore rules, hiding files or changing location.
3. In a project without Git, report that ignore/index checks are unavailable; the run is still temporary project-owned scratch, not a durable artifact store.
4. Give each writing assignment its own absolute task directory inside the run; other task directories and retained product files are outside that write boundary.
5. Record the run question, input identities, assignments, stopping conditions and in-flight state in the run brief; keep role outputs, source notes and experiment files in their assigned directories.
6. Give a role scratch write permission only in its payload and effective contract; otherwise keep it read-only. Existing experiment permission is separate from scratch-note permission.
7. Compare actual changed paths and relevant source/index/HEAD state before accepting results; reject writes outside assigned boundaries without discarding another actor's state.
8. Before retaining results, select the useful synthesis, supporting evidence, experiment outcomes and important rejected alternatives; do not copy the whole run by default.
9. Copy or rewrite only those selected artifacts into the retained material under `docs/materials/` (`references/synthesis.md`); replace scratch-only links with retained evidence links or stable sources.
10. Check that retained files are understandable and their required evidence resolves without the transient directory; link each from the material's index.
11. Keep scratch pointers explicitly temporary when they help resume; a missing scratch file is missing evidence, not a verified result. Do not delete a run automatically or commit its scratch content.

Allocation uses ordinary filesystem tools, not a new registry or CLI. Where available, `mktemp -d` supplies
collision-free names. Resolve returned directories to absolute paths before passing them to roles.

Example after verifying the project path and ignore state:

```sh
mkdir -p .devkit/transient/deep-research
research_run="$(mktemp -d .devkit/transient/deep-research/run-XXXXXX)"
research_task="$(mktemp -d "$research_run/task-XXXXXX")"
```

Check the actual run/task paths in Git before placing files there; later task-specific ignore exceptions can
differ from the parent. If allocation is unavailable, report the gap and keep any permitted read-only inquiry
inline; do not claim a scratch-writing role ran. The coordinator owns allocation and promotion, while members
write only their assigned scratch notes or explicitly authorized experiments.
