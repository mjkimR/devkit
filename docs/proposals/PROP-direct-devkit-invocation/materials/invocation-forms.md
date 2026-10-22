# Invocation forms: inventory, measurements and failure behavior

Collected in the Planning worktree at 6f0d4600 (macOS Darwin 24.6.0, Apple silicon, uv 0.12.8, Python 3.12).

## 1. Where `uv run devkit` is emitted

| Emitter | Mentions | Path kind |
| --- | --- | --- |
| Managed `AGENTS.md` block: `guidance_block.py` (3), `bundles/guidance.py` "Required first" line (1), `spec-pointer` (1), `run-pointer` (1) | 6 | Frequent: `get-context` once per bundle per agent context; `devkit run` per test or lint run |
| Generated `devkit-workflow` entry skill (`workflow_skill.py`) | 12 | Frequent: `workflow next`, `envelope`, `answer`, `handoff` |
| Generated `devkit-playbook` entry skill (`playbook_skill.py`) | 3 | Rare: explicit user invocation only |
| `devkit` bundle instructions (`consumption.md` 15, `in-repo-bundle.md` 4, `resource-kinds.md` 1) | 20 | Setup and maintenance: `add`, `sync`, `override`, `status`, `bundle validate` |
| `harness` bundle instructions (`harness-consumption.md` 4, `harness-assets.md` 4, `devkit-run.md` 2) | 10 | Mixed: `rules check` per commit; the rest is setup |
| `spec` bundle (`scout`, `code-reviewer`, `spec-feedback`, three playbooks) | 16 | Mixed; the same bundle names bare `devkit ...` about 267 times |
| `authoring` bundle (two rule messages, two guides, two playbooks, one instruction) | 7 | Rare: rule remediation text |
| `guides/` (installation guides) | 38 | Setup |

Hooks pay no `uv run` cost today:

- Commit gates (`.git/hooks/*.d/20-devkit`) execute the worktree's `.venv/bin/python` directly and report
  `GATE_INTERPRETER_UNAVAILABLE` when it cannot import `devkit_agt.features.gate`.
- Codex host hooks register `devkit host hook --host codex --asset <asset>`, resolved through the host's `PATH`
  (`devkit_dist/features/host/repositories/adapters/codex.py`); the adapter deliberately avoids machine-specific paths.
- No Claude Code or Antigravity hook registration calls devkit.

## 2. Per-call cost

Median of 20 to 40 warm runs from the worktree root, `VIRTUAL_ENV` unset; times in ms.

| Command | `uv run` | `uv run --no-sync` | `uv run --frozen` | `.venv/bin/devkit` | activated `PATH` |
| --- | --- | --- | --- | --- | --- |
| `--version` | 57.2 | 48.6 | 52.5 | 38.8 | 40.0 |
| `get-context spec` | 164.3 | 155.7 | 172.5 | 162.0 | 161.5 |
| `workflow next --unit <proposal>` | 141.3 | 127.0 | 130.1 | 118.7 | 118.8 |
| `spec resolve <ID>` | 446.8 | 436.0 | 448.2 | 427.0 | 429.8 |

- The `uv run` overhead is about 18-23 ms against the direct executable and about 9-14 ms against `--no-sync`; the
  draft's 93 ms against 53-63 ms (about 35 ms) was not reproduced at the median, though one run had a 119 ms p90.
- On real frequent commands the saving is 2-14 % of a 120-450 ms call. An agent session with about 50 devkit calls
  saves about 1 s, against seconds of model latency per tool call.

## 3. Behavior on a missing, stale or misplaced environment

Probed in scratch projects (a local package with a console script, and a non-editable path dependency whose lock
moved from 1.0.0 to 2.0.0 without `uv sync`):

| Situation | `uv run` | `uv run --no-sync` | `.venv/bin/<tool>` |
| --- | --- | --- | --- |
| No `.venv` | Creates and syncs it, then runs | Creates an empty `.venv`, then `Failed to spawn`, exit 2 | Shell `No such file or directory`, exit 127 |
| Called from a subdirectory | Finds the project, runs | Finds the project, runs | Exit 127 (path is relative to the root) |
| Lock moved (`git pull`, branch switch, new worktree without setup) | Syncs, runs the locked version | Runs the old version silently, exit 0 | Runs the old version silently, exit 0 |

- No direct form can emit a devkit advisory for a missing environment: devkit is not running. The draft's
  "fails with an actionable advisory" holds only for a wrapper or for `uv run`.
- An activated environment is not portable: the agent shell of this Planning run inherited
  `VIRTUAL_ENV=/Users/mj/workspace/hitl-kernel/.venv` from another project and had no `devkit` on `PATH`; `uv run`
  warned and used the project environment.
- An executable path recorded at sync is machine-specific; the managed `AGENTS.md` block is committed, so it cannot
  hold one, and the Codex adapter already rules machine paths out of registrations.
- Windows is out of scope (`ARCH-03-context`: devkit targets POSIX only), so `.venv/Scripts` is not a factor.
- A Codex sandbox run used `uv run --no-sync` for read-only queries
  (`docs/materials/2026-10/20261020-scope-registry-sandbox-access/verification.md`); that is observed usage, not a
  measured requirement.

## 4. Benchmark script

Run as `python3 bench.py <worktree> <runs> "--version" "get-context spec" ...`.

```python
import os, statistics, subprocess, sys, time
W = sys.argv[1]
N = int(sys.argv[2])
env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
act = dict(env, VIRTUAL_ENV=f"{W}/.venv", PATH=f"{W}/.venv/bin:" + env["PATH"])
cmds = {
    "uv run devkit": (["uv", "run", "devkit"], env),
    "uv run --no-sync devkit": (["uv", "run", "--no-sync", "devkit"], env),
    "uv run --frozen devkit": (["uv", "run", "--frozen", "devkit"], env),
    ".venv/bin/devkit": ([".venv/bin/devkit"], env),
    "activated PATH devkit": (["devkit"], act),
}
subs = [x.split() for x in sys.argv[3:]] or [["--version"]]
for sub in subs:
    print("##", " ".join(sub))
    for name, (base, e) in cmds.items():
        subprocess.run(base + sub, cwd=W, env=e, capture_output=True)  # warm
        ts = []
        for _ in range(N):
            t = time.perf_counter()
            r = subprocess.run(base + sub, cwd=W, env=e, capture_output=True)
            ts.append((time.perf_counter() - t) * 1000)
        ts.sort()
        print(f"{name:26s} median {statistics.median(ts):7.1f} ms  p10 {ts[len(ts)//10]:7.1f}  p90 {ts[len(ts)*9//10]:7.1f}  rc={r.returncode}")
```
