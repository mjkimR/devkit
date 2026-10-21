# [RULE-secret-leak] Secrets Never Enter a Commit

## 1. Overview

A credential committed to Git stays in its history even after the file is fixed. The rule stops it at the commit
gate and in CI, before it is pushed.

- **Phase and severity**: `linter`, `error`.
- **What is checked**: explicit targets only, the files named on the command line or the changed files of
  `devkit rules check --staged` / `--ci`. A run without targets reports nothing: a whole working tree scan would
  flag local files that `.gitignore` keeps out of Git, such as `.env`.

## 2. Cause of Violation

- **Credential files by name** (`<name> is a credential file`): `.env`, `.env.<anything>` and `<anything>.env`
  (templates ending in `.example`, `.sample` or `.template` are allowed), SSH private keys (`id_rsa`, `id_ed25519`,
  `id_ecdsa`, `id_dsa`) and key stores (`*.key`, `*.p12`, `*.pfx`, `*.jks`, `*.keystore`).
- **Credentials in content** (`Potential secret in file content (<kind>)`, once per line): PEM and PGP private key
  headers (`-----BEGIN ... PRIVATE KEY-----`), AWS access key IDs (`AKIA`, `ASIA`), GitHub tokens (`ghp_`, `gho_`,
  `ghu_`, `ghs_`, `ghr_`, `github_pat_`), `sk-` API keys, Stripe live keys (`sk_live_`, `rk_live_`), Slack tokens
  (`xox?-`) and Google API keys (`AIza`).

## 3. Remediation

1. Remove the secret from the change (`git restore --staged <file>` for a credential file, or edit the content).
2. Load the credential at run time from the environment or a secret store; commit a template (`.env.example`) with
   placeholders instead.
3. If the secret was ever committed or pushed, rotate it: removing it from the latest commit does not remove it from
   history.

## 4. Configuration

The rule has no settings.

## 5. Exceptions

There is no inline suppression. A test fixture that must contain a key-shaped string belongs under a path excluded
from every rule (`[rules] exclude = ["tests/fixtures/keys/**"]`), with the reason in a comment; prefer generating
such values in the test instead.
