# devkit harness in this repository

This repository runs the devkit harness of `devkit-agt`: governance rules and
commit gates run as code, delivery workflows are computed by `devkit workflow`,
and `devkit run` bounds the output of verification commands. The rule, gate
and workflow assets they run are deployed by `devkit sync` like any other
asset (the `devkit` bundle covers distribution).

## Contracts

1. **Rules and gates run as code.** `devkit rules check` loads synchronized
   rules without flags; `devkit gate` runs synchronized gates at commit time.
   Configure them in `[rules]` and `[gates]` of `.devkit/config.toml`, never by
   editing the managed file.
2. **Snapshot gates trust the committed receipt.** Snapshot gates
   (`devkit rules check --staged`, `--ci`) trust the committed
   `.devkit/installation.json` and fail when a managed rule no longer matches
   it; commit the receipt with every change that synchronized a rule.
