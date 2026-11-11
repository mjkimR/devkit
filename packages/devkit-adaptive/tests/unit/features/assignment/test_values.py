"""Pure event policy checks."""

from devkit_adaptive.features.assignment.models.values import fold


def test_fold_replaces_return_and_preserves_event_values():
    events = [
        {"id": "a1", "event": "assigned", "data": {"id": "a1", "status": "open"}},
        {"id": "a1", "event": "returned", "data": {"status": "failed"}},
        {"id": "a1", "event": "verified", "data": {"result": "fail"}},
        {"id": "a1", "event": "returned", "data": {"status": "completed"}},
    ]
    result = fold(events)["a1"]
    assert result["status"] == "returned" and result["return"]["status"] == "completed"
    assert result["verification"] is None
    assert events[0]["data"] == {"id": "a1", "status": "open"}
