# devkit harness in this repository

- Configure rules and gates in `[rules]` and `[gates]` of `.devkit/config.toml`;
  `devkit rules check` loads the synchronized rules without flags.
- Snapshot gates (`devkit rules check --staged`, `--ci`) read a managed rule only
  when it matches the committed `.devkit/installation.json`; commit the receipt
  with every change that synchronized a rule.
