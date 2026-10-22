# Verification evidence

## Header parsing benchmark

Python 3.12.3, PyYAML 6.0.3 with libyaml; Linux. Preloaded 682 Markdown headers from docs/ and specs/.
Nine alternating runs per route; values equal in every run. Python median 318.49 ms; guarded libyaml
median 89.80 ms; speedup 3.55x. This measures header parsing, not end-to-end command latency.

The Python baseline disables only the optional parser on the same worktree; no Git checkout is required.

```python
import statistics
import time
from pathlib import Path
from unittest.mock import patch

import yaml
from devkit_core.core import frontmatter as fm

headers = []
for directory in ('docs', 'specs'):
    for path in sorted(Path(directory).rglob('*.md')):
        block = fm.locate(path.read_text())
        if block:
            headers.append(block.header)

with patch.object(fm, '_FastStrictLoader', None):
    expected = [fm.load_header(header) for header in headers]
assert [fm.load_header(header) for header in headers] == expected
samples = {'python': [], 'guarded_c': []}
for iteration in range(9):
    order = [('python', None), ('guarded_c', fm._FastStrictLoader)]
    if iteration % 2:
        order.reverse()
    for name, loader in order:
        with patch.object(fm, '_FastStrictLoader', loader):
            started = time.perf_counter()
            result = [fm.load_header(header) for header in headers]
            samples[name].append((time.perf_counter() - started) * 1000)
        assert result == expected
print('PyYAML', yaml.__version__, 'libyaml', yaml.__with_libyaml__, 'headers', len(headers), 'equal=True')
for name, values in samples.items():
    print(name, 'median_ms', round(statistics.median(values), 2), 'runs', len(values))
ratio = statistics.median(samples['python']) / statistics.median(samples['guarded_c'])
print('speedup', round(ratio, 2))
assert ratio >= 2
```

## Compatibility and checks

Both parser routes run the shared grammar tests. Additional tests compare complete Python error messages,
accept moderately nested syntax, reject excessive syntax, preserve recursive alias identity, and import the module
with CSafeLoader absent. Tabs, question marks, hashes and U+FEFF use Python because libyaml accepts inputs the Python scanner rejects.
Independent review found 15 differing mutations among 2,960; another 19,138 unique mutations excluding those
characters had no differing outcomes. Regression tests cover the invalid forms and valid quoted occurrences.
The final frontmatter regression run passed 116 tests.
Lint and Pyright pass; the devkit-core wheel builds. The affected selector retains its full-suite fallback.

## Final cumulative verification

After merging main at 148f84df36858de01cd2f6147dbb21b346624b1f without conflicts, `just test-affected` retained
mode=full and passed 4,937 tests with 12 skipped. CI rules check passed with zero errors and warnings.
Final core wheel build, lint-check core and check core passed. Independent review verified the P1 fix.
