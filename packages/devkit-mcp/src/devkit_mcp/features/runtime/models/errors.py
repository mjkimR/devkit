"""Stable advisories of the retained MCP runtime."""

from devkit.advisory import Actor
from devkit_dist.features.host.models.errors import HostError


class RuntimeStaleError(HostError):
    code = "MCP_RUNTIME_STALE"
    actor = Actor.USER
    fix = (
        "Restart or reconnect the retained devkit MCP service so it loads the installed code, then call the tool"
        " again; nothing ran. A request retained by the old process does not survive: inspect Git, then prepare it"
        " again"
    )
