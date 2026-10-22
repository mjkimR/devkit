# Script support

## Decide whether a script is needed

1. **Existing CLI first.** If `devkit`, `git`, `rg` or another installed tool
   already prints the needed slice, call it. Put a few chained commands in
   `SKILL.md` as a code block, not in a script file.
2. **No script that only prints a reference file.** Make it a conditional
   reference instead, because running a script can trigger a host approval
   prompt where reading a file does not.
3. **Otherwise write a Python 3 script.**

## Writing rules

- Use the standard library only, so the script runs without a build step or
  installation.
- State the minimum Python version in the file header and use no syntax or
  modules newer than it (for example no `match` or `tomllib` below 3.11).
- Handle paths with `pathlib`.
- Read and write files with `encoding="utf-8"` and call
  `sys.stdout.reconfigure(encoding="utf-8")`; piped output otherwise follows
  the locale encoding.
- Print compact, deterministic, machine-readable output (TSV, JSON or IDs) with
  stable ordering.
- Keep a script read-only unless it must write; a script that writes declares it
  in its name or a flag.
- On failure, exit non-zero with a message that states the cause and the next
  action.
- Support `--help` with one line per option.

## Wiring it into the skill

- In `SKILL.md`, state when to run the script and say to run it, not read it;
  only its output enters the context.
- Describe in one line what the script computes, so an agent can reach the same
  result with ordinary commands when the script cannot run.
- Invoke it by path relative to the skill directory, for example
  `python3 scripts/collect.py --format tsv`. Keep it executable (`0755`) in the
  source; projections preserve the mode.
