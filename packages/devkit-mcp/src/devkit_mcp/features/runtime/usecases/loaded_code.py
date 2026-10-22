"""Record the devkit code a retained service loaded and refuse protected calls once it is stale."""

from __future__ import annotations

from devkit_core.base.usecase import BaseUseCase

from devkit_mcp.features.runtime.models.errors import RuntimeStaleError
from devkit_mcp.features.runtime.models.loaded_code import LoadedCodeBaseline
from devkit_mcp.features.runtime.services import loaded_code

DETAIL_LIMIT = 20


class RecordLoadedCodeUseCase(BaseUseCase):
    """The baseline the service compares against: the installed devkit source when it starts."""

    def execute(self) -> LoadedCodeBaseline:
        return loaded_code.record()


class GuardLoadedCodeUseCase(BaseUseCase):
    """Raise ``MCP_RUNTIME_STALE`` when a loaded devkit module differs from the recorded baseline."""

    def __init__(self, baseline: LoadedCodeBaseline) -> None:
        self.baseline = baseline

    def execute(self) -> None:
        modules = loaded_code.stale(self.baseline)
        if modules:
            shown = [f"stale module: {name}" for name in modules[:DETAIL_LIMIT]]
            if len(modules) > DETAIL_LIMIT:
                shown.append(f"and {len(modules) - DETAIL_LIMIT} more")
            raise RuntimeStaleError(
                f"this MCP service process loaded devkit code that differs from the code now installed"
                f" ({len(modules)} module(s)); the call did not run",
                *shown,
            )
