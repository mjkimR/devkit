# Source acquisition variants

Run every command from the project root. `$work` is the temporary directory the entry's first command created and printed, outside the project tree; if the shell keeps no variables between commands, write the printed path in its place.

## A branch or tag

```bash
git clone -c core.symlinks=false --depth 1 --no-recurse-submodules --branch <branch-or-tag> <url> "$work/source"
git -C "$work/source" rev-parse HEAD
```

## A commit SHA

`--branch` rejects a commit SHA; fetch the commit into an empty repository:

```bash
git init -q "$work/source"
git -C "$work/source" config core.symlinks false
git -C "$work/source" fetch --depth 1 <url> <full-commit-sha>
git -C "$work/source" checkout --detach FETCH_HEAD
git -C "$work/source" rev-parse HEAD
```

If the server refuses to serve that commit, report the refusal and ask for a branch or tag.

## A subdirectory

1. Clone the repository as above; record its commit and the subdirectory as the source path prefix.
2. Limit the inventory to `"$work/source/<subdirectory>"`.
3. Take the license file from the repository root unless the subdirectory carries its own.

## A local path

1. Read the path in place; copy nothing and write nothing under it.
2. If `git -C <path> rev-parse HEAD` succeeds, record that commit, `git -C <path> remote get-url origin` when a remote exists, and whether `git -c core.fsmonitor=false -C <path> status --porcelain` prints any line; the option keeps the source's own configuration from running a program.
3. If the path is not a Git repository, record the absolute path and state that the source has no commit identity.
4. If uncommitted changes exist, state that the recorded commit does not identify the files read.

## A failed clone

1. Report the Git error text and the URL; retry once only when the error names a transient network failure.
2. If the repository needs credentials, ask the user for a local path to their own checkout instead of handling a credential.
3. Delete `$work` before ending the run; leave no partial directory.

## Identity to record

| Field | Value |
| --- | --- |
| URL | The clone URL, or the local path |
| Commit | The full SHA `rev-parse HEAD` printed |
| Path | The file's path relative to the repository root |
| License | The license file's path and the license it states, or `none found` |

A source without a license file grants no stated permission to redistribute; carry `none found` into the recommendation's conversion notes.
