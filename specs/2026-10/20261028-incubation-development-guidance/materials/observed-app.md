# Observed synthetic app artifacts

These are disposable semantic-exercise artifacts, not a shipped app or real-user product decisions.

## Initial implementation

File `shopping.py`, SHA256 `715738c6c5f618eca8fca9917c0365224a33b428edc210d20509d068420c6a41`.

```python
"""Single-person shopping list; Python standard library only."""
import argparse
import json
import os
from pathlib import Path


def load(path):
    if not path.exists():
        return []
    items = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(items, list):
        raise ValueError("data must be a JSON list")
    ids = set()
    for item in items:
        if not isinstance(item, dict) or set(item) != {"id", "name", "done"}:
            raise ValueError("invalid shopping item")
        if type(item["id"]) is not int or item["id"] < 1 or item["id"] in ids:
            raise ValueError("invalid or duplicate item id")
        if not isinstance(item["name"], str) or not item["name"].strip():
            raise ValueError("invalid item name")
        if type(item["done"]) is not bool:
            raise ValueError("invalid completion state")
        ids.add(item["id"])
    return items


def save(path, items):
    # One editor only. Replacement avoids exposing a partially written JSON file.
    pending = path.with_name(path.name + ".pending")
    pending.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(pending, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("shopping.json"))
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="add an item")
    add.add_argument("name")
    commands.add_parser("list", help="show pending items")
    done = commands.add_parser("done", help="mark an item done by id")
    done.add_argument("id", type=int)
    args = parser.parse_args()
    try:
        items = load(args.data)
        if args.command == "add":
            name = args.name.strip()
            if not name:
                raise ValueError("item name cannot be blank")
            item = {"id": max((item["id"] for item in items), default=0) + 1, "name": name, "done": False}
            items.append(item)
            save(args.data, items)
            print(f"Added {item['id']}: {name}")
        elif args.command == "done":
            item = next((item for item in items if item["id"] == args.id), None)
            if item is None:
                raise ValueError(f"item {args.id} does not exist")
            item["done"] = True
            save(args.data, items)
            print(f"Done {item['id']}: {item['name']}")
        else:
            pending = [item for item in items if not item["done"]]
            print("\n".join(f"{item['id']}: {item['name']}" for item in pending) or "No pending items.")
    except (OSError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    main()
```

## Reconstructed adapter

File `shopping.py`, SHA256 `008fd9adc442f96387fd9bd643d611efbb5e16767af3871755c585ac75e05467`.

```python
"""Single-person shopping list; Python standard library only."""
import argparse
from pathlib import Path

from shopping_core import add_item, complete_item, pending_items


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("shopping.json"))
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="add an item")
    add.add_argument("name")
    commands.add_parser("list", help="show pending items")
    done = commands.add_parser("done", help="mark an item done by id")
    done.add_argument("id", type=int)
    args = parser.parse_args()
    try:
        if args.command == "add":
            item = add_item(args.data, args.name)
            print(f"Added {item['id']}: {item['name']}")
        elif args.command == "done":
            item = complete_item(args.data, args.id)
            print(f"Done {item['id']}: {item['name']}")
        else:
            pending = pending_items(args.data)
            print("\n".join(f"{item['id']}: {item['name']}" for item in pending) or "No pending items.")
    except (OSError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    main()
```

## Reconstructed core

File `shopping_core.py`, SHA256 `ce4f5693a09861219507f219009e31ae06d696abd9dab3bd776e1c299304b93b`.

```python
"""Persistence and list operations for a single shopping-list editor."""
import json
import os


def load(path):
    if not path.exists():
        return []
    items = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(items, list):
        raise ValueError("data must be a JSON list")
    ids = set()
    for item in items:
        if not isinstance(item, dict) or set(item) != {"id", "name", "done"}:
            raise ValueError("invalid shopping item")
        if type(item["id"]) is not int or item["id"] < 1 or item["id"] in ids:
            raise ValueError("invalid or duplicate item id")
        if not isinstance(item["name"], str) or not item["name"].strip():
            raise ValueError("invalid item name")
        if type(item["done"]) is not bool:
            raise ValueError("invalid completion state")
        ids.add(item["id"])
    return items


def save(path, items):
    # One editor only. Replacement avoids exposing a partially written JSON file.
    pending = path.with_name(path.name + ".pending")
    pending.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(pending, path)



def add_item(path, name):
    items = load(path)
    name = name.strip()
    if not name:
        raise ValueError("item name cannot be blank")
    item = {"id": max((item["id"] for item in items), default=0) + 1, "name": name, "done": False}
    items.append(item)
    save(path, items)
    return item


def complete_item(path, item_id):
    items = load(path)
    item = next((item for item in items if item["id"] == item_id), None)
    if item is None:
        raise ValueError(f"item {item_id} does not exist")
    item["done"] = True
    save(path, items)
    return item


def pending_items(path):
    return [item for item in load(path) if not item["done"]]
```

## Current facts after fresh-context resume

File `incubation.md`, SHA256 `bc8b21602fbd0f28158150ecdb67a09c52a8817f8b4198801a24fef554ad2548`.

