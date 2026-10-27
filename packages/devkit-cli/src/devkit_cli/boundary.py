"""The error boundary of a tool's commands and the output options it adds to each.

One ``Boundary`` per tool names the tool's logger root and environment prefix; the instance is the decorator::

    boundary = Boundary("mytool")          # MYTOOL_QUIET, MYTOOL_VERBOSE, MYTOOL_STRICT; logger "mytool"

    @click.command()
    @FORMAT_OPTION
    @boundary
    def scan(output_format: str) -> None: ...

- ``-q/--quiet``, ``-v/--verbose`` and ``--strict`` (or the three environment variables, on only when exactly
  ``1``; a flag wins) are added to every command and consumed by the boundary;
- under ``--verbose`` every record of the tool's logger is printed on stderr as an ``[INFO]`` line;
- any error leaves as one Agent Advisory Protocol block on stderr or, when stdout is JSON, as ``{"error": {...}}``
  on stdout only, and the process exits with the error's ``exit_code``; anything else is ``UNEXPECTED_ERROR``;
- output bytes never depend on the locale (stdout and stderr are made UTF-8 with ``backslashreplace``), and a
  reader that closes stdout early (``mytool ... | head``) ends the command quietly with exit ``2``.

click only parses syntax: a semantic argument check raises ``devkit.advisory.ArgumentError`` (``ARGUMENT_INVALID``)
through the boundary, so a JSON caller still receives one document.
"""

from __future__ import annotations

import contextlib
import contextvars
import functools
import io
import logging
import os
import sys
from collections.abc import Callable, Iterator
from dataclasses import replace
from typing import Any, NoReturn

import click
from devkit.advisory import AdvisoryError, ArgumentError, ExitCode, Level, as_advisory_error

from devkit_cli.output import OutputSettings, Reported, _settings, _unprinted, echo_json, is_json

_CONTINUATION = " " * len("[INFO]   ")


class _InfoFormatter(logging.Formatter):
    """A log record as ``[INFO]   <module>: <message>``, its further lines (a traceback) as continuation lines.

    ``<module>`` is the logger name without the tool's root prefix, so an agent reading ``-v`` output knows which
    part of the tool spoke.
    """

    def __init__(self, root: str) -> None:
        super().__init__()
        self._prefix = f"{root}."

    def format(self, record: logging.LogRecord) -> str:
        head, *rest = super().format(record).splitlines() or [""]
        source = record.name.removeprefix(self._prefix)
        return "\n".join([f"[INFO]   {source}: {head}".rstrip(), *(f"{_CONTINUATION}{line}".rstrip() for line in rest)])


def _utf8_output() -> None:
    """Make stdout and stderr UTF-8 with ``backslashreplace``, so no output depends on the locale.

    A character UTF-8 cannot encode (a lone surrogate from a ``surrogateescape``-decoded path) is written as its
    ``\\uXXXX`` escape instead of failing the command.
    """
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            with contextlib.suppress(OSError, ValueError):  # a closed or already-read stream keeps its settings
                stream.reconfigure(encoding="utf-8", errors="backslashreplace")


def _stdout_closed() -> NoReturn:
    """The reader of stdout went away: exit ``2`` without an advisory.

    Nobody reads the result any more, so nothing more is written: stdout is pointed at the null device (the
    interpreter's final flush must not fail again) and no advisory is rendered.
    """
    with contextlib.suppress(AttributeError, OSError, ValueError):
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        os.close(devnull)
    sys.exit(int(ExitCode.ERROR))


