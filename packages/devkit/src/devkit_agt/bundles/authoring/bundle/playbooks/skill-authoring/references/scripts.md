# Script support

1. If `devkit`, `git`, `rg` or another installed tool already prints the needed slice, put the command in
   `SKILL.md` instead of a script.
2. If the script would only print a file, make that file a reference instead; running a script can trigger a host
   approval prompt.
3. Otherwise write a Python 3 script:
   - Use the standard library only, so it runs without installation. State the minimum Python version in the
     header and use nothing newer.
   - Read and write with `encoding="utf-8"` and call `sys.stdout.reconfigure(encoding="utf-8")`; piped output
     otherwise follows the locale.
   - Print compact, deterministic output (TSV, JSON or IDs) in stable order.
   - Stay read-only unless the script's name or a flag declares the write.
4. In `SKILL.md`, say when to run the script (not read it) by its path relative to the skill directory
   (`python3 scripts/collect.py`), and describe in one line what it computes so an agent can do it by hand when the
   script cannot run. Keep it executable (`0755`); projections preserve the mode.
