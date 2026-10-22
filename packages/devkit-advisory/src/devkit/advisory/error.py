from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Self, TypedDict

from devkit.advisory.advisory import DEFAULT_CODE, Advisory
from devkit.advisory.types import ActionMode, Actor, ExitCode, Level, Retry

UNEXPECTED_CODE = "UNEXPECTED_ERROR"


class AdvisoryFields(TypedDict, total=False):
    """The keyword arguments of ``AdvisoryError``, for subclasses that add constructor state of their own.

    A subclass declares ``**fields: Unpack[AdvisoryFields]`` and forwards them to ``super().__init__``.
    """

    code: str | None
    level: Level | None
    actor: Actor | None
    retry: Retry | None
    guardrail: bool | None
    input_error: bool | None
    retry_after: str | None
    fix: str | None
    what_to_report: str | None
    target_files: Sequence[str] | None
    brief: bool | None
    exit_code: ExitCode | None


class AdvisoryError(Exception):
    """Exception carrying an Agent Advisory Protocol envelope.

    Subclasses may set a class-level default for every field (``code``,
    ``level``, ``actor``, ``retry``, ``guardrail``, ``input_error``,
    ``retry_after``, ``fix``, ``what_to_report``, ``target_files``, ``brief``,
    ``exit_code``); a keyword argument other than ``None`` overrides it per
    instance. Positional arguments after the message become ``[DETAIL]`` lines
    and are converted to ``str``; an empty ``code`` is ``GENERAL_ERROR``, and a
    ``target_files`` given as one string is one target.

    An instance whose ``level`` is ``WARNING`` or ``NOTICE`` reports something
    an operation that succeeded must tell its caller: it is returned with the
    result (under ``notices``), never raised, and its ``exit_code`` is ``OK``.
    An ``ERROR`` whose ``exit_code`` is ``OK``, or whose mode is ``AUTO``
    without a ``fix``, raises ``ValueError``.
    """

    exit_code: ExitCode = ExitCode.ERROR
    code: str = DEFAULT_CODE
    level: Level = Level.ERROR
    actor: Actor = Actor.NONE
    retry: Retry = Retry.UNSAFE
    guardrail: bool = False
    input_error: bool = False
    retry_after: str | None = None
    fix: str | None = None
    what_to_report: str | None = None
    target_files: tuple[str, ...] = ()
    brief: bool = False

    def __init__(
        self,
        message: str,
        *details: object,
        code: str | None = None,
        level: Level | None = None,
        actor: Actor | None = None,
        retry: Retry | None = None,
        guardrail: bool | None = None,
        input_error: bool | None = None,
        retry_after: str | None = None,
        fix: str | None = None,
        what_to_report: str | None = None,
        target_files: Sequence[str] | None = None,
        brief: bool | None = None,
        exit_code: ExitCode | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        if level is not None:
            self.level = level
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
            self.target_files = (target_files,) if isinstance(target_files, str) else tuple(target_files)
        if brief is not None:
            self.brief = brief
        if not self.code:
            self.code = DEFAULT_CODE
        if self.level is not Level.ERROR:
            self.exit_code = ExitCode.OK
        self.details: tuple[str, ...] = tuple(str(detail) for detail in details)
        self._check()

    def _check(self) -> None:
        """Refuse an error that would exit ``0`` or tell the agent to run a ``[FIX]`` it does not have."""
        if self.level is not Level.ERROR:
            return
        if self.exit_code is ExitCode.OK:
            raise ValueError(f"{self.code}: an ERROR advisory exits {int(ExitCode.FINDINGS)} or {int(ExitCode.ERROR)}")
        # Derived from the fields alone: a subclass's ``advisory`` may read state its __init__ has not set yet.
        fields = Advisory(actor=self.actor, retry=self.retry, guardrail=self.guardrail, input_error=self.input_error)
        if fields.mode is ActionMode.AUTO and not self.fix:
            raise ValueError(f"{self.code}: an AUTO error needs the fix command it directs the agent to run")

    def __reduce__(self) -> tuple[Any, ...]:
        # Rebuilt without __init__, as with_level copies: subclasses may require their own arguments.
        return _rebuild, (type(self), self.args, self.__dict__)

    def with_level(self, level: Level, *, brief: bool | None = None) -> Self:
        """A copy at ``level``: the same class, code and fields.

        ``exit_code`` is ``OK`` below ``ERROR``; an ``ERROR`` copy keeps this error's
        ``exit_code``, or takes the class default when this is a warning or notice.

        For a condition that is an error in one command and a warning or notice
        in another (override drift after ``devkit sync``, another rule's policy
        problem in ``devkit rules explain``).
        """
        copy = _rebuild(type(self), self.args, self.__dict__)
        copy.level = level
        if brief is not None:
            copy.brief = brief
        if level is not Level.ERROR:
            copy.exit_code = ExitCode.OK
        elif self.level is not Level.ERROR:
            copy.exit_code = type(self).exit_code
        copy._check()
        return copy

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
            level=Level.ERROR,
            actor=Actor.DEVELOPER,
            retry=Retry.AFTER_FIX,
            guardrail=True,
            input_error=False,
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
            level=Level.ERROR,
            actor=Actor.USER,
            retry=Retry.AFTER_FIX,
            guardrail=False,
            input_error=False,
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
            level=Level.ERROR,
            actor=Actor.TOOL,
            retry=Retry.AFTER_FIX,
            guardrail=False,
            input_error=False,
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
            level=Level.ERROR,
            actor=Actor.DEVELOPER,
            retry=Retry.AFTER_FIX,
            guardrail=False,
            input_error=True,
            fix=fix,
            target_files=target_files,
        )

    @property
    def advisory(self) -> Advisory:
        return Advisory(
            code=self.code,
            level=self.level,
            actor=self.actor,
            retry=self.retry,
            guardrail=self.guardrail,
            input_error=self.input_error,
            retry_after=self.retry_after,
            fix=self.fix,
            what_to_report=self.what_to_report,
            target_files=self.target_files,
            details=self.details,
            brief=self.brief,
        )

    @property
    def mode(self) -> ActionMode:
        return self.advisory.mode

    def lines(self) -> list[str]:
        """Render the advisory block (headline by level) as sentinel lines for stderr."""
        return self.advisory.lines(self.message)

    def render(self) -> str:
        """Render the advisory block as one text (CLI stderr or MCP tool result)."""
        return "\n".join(self.lines())

    def to_dict(self, *, include_advisory: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "code": self.code,
            "level": self.level.value,
            "message": self.message,
            "exit_code": int(self.exit_code),
        }
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