class Boundary:
    """The error boundary and output options of one tool's commands.

    ``name`` is the root of the tool's logger hierarchy (records of ``name`` and its children are shown under
    ``--verbose``); ``env_prefix`` defaults to ``name`` upper-cased with ``-`` and ``.`` as ``_``. ``log`` receives
    the traceback of an unexpected error at ``DEBUG`` (default: the ``<name>.cli`` logger).
    """

    def __init__(self, name: str, *, env_prefix: str | None = None, log: logging.Logger | None = None) -> None:
        if not name or name != name.strip():
            raise ValueError(f"Boundary name {name!r} must be a non-empty logger name")
        prefix = env_prefix if env_prefix is not None else name.upper().replace("-", "_").replace(".", "_")
        if not prefix.isidentifier():
            raise ValueError(f"environment prefix {prefix!r} is not a valid variable name prefix")
        self.name = name
        self.quiet_env = f"{prefix}_QUIET"
        self.verbose_env = f"{prefix}_VERBOSE"
        self.strict_env = f"{prefix}_STRICT"
        self._log = log if log is not None else logging.getLogger(f"{name}.cli")

    def __repr__(self) -> str:
        return f"Boundary({self.name!r})"

    def resolve_output(self, quiet: bool, verbose: bool, strict: bool) -> OutputSettings:
        """Combine the flags with the environment: a flag wins; quiet together with verbose is ``ArgumentError``."""
        if quiet or verbose:
            sources = ["--quiet", "--verbose"]
        else:
            quiet, verbose = self._env(self.quiet_env), self._env(self.verbose_env)
            sources = [f"{self.quiet_env}=1", f"{self.verbose_env}=1"]
        if quiet and verbose:
            raise ArgumentError(
                f"{' and '.join(sources)} cannot be combined",
                target_files=sources,
                fix="Pass at most one of -q/--quiet and -v/--verbose",
            )
        return OutputSettings(quiet=quiet, verbose=verbose, strict=strict or self._env(self.strict_env))

    @staticmethod
    def _env(name: str) -> bool:
        return os.environ.get(name) == "1"

    def output_options[F: Callable[..., Any]](self, fn: F) -> F:
        """Add ``-q/--quiet``, ``-v/--verbose`` and ``--strict`` (parameters ``quiet``, ``verbose``, ``strict``).

        The boundary applies it and consumes the three parameters, so a command never sees them.
        """
        fn = click.option(
            "--strict", "strict", is_flag=True, help=f"Exit 1 when a warning was reported (or {self.strict_env}=1)"
        )(fn)
        fn = click.option(
            "--verbose",
            "-v",
            "verbose",
            is_flag=True,
            help=f"Also print [INFO] log lines on stderr (or {self.verbose_env}=1)",
        )(fn)
        return click.option(
            "--quiet", "-q", "quiet", is_flag=True, help=f"Hide [NOTICE] blocks on stderr (or {self.quiet_env}=1)"
        )(fn)

    @contextlib.contextmanager
    def _logs_on_stderr(self, enabled: bool) -> Iterator[None]:
        """Print every record of the tool's logger on stderr while the command runs, when ``enabled``."""
        if not enabled:
            yield
            return
        logger = logging.getLogger(self.name)
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(_InfoFormatter(self.name))
        previous = logger.level
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        try:
            yield
        finally:
            logger.removeHandler(handler)
            logger.setLevel(previous)

    def __call__(self, fn: Callable[..., Any] | None = None, *, json_only: bool = False) -> Any:
        """Decorate a click command so every error leaves through the Agent Advisory Protocol.

        Use as ``@boundary`` or ``@boundary(json_only=True)``, below the click decorators. It adds the output options
        and applies them while the command runs. An error is rendered on stderr; when stdout is JSON (``json_only``,
        or the command's ``output_format`` parameter is ``json``) it is printed there instead, as ``{"error": {...}}``
        with the warnings and notices passed to ``echo_notices`` before it under ``notices``, or not at all when the
        error is ``Reported`` (its result is already there). The process exits with the error's ``exit_code``; any
        other exception is ``UNEXPECTED_ERROR``, its traceback logged for ``--verbose``. click's own exits, aborts
        and usage errors pass through; any other ``click.ClickException`` is unexpected. A ``BrokenPipeError`` (the
        reader closed stdout) exits ``2`` without output.
        """

        def decorate(func: Callable[..., Any]) -> Callable[..., Any]:
            @functools.wraps(func)
            def wrapper(
                *args: Any, quiet: bool = False, verbose: bool = False, strict: bool = False, **kwargs: Any
            ) -> Any:
                _utf8_output()
                try:
                    return guarded(*args, quiet=quiet, verbose=verbose, strict=strict, **kwargs)
                except BrokenPipeError:  # also raised while rendering an error below
                    _stdout_closed()

            def guarded(*args: Any, quiet: bool, verbose: bool, strict: bool, **kwargs: Any) -> Any:
                token: contextvars.Token[OutputSettings | None] | None = None
                pending: list[AdvisoryError] = []
                pending_token = _unprinted.set(pending)
                json_out = json_only or is_json(kwargs.get("output_format"))
                try:
                    settings = replace(self.resolve_output(quiet, verbose, strict), json=json_out)
                    token = _settings.set(settings)
                    with self._logs_on_stderr(settings.verbose):
                        try:
                            return func(*args, **kwargs)
                        except Exception as exc:
                            expected = isinstance(exc, AdvisoryError) and exc.level is Level.ERROR
                            if not (expected or isinstance(exc, (click.UsageError, Reported, BrokenPipeError))):
                                self._log.debug("unexpected error", exc_info=exc)  # a raised notice included
                            raise
                except (
                    click.exceptions.Exit,
                    click.UsageError,
                    click.exceptions.Abort,
                    SystemExit,
                    BrokenPipeError,
                ):
                    raise
                except Reported as reported:
                    if not json_out:
                        click.echo(reported.error.render(), err=True)
                    sys.exit(int(reported.error.exit_code))
                except Exception as exc:
                    error = as_advisory_error(exc)
                    if json_out:
                        document: dict[str, object] = {"error": error.to_dict()}
                        if pending:
                            document["notices"] = [notice.to_dict() for notice in pending]
                        echo_json(document)
                    else:
                        click.echo(error.render(), err=True)
                    sys.exit(int(error.exit_code))
                finally:
                    _unprinted.reset(pending_token)
                    if token is not None:
                        _settings.reset(token)

            return self.output_options(wrapper)

        return decorate if fn is None else decorate(fn)
