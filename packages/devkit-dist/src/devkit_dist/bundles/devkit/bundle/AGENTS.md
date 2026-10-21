# devkit in this repository

devkit installs agent assets from versioned bundles. `.devkit/config.toml`
selects them; the receipt `.devkit/installation.json` records what was deployed.

## Contracts

1. **Load context once per bundle.** Run `uv run devkit get-context <bundle>`
   once per agent context before using a bundle's assets; it returns this
   constitution and the instruction headers with paths. Read a body only when
   its header matches the work; reload only after the context was lost.
2. **Never edit generated copies.** `devkit sync` regenerates `.devkit/managed/`
   and the projections under `.claude/`, `.agents/` and `.codex/`, and refuses
   to run over a modified managed file. Change the source bundle, or run
   `devkit override create <bundle>:<asset>`.
3. **Selection lives in `.devkit/config.toml`.** Installing a package only makes
   its bundle available; `devkit add <bundle>[:<preset>]` selects it and syncs,
   `devkit remove <bundle>` deselects. Bundles that declare `auto_select` are
   selected by default (`devkit list` shows them); `<bundle> = false` under
   `[presets]` opts out.
4. **Playbooks are explicit.** Ordinary tasks never search playbooks. Search
   only when the user invokes the `devkit-playbook` skill for the current task,
   or when a failing rule's remediation names a playbook.
5. **Commit the receipt with the change.** After `devkit sync`, commit
   `.devkit/installation.json` with the change that required it.
