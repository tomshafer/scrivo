"""Compile a static site from directory contents."""

import logging
import os
import shlex
import subprocess as sp
from dataclasses import dataclass
from typing import Sized

log = logging.getLogger(__name__)


@dataclass
class page:
    """Representation of a single Markdown page."""

    srcpath: str
    relpath: str

    def rebase(self, new: str) -> str:
        """Return the absolute path of this page in a new tree.

        Args:
            new (str): Top of the new directory tree.

        Returns:
            str: An absolute filesystem path in the new tree.

        """
        return os.path.abspath(os.path.join(new, self.relpath))


def compile_site(source_dir: str, output_dir: str) -> None:
    """Build and export a static website.

    Args:
        source_dir (str): Static site source directory.
        output_dir (str): Output directory.

    """
    output_dir = ensure_dir_exists(output_dir)
    rsync(source_dir, output_dir)

    # Run markdown against every markdown file
    pages = collect_pages(source_dir)
    render_pages(pages, source_dir, output_dir)

    # Generate various programmatic pages
    # Some kind of registry?
    # Feeds
    # Tags
    # Archives
    # Blog index
    #


def render_pages(pages: list[page], src: str, dst: str) -> None:
    """Render individual markdown pages into the destination.

    Args:
        pages (list[page]): The list of pages to render.
        src (str): Source directory, for path manipulation.
        dst (str): Destination directory, for path manipulation.

    """
    # FIXME: Generating "output.html" next to "output/"
    for page in pages:
        dpath = os.path.split(page.rebase(dst))[0] + ".html"
        with open(dpath, "w") as fout:
            with open(page.srcpath, "r") as fin:
                fout.write(fin.read())


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
    pages = []
    for pwd, _, files in os.walk(source_dir):
        for file in filter(lambda f: f.lower().endswith(tuple(exts)), files):
            srcpath = os.path.abspath(os.path.join(pwd, file))
            relpath = os.path.relpath(srcpath, source_dir)
            pages += [page(srcpath=srcpath, relpath=relpath)]
    log.info(f"Collected {len(pages)} Markdown {pl('page', pages)}")
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
