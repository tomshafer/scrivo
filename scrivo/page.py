"""A Page represents a single web document.

Pages originate in Markdown and are to be rendered as HTML.
"""
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional, Tuple, TypeVar

from dateparser import parse as parse_date
from jinja2 import Environment, FileSystemLoader, Template
from markdown import Markdown

from scrivo.markdown import YAMLMetadataExtension

# This is the entire configuration of the Markdown parser
_md_parser = Markdown(
    output_format="html5",
    tab_length=2,
    extensions=[
        "markdown.extensions.fenced_code",
        "markdown.extensions.footnotes",
        "markdown.extensions.tables",
        "markdown.extensions.codehilite",
        "markdown.extensions.smarty",
        "markdown.extensions.toc",
        "mdx_math",
        YAMLMetadataExtension(),
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


def parse_markdown(source: str) -> Tuple[str, Dict]:
    """Parse a Markdown document using our custom parser.

    Args:
        source (str): the Markdown source text

    Returns:
        tuple(str, dict):
            1. the converted output as a string
            2. any extracted metadata as a dict

    """
    # Reset or we'll have leftover garbage from the previous file
    _md_parser.reset()
    html: str = _md_parser.convert(source)
    meta: Dict = _md_parser.metadata  # pylint: disable=no-member
    return html, meta


def check_metadata(meta: Dict) -> Dict[str, Any]:
    """Clean the provided metadata and check for unexpected values.

    Args:
        meta (dict): metadata from the Markdown parser

    Returns:
        dict(str, Any): a dict of cleaned metadata entries

    """
    ACCEPTABLE_METADATA = {"title", "date", "tags", "draft", "template", "heading"}
    provided_meta = set(meta.keys())
    # Warn about invalid metadata
    invalid = provided_meta.difference(ACCEPTABLE_METADATA)
    for key in invalid:
        logging.warning('metadata key "%s" will not be parsed', key)
    # Assign with defaults
    # TODO: wrap as a function
    return {
        "title": meta["title"] if "title" in meta else None,
        "date": parse_date(
            meta["date"],
            settings={"TIMEZONE": "US/Eastern", "RETURN_AS_TIMEZONE_AWARE": True},
        )
        if "date" in meta
        else None,
        "tags": list(meta["tags"]) if "tags" in meta else [],
        "draft": bool(meta["draft"]) if "draft" in meta else False,
        "template": meta["template"] if "template" in meta else None,
        "heading": meta["heading"] if "heading" in meta else None,
    }


# This TypeVar allows us to type hint a class method
T = TypeVar("T", bound="Page")


class Page:
    """A single page for the website.

    Args:
        source (str): Markdown page source
        website_path (str): path relative to the website root
        template (Template): Jinja2 template

    Attributes:
        (none)

    """

    _default_date = "2001-01-01"

    def __init__(self, source: str, website_path: str) -> None:
        """A Page is created from a source and with a path."""
        self.source = source
        self.website_path = website_path

        # Parse the source to HTML and metadata
        self.html, meta = parse_markdown(self.source)
        self.meta = check_metadata(meta)

    def __repr__(self) -> str:
        """String representation of a Page."""
        return f"Page({self.website_path})"

    def render(self, template: Optional[Template] = None) -> str:
        """Return a rendered page as a string.

        Each single-page template provides a "content" variable that should
        be bound to the HTML for the page. All other metadata are passed as
        parameters to be used.

        Args:
            template (Template): a Jinja2 Template overriding the internal one

        Returns:
            string: the rendered Page object

        """
        if template is None:
            return self.html
        return template.render(
            content=self.html,
            slug=self.slug,
            url=self.url,
            topdir=self.rootdir,
            escaped_html=self.escaped_html,
            **self.meta,
        )

    @property
    def url(self) -> str:
        """Return the HTML-extension URL for the page."""
        return self.slug + ".html"

    @property
    def slug(self) -> str:
        """Return the no-extension slug for the page."""
        return os.path.splitext(self.website_path)[0]

    @property
    def date(self) -> datetime:
        """Return a datetime object."""
        if self.meta["date"]:
            return self.meta["date"]
        return parse_date(self._default_date)

    @property
    def rootdir(self) -> str:
        """Return the "root" to return to."""
        dirname = os.path.dirname(self.website_path)
        return dirname

    @property
    def escaped_html(self) -> str:
        """Return escaped HTML for JSON feed."""
        return json.dumps(self.html)


# Load templates
def load_templates_from_dir(directory: str) -> Environment:
    """Produce an Environment targeted at a directory."""
    return Environment(loader=FileSystemLoader(directory))  # noqa: S701
