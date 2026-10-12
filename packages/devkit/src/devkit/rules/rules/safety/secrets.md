# [RULE-secret-leak] Secrets must not enter the repository

The rule flags, among the files under check:

- credential files by name: `.env`, `.env.*` and `*.env` (templates ending in
  `.example`, `.sample` or `.template` are allowed), SSH private keys such as
  `id_rsa` and `id_ed25519`, and key stores (`*.key`, `*.p12`, `*.pfx`,
  `*.jks`, `*.keystore`);
- contents matching PEM or PGP private key headers (`-----BEGIN ... PRIVATE
  KEY-----`, including encrypted keys), AWS access key IDs (`AKIA`/`ASIA`),
  GitHub tokens (`ghp_`, `gho_`, ..., `github_pat_`), `sk-` API keys, Stripe
  live keys, Slack tokens and Google API keys. Each matching line is reported
  once, with the kind of credential.

It inspects explicit targets only: files named on the command line or the
changed files of `devkit rules check --staged` / `--ci`. A run without targets
reports nothing, because a working tree scan would flag ignored local files.

Remove the secret from the change and load credentials from the environment or
a secret store instead. Rotate any key that was already committed.
