"""Markdown with custom extensions.

We run two parsers against each file:

1. HTML parser, to generate the page output, and
2. Plain text parser, to generate text for page similarities.

"""

import logging
import re
import yaml
from markdown import Markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown_plain_text.extention import PlainTextExtension
from typing import Any, NamedTuple

__all__ = ["parse_markdown"]


log = logging.getLogger(__name__)


class YAMLSearchError(Exception):
    pass


class MarkdownWithMetadata(Markdown):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.metadata: dict[str, Any] = {}


class YAMLPreprocessor(Preprocessor):
    def run(self, lines: list[str]) -> list[str]:
        """Extract and parse a YAML block at the top of a file."""
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
            raise YAMLSearchError("did not find the end of the YAML header block")

        # lowercase the keys
        # setattr() gets around typing issues with .metadata
        setattr(self.md, "metadata", {k.lower(): v for k, v in metadata.items()})  # noqa: B010
        return new_lines


class YAMLExtension(Extension):
    def extendMarkdown(self, md: Markdown) -> None:
        """Register our metadata preprocessor at low priority."""
        md.preprocessors.register(YAMLPreprocessor(md), "yaml", 1)


# All docs share a parser, defined here ------------------------------


_html_parser = MarkdownWithMetadata(
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

# Run YAML with PlainText to remove metadata from the tree
_text_parser = MarkdownWithMetadata(
    extensions=[
        YAMLExtension(),
        PlainTextExtension(),
    ],
)


class _Parsed(NamedTuple):
    plaintext: str
    html: str
    metadata: dict[str, Any]


def parse_markdown(source: str) -> _Parsed:
    """Parse a Markdown document into HTML and metadata."""
    # Reset or we'll have leftover garbage from the previous file
    _html_parser.reset()
    _text_parser.reset()
    return _Parsed(
        _text_parser.convert(source),
        _html_parser.convert(source),
        _html_parser.metadata,
    )
