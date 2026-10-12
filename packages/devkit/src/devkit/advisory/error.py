from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Self

from devkit.advisory.advisory import DEFAULT_CODE, Advisory
from devkit.advisory.types import ActionMode, Actor, ExitCode, Retry

UNEXPECTED_CODE = "UNEXPECTED_ERROR"


class AdvisoryError(Exception):
    """Exception carrying an Agent Advisory Protocol envelope.

    Subclasses may set a class-level default for every field (``code``,
    ``actor``, ``retry``, ``guardrail``, ``input_error``, ``retry_after``,
    ``fix``, ``what_to_report``, ``target_files``, ``exit_code``); a keyword
    argument other than ``None`` overrides it per raise. Positional arguments
    after the message become ``[DETAIL]`` lines and are converted to ``str``.
    """

    exit_code: ExitCode = ExitCode.FAILED
    code: str = DEFAULT_CODE
    actor: Actor = Actor.NONE
    retry: Retry = Retry.UNSAFE
    guardrail: bool = False
    input_error: bool = False
    retry_after: str | None = None
    fix: str | None = None
    what_to_report: str | None = None
    target_files: tuple[str, ...] = ()

    def __init__(
        self,
        message: str,
        *details: object,
        code: str | None = None,
        actor: Actor | None = None,
        retry: Retry | None = None,
        guardrail: bool | None = None,
        input_error: bool | None = None,
        retry_after: str | None = None,
        fix: str | None = None,
        what_to_report: str | None = None,
        target_files: Sequence[str] | None = None,
        exit_code: ExitCode | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        if actor is not None:
            self.actor = actor
        if retry is not None:
            self.retry = retry
        if guardrail is not None:
            self.guardrail = guardrail
        if input_error is not None:
            self.input_error = input_error
        if exit_code is not None:
            self.exit_code = exit_code
        if retry_after is not None:
            self.retry_after = retry_after
        if fix is not None:
            self.fix = fix
        if what_to_report is not None:
            self.what_to_report = what_to_report
        if target_files is not None:
            self.target_files = tuple(target_files)
        self.details: tuple[str, ...] = tuple(str(detail) for detail in details)

    @classmethod
    def blocked(
        cls,
        message: str,
        *details: object,
        code: str | None = None,
        fix: str | None = None,
        target_files: Sequence[str] | None = None,
    ) -> Self:
        """A deliberate guardrail or policy refused the operation (``BLOCKED``)."""
        return cls(
            message,
            *details,
            code=code,
            actor=Actor.DEVELOPER,
            retry=Retry.AFTER_FIX,
            guardrail=True,
            fix=fix,
            target_files=target_files,
        )

    @classmethod
    def interaction(
        cls,
        message: str,
        *details: object,
        code: str | None = None,
        what_to_report: str | None = None,
        fix: str | None = None,
    ) -> Self:
        """A human decision is required; ``fix`` runs only after the user agrees (``INTERACTION``)."""
        return cls(
            message,
            *details,
            code=code,
            actor=Actor.USER,
            retry=Retry.AFTER_FIX,
            what_to_report=what_to_report,
            fix=fix,
        )

    @classmethod
    def auto_fix(
        cls,
        message: str,
        *details: object,
        fix: str,
        code: str | None = None,
        target_files: Sequence[str] | None = None,
    ) -> Self:
        """A safe remediation command exists; run it once, then retry once (``AUTO``)."""
        return cls(
            message,
            *details,
            code=code,
            actor=Actor.TOOL,
            retry=Retry.AFTER_FIX,
            fix=fix,
            target_files=target_files,
        )

    @classmethod
    def invalid_input(
        cls,
        message: str,
        *details: object,
        code: str | None = None,
        fix: str | None = None,
        target_files: Sequence[str] | None = None,
    ) -> Self:
        """Malformed flag, argument, or input file; correct it before rerunning (``INPUT_ERROR``)."""
        return cls(
            message,
            *details,
            code=code,
            actor=Actor.DEVELOPER,
            retry=Retry.AFTER_FIX,
            input_error=True,
            fix=fix,
            target_files=target_files,
        )

    @property
    def advisory(self) -> Advisory:
        return Advisory(
            code=self.code,
            actor=self.actor,
            retry=self.retry,
            guardrail=self.guardrail,
            input_error=self.input_error,
            retry_after=self.retry_after,
            fix=self.fix,
            what_to_report=self.what_to_report,
            target_files=self.target_files,
            details=self.details,
        )

    @property
    def mode(self) -> ActionMode:
        return self.advisory.mode

    def lines(self) -> list[str]:
        """Render the error and advisory as sentinel lines for stderr."""
        return self.advisory.lines(self.message)

    def render(self) -> str:
        """Render the error and advisory as one text block (CLI stderr or MCP tool result)."""
        return "\n".join(self.lines())

    def to_dict(self, *, include_advisory: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {"code": self.code, "message": self.message, "exit_code": int(self.exit_code)}
        if include_advisory:
            data["advisory"] = self.advisory.to_dict()
        return data

    def to_problem_details(
        self, *, status: int | None = None, type_base: str | None = None, include_advisory: bool = True
    ) -> dict[str, Any]:
        """Format as an RFC 7807 problem details object.

        ``status`` is the HTTP status chosen by the transport boundary and is omitted when not given.
        ``type`` is ``<type_base>/<code>`` when a documentation base URI is given, else ``about:blank``.
        """
        data: dict[str, Any] = {
            "type": f"{type_base.rstrip('/')}/{self.code}" if type_base else "about:blank",
            "title": self.code,
            "detail": self.message,
            "code": self.code,
        }
        if status is not None:
            data["status"] = status
        if include_advisory:
            data["advisory"] = self.advisory.to_dict()
        return data

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{type(self).__name__}(code={self.code!r}, message={self.message!r})"


def as_advisory_error(error: BaseException) -> AdvisoryError:
    """Return ``error`` itself, or wrap an unexpected exception as an ``UNEXPECTED_ERROR`` (``MAINTENANCE``)."""
    if isinstance(error, AdvisoryError):
        return error
    message = str(error) or type(error).__name__
    return AdvisoryError(message, code=UNEXPECTED_CODE, actor=Actor.DEVELOPER, retry=Retry.UNSAFE)


def render_error(error: BaseException) -> str:
    """Render any exception as an advisory block, adapting non-advisory errors."""
    return as_advisory_error(error).render()
