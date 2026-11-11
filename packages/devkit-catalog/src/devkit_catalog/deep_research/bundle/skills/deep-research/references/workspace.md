# Allocate and promote research work

1. After the question and bound are set, allocate a new run directory under `.devkit/transient/deep-research/` with a collision-free name (`mktemp -d`, example below); never reuse an existing run. Read an earlier run only when the user names it as an input source.
2. In a Git project, verify the exact run and task paths are ignored and contain no tracked files before writing scratch content (a task-specific ignore exception can differ from the parent); on an ignore/tracking conflict, report it and stop allocation instead of editing ignore rules, hiding files or changing location.
3. Without Git, report that ignore/index checks are unavailable; the run is still temporary project-owned scratch, not a durable artifact store.
4. Give each writing assignment its own task directory inside the run, resolved to an absolute path before passing it to the role; other task directories and retained product files are outside its write boundary.
5. Record the run question, input identities, assignments, stopping conditions and in-flight state in the run brief; keep role outputs, source notes and experiment files in their assigned directories.
6. Keep optional cloud request/report scratch in this run; before pausing, preserve the exact safe request and required return evidence in the partial material, not only a scratch pointer.
7. Grant a role scratch write permission only in its payload and effective contract; otherwise keep it read-only. Experiment permission is separate from scratch-note permission.
8. Before accepting results, compare actual changed paths and relevant source/index/HEAD state; reject writes outside assigned boundaries without discarding another actor's state.
9. Before retaining, select the useful synthesis, supporting evidence, experiment outcomes and important rejected alternatives, not the whole run; copy or rewrite only those into the retained material under `docs/materials/` (`references/synthesis.md`) and replace scratch-only links with retained evidence links or stable sources.
10. Check that retained files are understandable, linked from the material's index and resolve their required evidence without the transient directory.
11. Mark scratch pointers kept for resuming as temporary; a missing scratch file is missing evidence, not a verified result. Never delete a run automatically or commit its scratch content.
12. If allocation is unavailable, report the gap and keep any permitted read-only inquiry inline; do not claim a scratch-writing role ran.

Allocate with ordinary filesystem tools, not a registry or CLI. The coordinator owns allocation and promotion;
members write only their assigned scratch notes or explicitly authorized experiments.

Example after verifying the project path and ignore state:

```sh
mkdir -p .devkit/transient/deep-research
research_run="$(mktemp -d .devkit/transient/deep-research/run-XXXXXX)"
research_task="$(mktemp -d "$research_run/task-XXXXXX")"
```
