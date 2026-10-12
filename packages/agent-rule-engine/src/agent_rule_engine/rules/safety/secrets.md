# [RULE-secret-leak] Secrets must not enter the repository

The rule flags, among the files under check, credential files (`.env` and
`.env.*` except `.env.example`, `.env.sample` and `.env.template`; SSH private
keys such as `id_rsa` and `id_ed25519`) and contents matching PEM private key
headers, AWS access key IDs, GitHub tokens or `sk-` API keys.

It inspects explicit targets only: files named on the command line or the
changed files of `agent-rules check --staged` / `--ci`. A run without targets
reports nothing, because a working tree scan would flag ignored local files.

Remove the secret from the change and load credentials from the environment or
a secret store instead. Rotate any key that was already committed.
