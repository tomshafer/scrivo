"""Compile a static site from directory contents."""

import logging
import os
import shlex
import subprocess as sp

from jinja2 import Environment, FileSystemLoader
from tqdm.auto import tqdm

from scrivo.pages import page
from scrivo.rendering import REGISTRY
from scrivo.utils import s

log = logging.getLogger(__name__)


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

    for target in REGISTRY:
        log.debug(f'Dispatching job "{target}"')
        REGISTRY[target](pages, output_dir, templates)


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

    log.info(f"Collected and processed {len(pages)} {s('page', pages)}")
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
