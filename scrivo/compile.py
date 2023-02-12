"""Compile a static site from directory contents."""

import logging
import os
import shlex
import subprocess as sp
from functools import reduce
from operator import add

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
    """Build and write a static website.

    Args:
        source_dir: Source directory
        output_dir: Output directory
        website_root: URL root for the domain
        template_dir: Jinja HTML template directory

    """
    tmpldir = Environment(loader=FileSystemLoader(template_dir))
    outdir = ensure_dir_exists(output_dir)
    rsync(source_dir, outdir)

    pages = collect_pages(source_dir)
    renders = reduce(add, (fn(pages, outdir, tmpldir) for fn in REGISTRY.values()))
    write_sitemap(renders, outdir, website_root)


def collect_pages(source_dir: str, exts: tuple[str, ...] = ("md",)) -> list[page]:
    """Locate Markdown pages in a tree.

    Args:
        source_dir: Source directory to search in for Markdown files
        exts: File extensions to treat as Markdown

    """
    paths = [
        os.path.abspath(os.path.join(pwd, file))
        for pwd, _, files in os.walk(source_dir)
        for file in filter(lambda f: f.lower().endswith(exts), files)
    ]
    pages = [
        page(path, os.path.relpath(path, source_dir))
        for path in tqdm(paths, unit="pg", desc="Rendering Markdown")
    ]

    log.info(f"Collected and processed {len(pages)} {s('page', pages)}")
    return pages


def rsync(src: str, dst: str) -> None:
    """Run rsync to update the output relative to the source."""
    command = shlex.split(f'rsync -rL --delete --exclude=".*" "{src}/" "{dst}/"')
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
