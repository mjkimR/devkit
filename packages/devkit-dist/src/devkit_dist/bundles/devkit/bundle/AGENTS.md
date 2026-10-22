# devkit in this repository

- Read an instruction body only when its header matches the work.
- Search playbooks only when the user invokes `devkit-playbook` for the current
  task or a failing rule's remediation names one.
- Select bundles with `devkit add <bundle>[:<preset>]` and `devkit remove <bundle>`;
  installing a package only makes its bundle available.
- After `devkit sync`, commit `.devkit/installation.json` with the change that
  required it.
