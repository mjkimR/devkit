"""Bounded read-only registry view for collection; ordinary queries keep their contract."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

from devkit_spec.features.scope.models.deadline import Deadline
from devkit_spec.features.scope.models.model import Problem, Record
from devkit_spec.features.scope.repositories.localfs import LocalRegistry
from devkit_spec.features.scope.repositories.source import DOCUMENT_BYTES, TOTAL_DOCUMENT_BYTES


class CollectionRegistry(LocalRegistry):
    def query(self, namespace: str, deadline: Deadline) -> tuple[list[Record], list[Problem]]:
        records: list[Record] = []
        problems: list[Problem] = []
        size = 0
        with self._read_locked(namespace, deadline) as directory:
            if directory is None:
                return records, problems
            with os.scandir(directory) as entries:
                for entry in entries:
                    deadline.check("scope registry inventory")
                    if not entry.name.endswith(".json"):
                        continue
                    if len(records) + len(problems) >= 256:
                        problems.append(Problem("remaining-records", "input-limit"))
                        break
                    try:
                        fd = os.open(Path(entry.path), os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
                        with os.fdopen(fd, "rb") as stream:
                            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                                raise OSError("Registry record is not a regular file")
                            data = stream.read(DOCUMENT_BYTES + 1)
                        size += len(data)
                        if len(data) > DOCUMENT_BYTES or size > TOTAL_DOCUMENT_BYTES:
                            problems.append(Problem(entry.name, "input-limit"))
                            break
                        records.append(Record.from_dict(json.loads(data)))
                    except (OSError, ValueError, UnicodeError, TypeError, KeyError):
                        problems.append(Problem(entry.name, "source-unreadable"))
        return sorted(records, key=lambda item: item.task_id), problems
