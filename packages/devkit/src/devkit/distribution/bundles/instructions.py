"""``instruction`` assets: Markdown documents whose frontmatter header is their catalog entry."""

from __future__ import annotations

from devkit.core import frontmatter
from devkit.core.errors import FrontmatterError

from ..errors import BundleError


def read_instruction_header(data: bytes, context: str) -> str:
    """The raw YAML header of an instruction; it must declare nonempty ``name`` and ``description`` strings."""
    try:
        text = data.decode("utf-8")
    except UnicodeError as exc:
        raise BundleError(f"{context}: instruction must be UTF-8") from exc
    try:
        block = frontmatter.locate(text)
        if block is None:
            raise BundleError(f"instruction requires YAML frontmatter: {context}")
        metadata = frontmatter.load_header(block.header)
    except FrontmatterError as exc:
        raise BundleError(f"{context}: {exc}") from exc
    for field in ("name", "description"):
        value = metadata.get(field)
        if not isinstance(value, str) or not value.strip():
            raise BundleError(f"{context}: instruction frontmatter needs a nonempty {field}")
    return block.header
