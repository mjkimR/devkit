"""Extension notes are additive to the established boundary parser."""

import pytest

from devkit_spec.features.entrypoints.repositories.bundle import parse_acceptance_ids, parse_boundaries


def test_annotation_preserves_values_and_scanner_ordinals() -> None:
    text = """---
example: '- [ ] skipped'
---
<!-- - [ ] skipped -->
```markdown
- [ ] skipped
```
- [ ] **Task 1**: Implement
  - **_Boundary**: `src/a.py` (existing note),
    `src/b.py` (scope extension: shares parsing: AC-01, AC-02), `tests/` (sync output)
  - _Requirements: AC-01, AC-02_
- [x] **Task 2**: Other
  - **_Boundary**: **src/c.py**
"""
    first, second = parse_boundaries(text)
    assert first.index == 1 and second.index == 2
    assert first.values == ["src/a.py", "src/b.py", "tests/"]
    assert first.requirements == ["AC-01", "AC-02"]
    assert [(e.path, e.reason) for e in first.extensions] == [("src/b.py", "shares parsing: AC-01, AC-02")]
    assert not first.annotation_errors
    assert second.values == ["src/c.py"] and not second.extensions


@pytest.mark.parametrize(
    "note", ["(scope extension: )", "(scope extension: nested (why))", "(scope extension: unclosed"]
)
def test_invalid_note_is_exposed_for_inspection(note: str) -> None:
    task = parse_boundaries(f"- [ ] task\n  - **_Boundary**: `src/x.py` {note}\n")[0]
    assert task.annotation_errors


def test_legacy_multiline_note_with_nested_call_backticks_and_commas() -> None:
    # FB-entrypoints-derive-boundary-annotations: prose must not become a bogus path.
    text = """- [ ] task
  - **_Boundary**: `a/b.py`,
    `c/d.py` (its fixture asserts `ContextResult.to_dict()` shape, so it gains keys),
    plain/e.py (legacy note), `f/g.py`
"""
    task = parse_boundaries(text)[0]
    assert task.values == ["a/b.py", "c/d.py", "plain/e.py", "f/g.py"]
    assert not task.extensions and not task.annotation_errors


def test_acceptance_ids_ignore_examples_and_require_bracketed_heading_ids() -> None:
    assert parse_acceptance_ids("""### [AC-01] real
```markdown
### [AC-02] example
```
<!--
### [AC-03] comment
-->
### AC-04 informal
""") == {"AC-01"}
