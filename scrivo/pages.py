"""Processing and rendering individual pages."""

import os
from typing import Any, Optional

from jinja2 import Environment, Template

from scrivo.markdown import md2html


class page:
    """Representation of a Markdown page."""

    def __init__(self, srcpath: str, relpath: str) -> None:
        """Read and render a Markdown file to HTML + metadata.

        Args:
            srcpath (str): Path to the source Markdown file.
            relpath (str): Path to the source file relative to root.

        """
        self.srcpath = srcpath
        self.relpath = relpath
        with open(srcpath) as f:
            self.text = f.read()
            self.html, self.meta = md2html(self.text)

    def __repr__(self) -> str:
        """Represent a page object as a string.

        Returns:
            str: A page identifier.

        """
        return f"<page({self.relpath})>"

    def render(self, tmpl: Optional[Template] = None) -> str:
        """Render a page as pure HTML or into a Jinja template.

        Args:
            tmpl (Template, optional): A Jinja template.

        Returns:
            str: The rendered page contents.

        """
        return tmpl.render(**self.to_template_dict()) if tmpl is not None else self.html

    @property
    def relpath_html(self) -> str:
        """Construct the relative path of a putative HTML file for this page.

        Returns:
            str: The '.html' equivalent of `self.relpath`.

        """
        return f"{os.path.splitext(self.relpath)[0]}.html"

    def to_template_dict(self) -> dict[str, Any]:
        """Render page as a dict for templating.

        Returns:
            dict[str, Any]: Union of the rendered page contents and metadata.

        """
        return {"content": self.html} | self.meta

    def destpath_html(self, base: str) -> str:
        """Compute a destination HTML path given a new base.

        Args:
            base (str): The base of the new directory tree.

        Returns:
            str: New HTML-extension absolute path.

        """
        return os.path.abspath(os.path.join(base, self.relpath_html))


def render_pages(pages: list[page], dst: str, templates: Environment) -> None:
    """Render individual markdown pages into the destination.

    Args:
        pages (list[page]): The list of pages to render.
        dst (str): Destination directory, for path manipulation.
        templates (Environment): Jinja template environment.

    """
    for page in pages:
        template = resolve_page_template(page, templates)
        with open(page.destpath_html(dst), "w") as outf:
            outf.write(page.render(template))


def resolve_page_template(page: page, templates: Environment) -> Template:
    """Compute which template to apply to a page.

    Args:
        page (page): Page to be templated.
        templates (Environment): A Jinja templating environment.

    Returns:
        Template: Resolved template for the page.

    If a 'template' is specified in a page's metadata then we
    take that as the truth and return the specified tempate.
    Without that, we start at `BASEDIR/main.html` and walk up the
    tree from there, trying every `main.md` we can find.

    Example:
        The page work/physics/index.md tries the following
        templates in order:

        * `meta["template"]`, if specified
        * work/physics/main.html
        * work/main.html
        * main.html

    """
    # Easy path: We've specified the template in metadata
    template: Optional[str] = page.meta.get("template")
    if template is not None:
        return templates.get_template(template)

    # Harder path: Walk backwards to find the parent template, named <dir>/main.html
    base = os.path.dirname(page.relpath_html)
    template_set = set(templates.list_templates())
    while True:
        test_path = os.path.join(base, "main.html")
        if test_path in template_set:
            return templates.get_template(test_path)

        # Remove the trailing directory: "/<dir>". Returns -1 if none available.
        slash_idx = base.rfind("/")
        if slash_idx == -1:
            break
        base = base[:slash_idx]

    return templates.get_template("main.html")