class ArgumentError(AdvisoryError):
    """A command-line argument or library parameter is malformed or names something that does not exist.

    The one owner of ``ARGUMENT_INVALID`` (``INPUT_ERROR``): command lines raise it for every semantic argument
    check (click only parses syntax), so a JSON caller still receives one ``{"error": ...}`` document. An
    application's own argument error derives from it rather than declaring the code again.
    """

    code = "ARGUMENT_INVALID"
    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX
    input_error = True


def _rebuild[E: AdvisoryError](cls: type[E], args: tuple[Any, ...], state: dict[str, Any]) -> E:
    """Unpickle or copy an ``AdvisoryError`` without calling its ``__init__``."""
    error = cls.__new__(cls, *args)
    error.__dict__.update(state)
    return error


def as_advisory_error(error: BaseException) -> AdvisoryError:
    """Return an ``ERROR``-level ``error`` itself; wrap anything else as an ``UNEXPECTED_ERROR`` (``MAINTENANCE``).

    A warning or notice that was raised is a defect: they are returned, never raised.
    """
    if isinstance(error, AdvisoryError):
        if error.level is Level.ERROR:
            return error
        return AdvisoryError(
            f"a {error.level.value} advisory was raised instead of returned: ({error.code}) {error.message}",
            code=UNEXPECTED_CODE,
            actor=Actor.DEVELOPER,
            retry=Retry.UNSAFE,
        )
    message = f"{type(error).__name__}: {error}" if str(error) else type(error).__name__
    return AdvisoryError(message, code=UNEXPECTED_CODE, actor=Actor.DEVELOPER, retry=Retry.UNSAFE)


def render_error(error: BaseException) -> str:
    """Render any exception as an advisory block, adapting non-advisory errors."""
    return as_advisory_error(error).render()
