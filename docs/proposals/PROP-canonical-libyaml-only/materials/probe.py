import json
from pathlib import Path
import platform
import yaml
from devkit_core.core import frontmatter

root = Path.cwd()
rows = []
counts = {'headers': 0, 'c_rejected': 0, 'value_changes': 0}
for directory in ('docs', 'specs'):
    for path in sorted((root / directory).rglob('*.md')):
        try:
            block = frontmatter.locate(path.read_text(encoding='utf-8'))
            if block is None:
                continue
            old = frontmatter.load_header(block.header)
        except Exception:
            continue
        counts['headers'] += 1
        try:
            new = yaml.load(block.header, Loader=frontmatter._FastStrictLoader)
            new = {} if new is None else new
        except Exception as exc:
            counts['c_rejected'] += 1
            rows.append({'path': str(path.relative_to(root)), 'error': str(exc)})
            continue
        if old != new:
            counts['value_changes'] += 1
            rows.append({'path': str(path.relative_to(root)), 'values': 'changed'})
fixtures = {
    'tab_in_plain': 'key:\tvalue\n',
    'tab_in_quotes': 'key: "a\tb"\n',
    'question_in_plain': 'key: value?x\n',
    'hash_in_quotes': 'key: "a#b"\n',
    'unicode': 'key: "한글😀"\n',
    'invalid_date': 'key: 2024-02-30\n',
    'duplicate': 'key: 1\nkey: 2\n',
    'unsafe_tag': 'key: !!python/object:builtins.object {}\n',
}
results = {}
for name, value in fixtures.items():
    results[name] = {}
    for label, loader in [('python', frontmatter._StrictLoader), ('c', frontmatter._FastStrictLoader)]:
        try:
            results[name][label] = repr(yaml.load(value, Loader=loader))
        except Exception as exc:
            mark = getattr(exc, 'problem_mark', None)
            results[name][label] = {'exception': type(exc).__name__, 'line': mark.line + 1 if mark else None, 'column': mark.column + 1 if mark else None}
print(json.dumps({'python': platform.python_version(), 'pyyaml': yaml.__version__, 'libyaml': yaml.__with_libyaml__, 'corpus': counts, 'differences': rows, 'fixtures': results}, ensure_ascii=False, indent=2))
