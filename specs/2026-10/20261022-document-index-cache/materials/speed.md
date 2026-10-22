# Speed and multi-process evidence

Recorded for `SPEC-document-index-cache` (AC-06, AC-10) on the `dev-document-index-cache` worktree at `845c3c17`, the
final implementation commit. macOS on Apple silicon, 14 cores, Python 3.12.8, PyYAML 6.0.3 with libyaml. Nothing
else ran during the measurements. Wall time.

The three driver scripts are recorded verbatim at the end of this file. They ran from the ignored `scratch/`
directory of the worktree with `uv run python scratch/<script> <worktree>` and are not part of the change.

## In-process `DocumentIndex.load` (AC-10)

Method (`speed.py`): copy `docs/` and `specs/` into `scratch/fresh/` with an empty `.devkit/` and no
`.devkit/transient/`, so the copy has no memo. Warm the worktree's memo with one load, then one discarded load of
each root, then seven interleaved pairs: a load of the worktree (warm memo) and a load of the copy (no memo),
clearing the in-process memo before each load so every load behaves like a new process. Before timing, the warm and
fresh results were compared equal (documents with frontmatter, references and aliases, problems, historical paths).

| Load | Runs (ms) | Median |
| --- | --- | --- |
| Warm memo (worktree, 644 documents) | 52.2, 57.4, 56.1, 48.9, 51.8, 56.9, 53.3 | 53.3 ms |
| No memo (copy) | 317.6, 306.0, 329.1, 300.4, 319.7, 315.2, 313.5 | 315.2 ms |

Ratio of the medians: 0.169, within the bound of 0.35 (prototype: 0.18). A profile of the warm load shows the
existing walk (`os.walk`, `stat`, `pathlib.relative_to`) and file reads as most of the remaining time; decoding the
memo (590 KiB) is a small part.

## Commands (AC-10)

Method (`cli_speed.py`): one discarded run of each, then seven interleaved runs of each command with
`.venv/bin/devkit`, timed around `subprocess.run` in one Python driver: `-w` the worktree (warm memo) and
`-w scratch/fresh` (made its own Git repository with `git init` so that it is a devkit root; no
`.devkit/transient/`, so no memo). Every run exited `0`.

| Command | Warm memo, median | No memo, median | Baseline (`baseline-profile.md`, `eb33d6cf`) |
| --- | --- | --- | --- |
| `devkit spec resolve CAP-DOCS-document-model` | 186 ms | 434 ms | 427 ms |
| `devkit spec list feedback` | 198 ms | 451 ms | 440 ms |
| `devkit --help` (no index load; measured at `5e14eca4`) | 177 ms | | 191 ms |

The baseline column quotes `docs/materials/2026-10/20261022-document-index-cache/baseline-profile.md`, measured on
the Planning worktree while another profiling ran. The proposal expected about 170 ms with a warm memo; the rest of
each call is interpreter start, click and plugin import (`devkit --help`), outside this Unit (Non-Goal 4).

## Several processes at once (AC-06)

Method (`concurrency.py`): a copy of `docs/` and `specs/` with `.devkit/transient/` in `scratch/concurrency/`. Four
rounds; before rounds 1 to 3 one document changes, so every process has a changed entry to write. In each round
eight processes started with the `spawn` method wait on one barrier, then each runs `DocumentIndex.load` (which
reads and writes the memo) and returns its result. The parent compares each result, by value, with a load that has
the memo disabled, then decodes the memo left behind: `version` and `fingerprint` current and every entry rebuilt by
`decode_entry`.

| Round | Processes | Results equal to a fresh build | Exit codes | Memo entries | Memo decodes |
| --- | --- | --- | --- | --- | --- |
| 0 (no memo) | 8 | 8 | all `0` | 702 | yes |
| 1 | 8 | 8 | all `0` | 702 | yes |
| 2 | 8 | 8 | all `0` | 702 | yes |
| 3 | 8 | 8 | all `0` | 702 | yes |

The integration test `test_concurrent_loads_all_equal_a_fresh_build_and_leave_a_valid_memo` runs the same check
with eight threads in one process.

## Scripts

### `speed.py`

