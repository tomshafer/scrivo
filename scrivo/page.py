"""A Page represents a single web document.

Pages originate in Markdown and are to be rendered as HTML.
"""
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional, Tuple, TypeVar

from jinja2 import Environment, FileSystemLoader, Template
from markdown import Markdown

from scrivo.markdown import YAMLMetadataExtension
from scrivo.utils import get_tz

__all__ = ["Page", "load_templates_from_dir"]


# This is the entire configuration of the Markdown parser
_md_parser = Markdown(
    output_format="html5",  # type: ignore
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


def get_default(dct, key, default=None, fn=None):
    """Get a value from a dict and transform if not the default."""
    value = dct.get(key, default)
    if fn is not None and value != default:
        return fn(value)
    return value


def parse_date(x: str) -> datetime:
    """Parse a date string so it is timezone aware.

    Args:
        x: A date string.

    Returns:
        The timezone-aware datetime object.

    """
    date = datetime.strptime(x, "%Y-%m-%d %I:%M %p")
    tz = get_tz()
    return date.replace(tzinfo=tz)


def set_metadata(raw_meta: Dict) -> Dict[str, Any]:
    """Ensure a Page has the minimum expected metadata.

    We currently check for:

      - title
      - date
      - tags
      - template
      - draft
      - html_desc
      - html_head

    Additional metadata is left as-is and carried through.

    Args:
        raw_meta (dict): metadata from the Markdown parser

    Returns:
        (dict[str, Any]) a dict guaranteed to have the necessary properties

    """
    meta = {
        "title": get_default(raw_meta, "title", None),
        "date": get_default(
            dct=raw_meta,
            key="date",
            default=None,
            fn=parse_date,
        ),
        "tags": get_default(raw_meta, "tags", ["miscellaneous"]),
        "template": get_default(raw_meta, "template", None),
        "draft": get_default(raw_meta, "draft", False, bool),
        "html_desc": get_default(raw_meta, "html_desc", None),
        "html_head": get_default(raw_meta, "html_head", None),
    }

    # Make sure tags is a list/collection
    if not isinstance(meta["tags"], (list, tuple, set)):
        meta["tags"] = [meta["tags"]]

    # Pass through any other data
    for k in set(raw_meta.keys()).difference(meta.keys()):
        meta[k] = raw_meta[k]

    return meta


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
    meta: Dict = set_metadata(_md_parser.metadata)  # type: ignore
    return html, meta


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

    def __init__(self, source: str, website_path: str) -> None:
        """A Page is created from a source and with a path."""
        self.source = source
        self.website_path = website_path

        # Parse the source to HTML and metadata
        self.html, self.meta = parse_markdown(self.source)

        # Allow for related pages
        self.related_pages: Dict[float, Page] = {}

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
            related_pages=self.related_pages,
            post=self,
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
        return datetime(year=2001, month=1, day=1)

    @property
    def rootdir(self) -> str:
        """Return the "root" to return to."""
        dirname = os.path.dirname(self.website_path)
        return dirname

    @property
    def escaped_html(self) -> str:
        """Return escaped HTML for JSON feed."""
        return json.dumps(self.html)

    @property
    def is_blog(self) -> bool:
        """Does this Page look blog-related?"""
        return self.website_path.startswith("blog/")

    def count_related_pages(
        self, threshold: float = 1.0, only_blog: bool = False
    ) -> float:
        """Return the number of related posts with a given score."""
        return sum(
            score >= threshold
            for score, page in self.related_pages.items()
            if not only_blog or page.is_blog
        )

    @classmethod
    def from_path(cls, src: str, website_root: str) -> "Page":
        """Return a new Page read from a file.

        Args:
            src (str): path to the paper
            website_root (str): the local root of the website

        Return:
            (Page) a new Page object
        """
        with open(src, "r") as f:
            return Page(f.read(), os.path.relpath(src, website_root))


# Load templates
def load_templates_from_dir(directory: str) -> Environment:
    """Produce an Environment targeted at a directory."""
    return Environment(loader=FileSystemLoader(directory))  # noqa: S701
