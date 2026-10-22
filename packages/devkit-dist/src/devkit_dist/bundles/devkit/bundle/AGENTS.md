# devkit in this repository

## Contracts

1. **Load context once per bundle.** Before using a bundle's assets, run
   `uv run devkit get-context <bundle>` once per agent context; it returns this
   constitution and the instruction headers with paths. Read an instruction body
   only when its header matches the work, and reload only after the context was lost.
2. **Never edit generated copies.** `devkit sync` regenerates `.devkit/managed/`
   and the projections under `.claude/`, `.agents/` and `.codex/`, and refuses
   to run over a modified managed file. Change the source bundle, or run
   `devkit override create <bundle>:<asset>`.
3. **Selection lives in `.devkit/config.toml`.** Installing a package only makes
   its bundle available. Select a bundle with `devkit add <bundle>[:<preset>]`,
   which also syncs, and deselect it with `devkit remove <bundle>`. Bundles that
   declare `auto_select` are selected by default (`devkit list` shows them);
   `<bundle> = false` under `[presets]` opts one out.
4. **Playbooks are explicit.** Search playbooks only when the user invokes the
   `devkit-playbook` skill for the current task, or when a failing rule's
   remediation names a playbook.
5. **Commit the receipt with the change.** After `devkit sync`, commit the
   receipt `.devkit/installation.json` with the change that required it.