```python
"""AC-10: warm-memo versus fresh DocumentIndex.load, interleaved, in one process."""
import shutil, statistics, sys, time
from pathlib import Path
from devkit_spec.features.documents import DocumentIndex
from devkit_spec.features.documents.repositories import index as ix

root = Path(sys.argv[1]).resolve()
copy = root / "scratch" / "fresh"
if copy.exists():
    shutil.rmtree(copy)
copy.mkdir(parents=True)
(copy / ".devkit").mkdir()
for name in ("docs", "specs"):
    shutil.copytree(root / name, copy / name, symlinks=True)
assert not (copy / ".devkit/transient").exists()

def timed(path):
    ix._parsed.clear()
    start = time.perf_counter()
    index = DocumentIndex.load(path)
    elapsed = time.perf_counter() - start
    ix._parsed.clear()
    return elapsed, index

def view(i):
    return ([(d.path, d.id, d.frontmatter, d.references, d.aliases) for d in i.documents],
            [(p.message, p.target_files) for p in i.problems], i.historical)

_, warm_index = timed(root)       # warm the memo
_, fresh_index = timed(copy)      # discarded warm-up
_, warm_index = timed(root)       # discarded warm-up
assert view(warm_index) == view(fresh_index), "warm and fresh differ"
warm, fresh = [], []
for _ in range(7):
    w, _ = timed(root); warm.append(w)
    f, _ = timed(copy); fresh.append(f)
mw, mf = statistics.median(warm), statistics.median(fresh)
print(f"documents={len(warm_index.documents)} warm_median_ms={mw*1000:.1f} fresh_median_ms={mf*1000:.1f} ratio={mw/mf:.3f}")
print("warm_ms=" + ",".join(f"{x*1000:.1f}" for x in warm))
print("fresh_ms=" + ",".join(f"{x*1000:.1f}" for x in fresh))
```

### `cli_speed.py`

```python
"""AC-10: medians of seven CLI runs, warm memo (the worktree) and no memo (scratch/fresh), interleaved."""
import statistics, subprocess, sys, time
from pathlib import Path
root = Path(sys.argv[1]).resolve()
devkit = str(root / ".venv/bin/devkit")
fresh = root / "scratch/fresh"
def run(args, ws):
    start = time.perf_counter()
    done = subprocess.run([devkit, *args, "-w", str(ws)], capture_output=True)
    assert done.returncode == 0, done.stderr
    return (time.perf_counter() - start) * 1000
for args in (["spec", "resolve", "CAP-DOCS-document-model"], ["spec", "list", "feedback"]):
    run(args, root); run(args, fresh)  # discarded warm-up
    warm, cold = [], []
    for _ in range(7):
        warm.append(run(args, root)); cold.append(run(args, fresh))
    print(f"{' '.join(args)}: warm_median_ms={statistics.median(warm):.0f} no_memo_median_ms={statistics.median(cold):.0f}")
```

### `concurrency.py`

```python
"""AC-06: several processes load and write the memo of one workspace at once."""
import json, multiprocessing as mp, pickle, shutil, sys
from pathlib import Path

def view(i):
    return pickle.dumps(([(d.path, d.id, d.frontmatter, d.references, d.provenance, d.aliases, d.issues) for d in i.documents],
                         [(p.message, p.target_files) for p in i.problems], sorted(i.historical)))

def worker(root, barrier, queue):
    from devkit_spec.features.documents import DocumentIndex
    barrier.wait()
    queue.put(view(DocumentIndex.load(Path(root))))

def fresh(root):
    from devkit_spec.features.documents import DocumentIndex
    from devkit_spec.features.documents.repositories import index as ix
    from devkit_spec.features.documents.repositories.memo import ParseMemo
    ix._parsed.clear()
    original = ParseMemo.open
    ParseMemo.open = classmethod(lambda cls, root, *, writes: None)
    try:
        return view(DocumentIndex.load(root))
    finally:
        ParseMemo.open = original

if __name__ == "__main__":
    mp.set_start_method("spawn")
    source = Path(sys.argv[1]).resolve()
    root = source / "scratch" / "concurrency"
    if root.exists():
        shutil.rmtree(root)
    (root / ".devkit/transient").mkdir(parents=True)
    for name in ("docs", "specs"):
        shutil.copytree(source / name, root / name, symlinks=True)
    from devkit_spec.features.documents.repositories import memo
    from devkit_spec.features.documents.repositories.memo import decode_entry
    processes = 8
    for round_ in range(4):
        if round_:  # change one document per round so every process writes again
            target = root / "docs/capabilities/documents/CAP-DOCS-document-model.md"
            target.write_text(target.read_text(encoding="utf-8") + f"\nRound {round_}: `CAP-DOCS-document-lookup`.\n", encoding="utf-8")
        expected = fresh(root)
        barrier, queue = mp.Barrier(processes), mp.Queue()
        procs = [mp.Process(target=worker, args=(str(root), barrier, queue)) for _ in range(processes)]
        for p in procs: p.start()
        results = [queue.get(timeout=120) for _ in procs]
        for p in procs: p.join()
        stored = json.loads((root / ".devkit/transient/spec/document-index.json").read_text(encoding="utf-8"))
        assert stored["version"] == memo.FORMAT_VERSION and stored["fingerprint"] == memo.fingerprint()
        for relative, entry in stored["entries"].items():
            decode_entry(relative, entry)
        identical = sum(pickle.loads(r) == pickle.loads(expected) for r in results)
        print(f"round={round_} processes={processes} identical={identical} exit_codes={[p.exitcode for p in procs]} memo_entries={len(stored['entries'])} memo_decodes=yes")
        assert identical == processes
```
