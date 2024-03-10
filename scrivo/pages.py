"""Processing and rendering individual pages."""

import logging
import os
from collections import defaultdict
from datetime import datetime
from typing import Any

from jinja2 import Environment as Env, Template

from scrivo.markdown import parse_markdown

log = logging.getLogger(__name__)


__all__ = ["page"]


class page:
    """Representation of a Markdown page."""

    def __init__(self, srcpath: str, relpath: str) -> None:
        """Read and render a Markdown file to HTML + metadata.

        Args:
            srcpath: Source Markdown file path on disk
            relpath: Source file path relative to the webroot

        """
        self.srcpath = srcpath
        self.relpath = relpath
        with open(srcpath) as f:
            self.text = f.read()
            self.plain, self.html, _meta = parse_markdown(self.text)
            self.meta = defaultdict(lambda: None, _meta)

    def __repr__(self) -> str:
        return f"<page({self.relpath})>"

    def render(self, tmpl: Template | None = None) -> str:
        """Render a page as pure HTML or into a Jinja template."""
        return tmpl.render(**self.to_template_dict()) if tmpl is not None else self.html

    @property
    def relpath_html(self) -> str:
        """Construct the relative path of a putative HTML file for this page."""
        return f"{os.path.splitext(self.relpath)[0]}.html"

    @property
    def date(self) -> datetime:
        """Return page date metadata as a true datetime."""
        return datetime.strptime(self.meta["date"], "%Y-%m-%d %I:%M %p")

    def to_template_dict(self) -> dict[str, Any]:
        """Unify metadata and page content."""
        return {"content": self.html} | self.meta

    def destpath_html(self, base: str) -> str:
        """Compute a destination HTML path given a new base."""
        return os.path.abspath(os.path.join(base, self.relpath_html))


def render_pages(pages: list[page], dest: str, templates: Env) -> list[str]:
    """Render individual markdown pages into the destination.

    Args:
        pages: Collection of pages to render
        dst: Destination directory, for path manipulation
        templates: Jinja template environment

    Returns:
        Relative paths of written HTML files.

    """
    html_pages = []
    for page in pages:
        log.info(f"Rendering {page.relpath_html}")
        template = resolve_page_template(page, templates)
        dest_html = page.destpath_html(dest)
        with open(dest_html, "w") as outf:
            outf.write(page.render(template))
            html_pages.append(page.relpath_html)
    return html_pages


def resolve_page_template(page: page, templates: Env) -> Template:
    """Compute which template to apply to a page.

    If a 'template' is specified in a page's metadata then we
    take that as the truth and return the specified tempate.
    Without that, we start at `BASEDIR/main.html` and walk up the
    tree from there, trying every `main.md` we can find.

    Example:
        The page work/physics/index.md tries the following
        templates in order:

        * `meta["template"]`, if specified
        * work/physics/main.html
        * work/physics.html
        * work/main.html
        * main.html

    Args:
        page: Page to be templated
        templates: Jinja templating environment

    Returns:
        The resolved template for the page.

    """
    # Easy path: We've specified the template in metadata
    template: str | None = page.meta.get("template")
    if template is not None:
        return templates.get_template(template)

    # Harder path: Walk backwards to find the parent template, named <dir>/main.html
    base = os.path.dirname(page.relpath_html)
    template_set = set(templates.list_templates())

    matched_template = "main.html"
    while True:
        # /path/main.html
        test_path = os.path.join(base, "main.html")
        if test_path in template_set:
            matched_template = test_path
            break

        # /path.html
        test_path = f"{base}.html"
        if test_path in template_set:
            matched_template = test_path
            break

        # Remove the trailing directory: "/<dir>".
        # Returns -1 if none available.
        if slash_idx := base.rfind("/") == -1:
            break
        base = base[:slash_idx]

    result = templates.get_template(matched_template)
    log.debug(f"Mapped {page} => {result}")
    return result


def collect_blog_post_pages(pages: list[page], drafts: bool = False) -> list[page]:
    """Provide a list of blog posts from a page collection."""
    return [
        page
        for page in pages
        if page.relpath.startswith("blog/") and (drafts or not page.meta["draft"])
    ]
