# Script support

Read this when a skill step is repetitive and deterministic, or needs to parse
or filter repository state so that only the relevant slice reaches the context;
most situation-dependent content is a conditional reference instead.

## Decide whether a script is needed

1. **Existing CLI first.** If `devkit`, `git`, `rg` or another installed tool
   already prints the needed slice, call it. A few chained commands go into
   `SKILL.md` as a code block, not into a script file.
2. **No script that only prints a reference file.** That is a conditional
   reference with extra cost: running a script can trigger a host approval
   prompt where reading a file does not.
3. **Otherwise write a script** in Python 3 with the standard library, which
   needs no build step or installation.

## Writing rules

- Standard library only; no third-party packages.
- State the minimum Python version in the file header and use no syntax or
  modules newer than it (for example no `match` or `tomllib` below 3.11).
- Handle paths with `pathlib`.
- Read and write files with `encoding="utf-8"` and set UTF-8 on standard output
  (`sys.stdout.reconfigure(encoding="utf-8")`); piped output otherwise follows
  the locale encoding.
- Print compact, deterministic, machine-readable output (TSV, JSON or IDs) with
  stable ordering.
- Keep a script read-only unless it must write; a script that writes declares it
  in its name or a flag.
- On failure exit non-zero with a message that states the cause and the next
  action.
- Support `--help` with one line per option.

## Wiring it into the skill

- `SKILL.md` states when to run the script and says to run it, not read it. Only
  the output enters the context, which is the point of a script.
- `SKILL.md` also describes in one line what the script computes, so an agent
  can reach the same result with ordinary commands when the script cannot run.
  The script accelerates the procedure; it is not a hard dependency.
- Invoke it by path relative to the skill directory, for example
  `python3 scripts/collect.py --format tsv`. Keep it executable (`0755`) in the
  source; projections preserve the mode.
