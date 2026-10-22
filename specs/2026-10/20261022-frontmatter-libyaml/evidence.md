# Verification evidence

## Header parsing benchmark

Python 3.12.3, PyYAML 6.0.3 with libyaml; Linux. Preloaded 682 Markdown headers from docs/ and specs/.
Nine alternating runs per route; values equal in every run. Python median 178.74 ms; guarded libyaml
median 34.81 ms; speedup 5.14x. This measures header parsing, not end-to-end command latency.

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
with CSafeLoader absent. Tab separators use Python because libyaml accepts inputs the Python scanner rejects.
Lint and Pyright pass; the devkit-core wheel builds. The affected selector retains its full-suite fallback.
