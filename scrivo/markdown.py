"""Markdown with custom extensions."""

import logging
import re
from typing import Any

import yaml
from markdown import Markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

__all__ = ["YAMLExtension", "YAMLPreprocessor"]

log = logging.getLogger(__name__)


class YAMLPreprocessor(Preprocessor):
    """Parse YAML metadata at the top of a Markdown document."""

    def run(self, lines: list[str]) -> list[str]:
        """Run the Preprocessor to extract any YAML block.

        Args:
            lines (list[str]): the lines of the input Markdown

        Returns:
            list[str]: the original Markdown minus the YAML content

            NB: This also has side-effects, setting 'self.md.metadata' to the
            extracted YAML content.

        Raises:
            ValueError: If we cannot find the end ofa YAML header block.

        """
        RE_YAML = re.compile(r"^(-|\.){3}$")

        yaml_start, yaml_end = None, None
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            rx = RE_YAML.match(line.strip())
            # We're into text without ever seeing YAML
            if not rx and yaml_start is None:
                break
            # We see a YAML line and we haven't before
            if rx and yaml_start is None:
                yaml_start = i
                continue
            # We see a YAML line and we are tracking the YAML block
            if rx and yaml_start is not None:
                yaml_end = i
                break

        metadata: dict[str, Any] = {}
        if yaml_start is None and yaml_end is None:
            new_lines = lines
        elif yaml_start is not None and yaml_end is not None:
            new_lines = lines[(yaml_end + 1) :]
            metadata = yaml.safe_load("\n".join(lines[(yaml_start + 1) : yaml_end]))
        else:
            raise ValueError("did not find the end of the YAML header block")

        # lowercase the keys
        self.md.metadata = {k.lower(): v for k, v in metadata.items()}

        return new_lines


class YAMLExtension(Extension):
    """Parse YAML metadata at the top of a Markdown document."""

    def extendMarkdown(self, md: Markdown) -> None:
        """Register our metadata preprocessor at low priority.

        Args:
            md: Markdown parser.

        """
        md.preprocessors.register(YAMLPreprocessor(md), "yaml", 1)


_parser = Markdown(
    output_format="html",
    tab_length=2,
    extensions=[
        "markdown.extensions.abbr",
        "markdown.extensions.fenced_code",
        "markdown.extensions.footnotes",
        "markdown.extensions.tables",
        "markdown.extensions.codehilite",
        "markdown.extensions.smarty",
        "markdown.extensions.toc",
        "mdx_math",
        YAMLExtension(),
    ],
    extension_configs={
        "markdown.extensions.footnotes": {
            "UNIQUE_IDS": True,
            # https://github.com/jekyll/jekyll/issues/3751#issue-83081590
            "BACKLINK_TEXT": "&#8617;&#xfe0e;",
        },
        "markdown.extensions.codehilite": {"use_pygments": True, "guess_lang": False},
        "mdx_math": {"enable_dollar_delimiter": True},
    },
)


def md2html(source: str) -> tuple[str, dict[str, Any]]:
    """Parse a Markdown document using our custom parser.

    Args:
        source (str): the Markdown source text

    Returns:
        tuple(str, dict):
            1. the converted output as a string
            2. any extracted metadata as a dict

    """
    _parser.reset()  # Reset or we'll have leftover garbage from the previous file
    html = _parser.convert(source)
    meta: dict[str, Any] = _parser.metadata  # type: ignore
    return html, meta
