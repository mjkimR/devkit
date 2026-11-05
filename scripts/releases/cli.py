"""Selective release command boundary: stable sentinels and protocol-rendered failures."""

from __future__ import annotations

import os
import subprocess
import sys
import urllib.error
import zipfile
from pathlib import Path

import click
from devkit.advisory import Actor, AdvisoryError, ArgumentError, Retry
from devkit_dist.adapters.cli import boundary, field_value

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "releases"

from .artifacts import bootstrap, publish
from .errors import ReleaseError
from .prepare import prepare
from .release import release

ROOT = Path(__file__).resolve().parents[2]


@click.command()
@click.argument("operation", type=click.Choice(["prepare", "build", "publish"]), default="prepare")
@click.argument("tag", required=False)
@click.option("--check", is_flag=True)
@click.option("--baseline", type=click.Path(path_type=Path))
@click.option("--bootstrap", "bootstrap_tag")
@click.option("--source")
@click.option("--artifacts", type=click.Path(path_type=Path))
@click.option("--output", type=click.Path(path_type=Path))
@click.option("--repository", default=lambda: os.environ.get("GITHUB_REPOSITORY", "mjkimR/devkit"))
@boundary
def command(operation, tag, check, baseline, bootstrap_tag, source, artifacts, output, repository):
    root = click.get_current_context().obj["root"]
    try:
        invalid = (
            (check and (operation != "prepare" or bootstrap_tag))
            or (bootstrap_tag and (operation != "prepare" or tag or baseline))
            or (not bootstrap_tag and any([source, artifacts, output]))
            or (operation == "prepare" and tag)
            or (operation == "publish" and baseline)
        )
        if invalid:
            raise ArgumentError(
                "unsupported release option combination",
                code="RELEASE_OPTIONS_INVALID",
                fix="Use --check only with prepare --baseline FILE; use bootstrap, build and publish without --check and with their own inputs.",
            )
        if operation == "build":
            version = (root / "VERSION").read_text().strip()
            if tag != "v" + version:
                raise ReleaseError(
                    f"{tag} does not match VERSION ({version})",
                    code="RELEASE_TAG_MISMATCH",
                    fix="Pass the tag matching root VERSION.",
                )
        if bootstrap_tag:
            if not all([source, artifacts, output]):
                raise ReleaseError("bootstrap requires --source, --artifacts and --output")
            data = bootstrap(root, bootstrap_tag, source, artifacts, output, repository)
            click.echo(f"[RELEASE_BOOTSTRAP: v{data['release']} packages={len(data['packages'])}]")
        elif operation == "publish":
            if not tag:
                raise ReleaseError("publish requires a version tag")
            publish(root / "dist/release", tag, root=root)
            click.echo(f"[RELEASE_PUBLISHED: {field_value(tag)}]")
        else:
            if baseline is None:
                raise ReleaseError(
                    "completed --baseline FILE required; first import originals with --bootstrap",
                    code="RELEASE_BASELINE_REQUIRED",
                    fix="Import one completed release with --bootstrap TAG --source REF --artifacts DIR --output FILE; then pass --baseline FILE.",
                )
            if operation == "build":
                data = release(root, tag, baseline, repository)
                click.echo(f"[RELEASE: v{data['release']} assets=dist/release]")
            else:
                data = prepare(root, baseline, check=check)
                click.echo(
                    f"[VERSION: {data['release']} state={'checked' if check else 'synced'} packages={len(data['packages'])}]"
                )
    except subprocess.SubprocessError as exc:
        raise AdvisoryError(
            str(exc),
            str(getattr(exc, "stderr", None) or getattr(exc, "stdout", None) or ""),
            code="RELEASE_TOOL_FAILED",
            actor=Actor.DEVELOPER,
            retry=Retry.AFTER_FIX,
            fix="Resolve the named build, Git, lock, sync or gh command failure and rerun the same operation.",
        ) from exc
    except urllib.error.URLError as exc:
        raise AdvisoryError(
            str(exc),
            code="RELEASE_ARTIFACT_UNAVAILABLE",
            actor=Actor.DEVELOPER,
            retry=Retry.AFTER_FIX,
            fix="Restore access to the original artifact URL and retry; never substitute rebuilt bytes.",
        ) from exc
    except OSError as exc:
        raise AdvisoryError(
            str(exc),
            code="RELEASE_IO_FAILED",
            actor=Actor.DEVELOPER,
            retry=Retry.AFTER_FIX,
            fix="Restore the named file, executable or filesystem access, then rerun the same operation.",
        ) from exc
    except (ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        raise ReleaseError(str(exc)) from exc


@boundary
def invalid_argument(message: str) -> None:
    raise ArgumentError(message, fix="Run uv run python scripts/version.py --help and correct the arguments.")


def main(argv: list[str] | None = None, *, root: Path = ROOT) -> int:
    try:
        try:
            return command.main(args=argv, obj={"root": root}, standalone_mode=False) or 0
        except click.ClickException as exc:
            invalid_argument(exc.format_message())
    except SystemExit as exc:
        return int(exc.code or 0)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
