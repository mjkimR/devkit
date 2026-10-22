# devkit harness in this repository

## Contracts

1. **Rules and gates run as code.** `devkit rules check` loads the synchronized
   rules without flags, and `devkit gate` runs the synchronized gates at commit
   time. Configure them in `[rules]` and `[gates]` of `.devkit/config.toml`, not
   by editing the managed copies.
2. **Snapshot gates trust the committed receipt.** When a change synchronized a
   rule, commit `.devkit/installation.json` with it, because snapshot gates
   (`devkit rules check --staged`, `--ci`) fail when a managed rule no longer
   matches the committed receipt.