```markdown
# Incubation current context

## Goal and intended usage

This is a synthetic semantic exercise, not a real product request or approval.
A household member remembers shopping items and inspects what remains.
The retained goal is a standard-library Python CLI with local persistent data for one editor.
The representative flow adds milk and bread, lists both, marks milk done, then lists bread.
No accounts, concurrency, network services or new product features are in scope.

## Retained decisions and current choices

Synthetic fixture decisions: Python CLI, single-person use, persistence and the bounded representative flow.
The synthetic resumed direction reconstructs the implementation within this same goal.
Agent implementation choice: `shopping.py` owns argument parsing, output and error handling; `shopping_core.py` owns validation, persistence and list operations.
Reason: isolate operations from the CLI so later app changes have a small core to change.
Easier future maintenance is an inference, not a measured outcome.
JSON items retain numeric stable `id`, nonblank `name` and boolean `done` fields.
Completed items remain stored; `list` shows pending entries.
Writes use same-directory staged replacement after input validation.
The 100-replacement/2,000-read probe supports small-file serialization up to 100 items (5,635 bytes); it does not establish crash durability.
No product questions remain inside the supplied flow; expansion still needs a direction.

## Run and verify

Working directory: `/Users/mj/workspace/workbench/repos/devkit-wt-dev-incubation-development-guidance/.devkit/transient/incubation-guidance/sample-app`.
Runtime: `/Users/mj/workspace/workbench/repos/devkit-wt-dev-incubation-development-guidance/.devkit/transient/incubation-guidance/venv/bin/python` (Python 3.12.8 on local macOS).
No dependency installation is needed; `README.md` gives manual CLI commands.
Effective policy inspection via `/Users/mj/workspace/workbench/repos/devkit-wt-dev-incubation-development-guidance/.devkit/transient/incubation-guidance/venv/bin/python -m devkit_dist config show -w /Users/mj/workspace/workbench/repos/devkit-wt-dev-incubation-development-guidance/.devkit/transient/incubation-guidance/sample-app` returned `configuration.development.approach=incubation`, exit 0.
The installed incubation and docs contexts and relevant incubation references were read.

Current source SHA256:

- `shopping.py`: `008fd9adc442f96387fd9bd643d611efbb5e16767af3871755c585ac75e05467`.
- `shopping_core.py`: `ce4f5693a09861219507f219009e31ae06d696abd9dab3bd776e1c299304b93b`.

Run `/Users/mj/workspace/workbench/repos/devkit-wt-dev-incubation-development-guidance/.devkit/transient/incubation-guidance/venv/bin/python experiments/reconstruction/verify_resume.py` from the working directory.
This retained verifier runs the unchanged original CLI checker, an existing-data read, add/done/list on a retained copy, the JSON probe, in-memory compilation and rules.
It writes bounded artifacts under `experiments/` and preserves the original list.
It records both implementation hashes because the original CLI checker records only the adapter hash.
`experiments/reconstruction/after-sources.json` binds app, core and checker identities.
`experiments/reconstruction/after-checks.json` records exact commands, exits and streams.
`experiments/reconstruction/after-flow-transcript.json` records all 32 CLI subprocess interactions.
Before-reconstruction identities, source text and passing baseline are in `before-sources.json`, `before-checks.json` and `before-flow-transcript.json` in that directory.
`after-source-snapshot.json` retains the resulting app/core text and identities.

Observed after reconstruction:

- Original checker: exit 0; 32 actual CLI processes passed, including blank names, absent IDs, malformed JSON/schema and Unicode persistence.
- Original list `experiments/json-feasibility/flow-run-zgletljj/shopping.json`: CLI `list` exit 0 with `2: bread` and `3: 우유`; original bytes unchanged.
- Original data SHA256: `f880c9b1cb3f9a96d17f65acb5f373bc0227eca9ac384d51fc6989c54bbd6eb4`.
- Existing-data copy `experiments/reconstruction/continued-shopping.json`: added eggs as ID 4, completed bread ID 2, then listed `3: 우유` and `4: eggs`; prior IDs/names and milk completion retained.
- Probe: exit 0; 100 replacements, 2,000 reads, 100 final items, 5,635 bytes.
- Built-in `compile`: passed for app, core, both original checkers and resume verifier, without bytecode.
- Rules: exit 0; 13 rules, zero errors/warnings.

## Open questions and limitations

No real-user usability test occurred; scenario choices and actual process observations are distinct.
Concurrency, power-loss/crash durability, large data, filesystem permission failures and other Python/OS versions remain unverified.
No app build, linter or type checker is configured; those checks were not run.
The structure is intended to ease changes; future-change effort has not been measured.
No SDD package, Unit, envelope, adoption, Git action, dependency install or external service was used.
Each sibling-write operation requested separate host approval.
Exact cwd/absolute paths and before/after source snapshots substitute for native confinement; no native enforcement guarantee is claimed.

## Next useful action

Before another iteration, compare app/core identities above and run `/Users/mj/workspace/workbench/repos/devkit-wt-dev-incubation-development-guidance/.devkit/transient/incubation-guidance/venv/bin/python experiments/reconstruction/verify_resume.py`.
A changed source identity requires affected checks to pass before prior implementation evidence applies.
This bounded reconstruction is complete; the next product change requires a supplied direction rather than inferred scope.
```
