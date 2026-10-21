# Exact retrieval comparison and evidence

## Options

| Option | Evidence and tradeoff | Decision |
| --- | --- | --- |
| Call `search_playbooks` and filter results | Search ranks metadata, applies budgets and may load embedding dependencies; its results omit bodies. Exact IDs can be absent from ranked results. | Reject |
| Reuse installed-bundle override lookup | `override_commands.py` parses colon selectors and resolves installed sources for mutation; it does not define the deployed receipt snapshot. | Reject as resolver; reuse slug grammar only |
| New filesystem/manifest lookup | Would duplicate override/render/ownership logic and risk reading unsynchronized sources. | Reject |
| Thin exact lookup over existing receipt readers | `reading.py` offers synchronized root, runtime receipt and owned reads; `playbook_search.py` already checks playbook entrypoint prefixes/ownership. | Select |

## Source evidence

- `installation/reading.py`: `synchronized_project_root`, `read_synchronized`, `read_owned` preserve project-root,
  pending journal, personal render, managed hash/mode and live ordinary override semantics.
- `installation/context.py`: synchronized bundle absence uses `SELECTION_INVALID` and `devkit list`; no installed
  package lookup is needed to distinguish a typo from an unselected bundle.
- `installation/playbook_search.py`: receipt playbook assets and their entrypoints supply canonical identity and
  effective path; exact retrieval does not call its search index or bounds handling.
- `bundles/common.py` and `bundles/playbooks.py`: shared slug grammar and frontmatter decoding/header validation.
  `read_frontmatter` plus `text[block.end:]` supplies body extraction without a second parser.
- `cli/__init__.py`: `_json_command`, `WORKSPACE` and the adjacent context/search commands establish JSON-only
  success/error behavior. `installation/results.py` supplies the result/to_dict pattern.
- `tests/distribution/test_playbooks.py`: effective overrides and missing/modified file tests provide fixture and
  assertion patterns; Development adds exact-selector, complete-body and CLI coverage.

## Scout disposition

The nested scout returned completed based on source/test inspection, with no test execution. Its reuse and
receipt-snapshot recommendations are adopted. Its suggested colon delimiter follows existing override selectors,
but the approved task and milestone require slash; the new command intentionally uses slash while sharing the
same slug grammar. Exact-one-entrypoint validation is explicit in this proposal rather than assumed to be a
receipt-schema invariant. No stronger current-selection freshness guarantee is claimed.

## Verification limits

No production code or external scheduler integration was run. Shared personal-render evidence validation and source identity behavior are
specified from existing reader semantics; Development must verify the matrix in AC-2. The content hash identifies
returned bytes, not publisher provenance. No linked resources are prefetched. Read-only status allows existing
shared-lock transient infrastructure, not changes to deployed assets or selection.

## Challenger disposition

The mandatory medium challenger identified that `bundles/templates.py` excludes playbooks from `TEMPLATE_KINDS`,
and `bundles/manifest.py::_check_source` rejects them. The proposal now explicitly excludes playbook template or
personal-render support. AC-2 covers ordinary overrides and stale runtime evidence for other eligible assets.
The worker verified the correction against those sources; the challenger did not verify subsequent edits.
