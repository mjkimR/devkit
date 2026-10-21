# devkit harness in this repository

This repository runs the devkit harness of `devkit-agt`: rules and commit gates
run as code, `devkit workflow` computes delivery stages, and `devkit run`
bounds the output of verification commands.

## Contracts

1. **Rules and gates run as code.** `devkit rules check` loads synchronized
   rules without flags; `devkit gate` runs synchronized gates at commit time.
   Configure them in `[rules]` and `[gates]` of `.devkit/config.toml`, never by
   editing the managed file.
2. **Snapshot gates trust the committed receipt.** Snapshot gates
   (`devkit rules check --staged`, `--ci`) fail when a managed rule no longer
   matches the committed `.devkit/installation.json`; commit the receipt with
   every change that synchronized a rule.
