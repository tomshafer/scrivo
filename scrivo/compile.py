"""Compile a static site from directory contents."""

import logging
import os
import shlex
import subprocess as sp
from typing import Any, Optional, Sized

from jinja2 import Environment, FileSystemLoader, Template
from tqdm.auto import tqdm

from scrivo.markdown import md2html

log = logging.getLogger(__name__)


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


RENDER_REGISTRY = dict()


def compile_site(source_dir: str, output_dir: str, template_dir: str) -> None:
    """Build and export a static website.

    Args:
        source_dir (str): Static site source directory.
        output_dir (str): Output directory.
        template_dir (str): Jinja HTML template directory.

    """
    templates = Environment(loader=FileSystemLoader(template_dir))
    output_dir = ensure_dir_exists(output_dir)
    rsync(source_dir, output_dir)

    pages = collect_pages(source_dir)
    render_pages(pages, output_dir, templates)

    for target in RENDER_REGISTRY:
        log.info("Rendering...")
    # Generate various programmatic pages
    # Some kind of registry?
    # Feeds
    # Tags
    # Archives
    # Blog index
    #


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


def pl(word: str, collection: Sized, suffix: str = "s") -> str:
    """Pluralize a word based on collection size.

    Args:
        word (str): The unit of measure ot be pluralized.
        collection (Sized): The collection to measure for pluralization.
        suffix (str): Optional suffix to atttach if is needed.

    Returns:
        str: A pluralized version of `word` if needed.

    """
    return word + suffix * (len(collection) != 1)


def collect_pages(
    source_dir: str,
    exts: tuple[str, ...] = ("md", "mdown", "text"),
) -> list[page]:
    """Locate Markdown pages in a tree.

    Args:
        source_dir (str): Source directory to search for Markdown files.
        exts (tuple[str]): File extensions to treat as Markdown.

    Returns:
        list[str]: A collection of Markdown files.

    """
    paths = [
        os.path.abspath(os.path.join(pwd, file))
        for pwd, _, files in os.walk(source_dir)
        for file in filter(lambda f: f.lower().endswith(tuple(exts)), files)
    ]
    pages = [
        page(path, os.path.relpath(path, source_dir))
        for path in tqdm(paths, unit="pg", desc="Rendering Markdown")
    ]

    log.info(f"Collected and processed {len(pages)} {pl('page', pages)}")
    return pages


def rsync(src: str, out: str) -> None:
    """Run rsync to update the output relative to the source.

    Args:
        src (str): Static site source directory.
        out (str): Output directory.
    """
    command = shlex.split(f'rsync -rL --delete --exclude=".*" "{src}/" "{out}/"')
    log.debug(f"rsync command = `{' '.join(command)}`")
    sp.run(command)


def ensure_dir_exists(dirpath: str) -> str:
    """Create a directory if it doesn't already exist.

    Args:
        dirpath (str): The directory to create if not already existing.

    Returns:
        str: The absolute path to the target directory.

    """
    absdir = os.path.abspath(dirpath)
    if not os.path.exists(absdir):
        log.info(f"Creating directory {absdir}")
        os.mkdir(absdir)
    return absdir
