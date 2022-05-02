"""Compile a static site from directory contents."""

import logging
import os
import shlex
import subprocess as sp

from jinja2 import Environment, FileSystemLoader
from tqdm.auto import tqdm

from scrivo.pages import page
from scrivo.rendering import REGISTRY
from scrivo.utils import ensure_dir_exists, s

log = logging.getLogger(__name__)


def compile_site(
    source_dir: str,
    output_dir: str,
    website_root: str,
    template_dir: str,
) -> None:
    """Build and export a static website.

    Args:
        source_dir (str): Static site source directory.
        output_dir (str): Output directory.
        website_root (str): URL root for the domain.
        template_dir (str): Jinja HTML template directory.

    """
    templates = Environment(loader=FileSystemLoader(template_dir))
    output_dir = ensure_dir_exists(output_dir)
    rsync(source_dir, output_dir)

    pages = collect_pages(source_dir)

    rendered_pages = []
    for target in REGISTRY:
        log.debug(f'Dispatching job "{target}"')
        rendered_pages += REGISTRY[target](pages, output_dir, templates)

    write_sitemap(rendered_pages, output_dir, website_root)


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


def write_sitemap(urls: list[str], basedir: str, webroot: str) -> None:
    """Write a Google-compatible sitemap text file.

    The URLs come from two sources:

        1. Generated/rendered pages
        2. A crawl of select rsync'd files (e.g., PDFs)

    Args:
        urls: List of rendered URLs during compilation
        basedir: Output directory root
        webroot: Base URL for the website

    """
    sitemap_urls = []
    for url in urls:
        clean_url = url.removesuffix(".html").removesuffix("index")
        sitemap_urls += [f"{webroot.rstrip('/')}/{clean_url}"]
    for pwd, _, files in os.walk(basedir):
        for file in filter(lambda x: x.lower().endswith(".pdf"), files):
            clean_url = os.path.relpath(os.path.join(pwd, file), basedir)
            sitemap_urls += [f"{webroot.rstrip('/')}/{clean_url}"]

    with open(os.path.join(basedir, "sitemap.txt"), "w") as f:
        f.writelines(map(lambda u: u + "\n", sorted(sitemap_urls)))
