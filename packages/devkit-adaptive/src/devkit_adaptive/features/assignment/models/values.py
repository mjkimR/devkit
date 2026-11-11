"""Assignment values and the event fold."""

from dataclasses import dataclass, field
from typing import Any

from devkit.advisory import AdvisoryError

Assignment = dict[str, Any]
Event = dict[str, Any]


@dataclass
class Result:
    payload: dict[str, Any]
    notices: list[AdvisoryError] = field(default_factory=list)
    errors: list[AdvisoryError] = field(default_factory=list)


def fold(events: list[Event]) -> dict[str, Assignment]:
    assignments: dict[str, Assignment] = {}
    for event in events:
        identifier = event["id"]
        data = event["data"]
        match event["event"]:
            case "assigned":
                assignments[identifier] = dict(data)
            case "returned":
                assignments[identifier]["status"] = "returned"
                assignments[identifier]["return"] = data
                assignments[identifier]["verification"] = None
            case "verified":
                assignments[identifier]["verification"] = data
                assignments[identifier]["status"] = "verified" if data["result"] == "pass" else "rejected"
            case "closed":
                assignments[identifier].update(status="closed", close=data)
            case _:
                raise ValueError("unknown event")
    return assignments
