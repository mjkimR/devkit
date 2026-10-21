"""``instruction`` assets: Markdown documents whose frontmatter header is their catalog entry."""

from __future__ import annotations

from devkit_dist.features.distribution.models.errors import BundleError
from devkit_dist.features.distribution.services.bundles.common import read_frontmatter


def read_instruction_header(data: bytes, context: str) -> str:
    """The raw YAML header of an instruction; it must declare nonempty ``name`` and ``description`` strings."""
    _, block, metadata = read_frontmatter(data, context, "instruction")
    for field in ("name", "description"):
        value = metadata.get(field)
        if not isinstance(value, str) or not value.strip():
            raise BundleError(f"{context}: instruction frontmatter needs a nonempty {field}")
    return block.header
