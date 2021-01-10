"""Compile a static site from Markdown files."""
import logging
import os
import re
import time
from datetime import datetime
from typing import Iterable, List

from jinja2 import Environment

from scrivo.blog import render_archives_page, render_tags_page
from scrivo.config import Config
from scrivo.ml import page_similarities
from scrivo.page import Page, load_templates_from_dir
from scrivo.utils import logtime

__all__ = [
    "increment_counter",
    "find_pages",
    "symlink_directory",
    "render_markdown_pages",
    "compile_site",
]


logging.basicConfig(format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)


@logtime
def increment_counter(dest: str) -> None:
    """Increment a Siracusa-style process counter."""
    mode = "r+" if os.path.exists(dest) else "a+"
    with open(dest, mode) as f:
        contents = f.read()
        count = int(contents) if contents else 0
        logger.info("Build count: %d", count + 1)
        f.seek(0)
        f.write(str(count + 1) + "\n")
        # From SO -- need this to get correct behavior
        f.truncate()


@logtime
def find_pages(directory: str, exts: Iterable[str] = ("md",)) -> List[str]:
    """Return a list of source paths within a top-level directory.

    Args:
        directory (str): top-level directory
        exts (iterable): file extensions to search for

    Returns:
        a collection of pages to be considered for processing

    """
    return [
        os.path.join(pwd, file)
        for pwd, _, files in os.walk(directory)
        for file in files
        if file.lower().endswith(tuple(exts))
    ]


@logtime
def fetch_pages(srcdir: str, include_drafts: bool = False) -> List[Page]:
    """Return a list of Page objects for processing."""
    pages = (Page.from_path(path, srcdir) for path in find_pages(srcdir))
    return [p for p in pages if include_drafts or not p.meta["draft"]]


@logtime
def symlink_directory(
    source: str,
    dest: str,
    hide_prefixes: Iterable[str] = "_.",
    hide_suffixes: Iterable[str] = ("md", "draft"),
) -> None:
    """Symlink a directory tree from one location to another.

    Only files are linked; directories are created as necessary.

    Args:
        source (str): source dir
        dest (str): dest dir
        hide_prefixes (iter[str]): ignore files starting with these values
        hide_suffixes (iter[str]): ignore files ending with these values

    Matching is case-insensitive (using `.lower()`).
    """
    for pwd, _, files in os.walk(source):
        relpwd = os.path.relpath(pwd, source)
        hidden = any(
            p.lower().startswith(tuple(hide_prefixes))
            for p in relpwd.split(os.path.sep)
        )
        if hidden:
            continue

        files = [
            f
            for f in files
            if not f.lower().startswith(tuple(hide_prefixes))
            and not f.lower().endswith(tuple(hide_suffixes))
        ]
        if not files:
            continue

        dest_dir = os.path.join(dest, relpwd)
        os.makedirs(dest_dir, exist_ok=True)

        # TODO: Check for dead links?
        for f in files:
            src_link = os.path.abspath(os.path.join(pwd, f))
            dest_link = os.path.abspath(os.path.join(dest_dir, f))
            if os.path.exists(dest_link):
                if not os.path.islink(dest_link):
                    logger.warning("path %s exists but isn't a link", dest_link)
                continue
            os.symlink(src_link, dest_link)


@logtime
def render_markdown_pages(pages: List[Page], tmpls: Environment, cfg: Config) -> None:
    """Render the standard collection on Markdown pages (not the generated ones).

    Args:
        pages (list[Page]): the pages
        tmpls (Environment): the templates
        cfg (Config): the website configuration
    """
    for page in pages:
        # Find a better way to do this -- source the template
        if page.meta["template"]:
            template = tmpls.get_template(page.meta["template"])
        elif page.is_blog:
            template = tmpls.get_template(cfg.templates.blog.default)
        else:
            template = tmpls.get_template(cfg.templates.default)
        # Prepare the way
        dest = os.path.join(cfg.site.build_dir, page.url)
        if not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))
        # Rendering
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(page.render(template))


@logtime
def generate_sitemap(urllist: List[str]) -> str:
    out = ['<?xml version="1.0" encoding="UTF-8"?>']
    out += ['<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    out += [f"<url>\n<loc>{url}</loc>\n</url>" for url in sorted(set(urllist))]
    out += ["</urlset>"]
    return "\n".join(out) + "\n"


@logtime
def compile_site(
    source_dir: str, build_dir: str, config: Config, include_drafts: bool = False
) -> None:
    """Build a website from source.

    Args:
        source_dir (str): directory containing source files
        build_dir (str): directory in which to write output files
        config (Config): site configuration
        include_drafts (bool): include drafts in output
    """
    if not os.path.isdir(source_dir):
        raise FileNotFoundError(f"source directory {source_dir} does not exist")
    if not os.path.isdir(build_dir):
        raise FileNotFoundError(f"build directory {build_dir} does not exist")

    # Symlink the non-generated contents (images, etc.) into the destination
    symlink_directory(
        source=source_dir,
        dest=build_dir,
        hide_prefixes="_.",
        hide_suffixes=("md", "draft", "pxm"),
    )

    # Read and render the pages
    pages = fetch_pages(source_dir, include_drafts)
    blogs = sorted((p for p in pages if p.is_blog), key=lambda p: p.date, reverse=True,)
    templates = load_templates_from_dir(config.templates.source_dir)
    sitemap_cache = [os.path.join(config.site.build_dir, p.website_path) for p in pages]

    # Bind in the text similarity for blog posts
    sim = page_similarities(pages)
    for page in blogs:
        page.related_pages = sim[page]

    render_markdown_pages(pages, templates, config)

    # Render generated pages ---------------------------------------------------

    # TODO: Clean these up
    # Index page
    timer_start = time.time()
    with open(os.path.join(config.site.build_dir, "blog/index.html"), "w") as f:
        template = templates.get_template(config.templates.blog.home)
        f.write(template.render(posts=blogs, template=template))
    logger.info("Rendered index page in %.03f s", time.time() - timer_start)

    # Archive pages
    timer_start = time.time()
    template = templates.get_template(config.templates.blog.archives)

    # Main archive
    url = os.path.join(config.site.build_dir, "blog/archive/index.html")
    sitemap_cache += [url]
    if not os.path.exists(url):
        os.makedirs(os.path.dirname(url))
    with open(url, "w") as f:
        f.write(render_archives_page(blogs, template))

    # Year and month archives
    for year in {b.date.year for b in blogs}:
        year_blogs = [b for b in blogs if b.date.year == year]
        url = os.path.join(config.site.build_dir, f"blog/{year:04d}/index.html")
        sitemap_cache += [url]
        with open(url, "w") as f:
            f.write(render_archives_page(year_blogs, template, year=year))
        for month in {b.date.month for b in year_blogs}:
            month_blogs = [b for b in year_blogs if b.date.month == month]
            url = os.path.join(
                config.site.build_dir, f"blog/{year:04d}/{month:02d}/index.html"
            )
            sitemap_cache += [url]
            with open(url, "w") as f:
                f.write(
                    render_archives_page(month_blogs, template, year=year, month=month)
                )
    logger.info("Rendered archive pages in %.03f s", time.time() - timer_start)

    # Tags page
    timer_start = time.time()
    url = os.path.join(config.site.build_dir, "blog/tags/index.html")
    sitemap_cache += [url]
    if not os.path.exists(url):
        os.makedirs(os.path.dirname(url))
    with open(url, "w") as f:
        template = templates.get_template(config.templates.blog.tags)
        f.write(render_tags_page(posts=blogs, template=template))
    logger.info("Rendered tags pages in %.03f s", time.time() - timer_start)

    # JSON feed
    timer_start = time.time()
    with open(os.path.join(config.site.build_dir, "blog", "feed.json"), "w") as f:
        template = templates.get_template(config.templates.feeds.json)
        f.write(template.render(posts=blogs))

    # RSS feed
    with open(os.path.join(config.site.build_dir, "blog", "rss.xml"), "w") as f:
        template = templates.get_template(config.templates.feeds.rss)
        f.write(template.render(posts=blogs, build_date=datetime.now()))
    logger.info("Rendered feeds in %.03f s", time.time() - timer_start)

    # Sitemap
    psages = []
    for pwd, _, files in os.walk(config.site.build_dir):
        relpath = os.path.relpath(pwd, config.site.build_dir).replace("./", "")
        if relpath.startswith("assets"):
            continue
        pages = [f for f in files if f.endswith(("html", "json", "xml", "pdf"))]
        if not pages:
            continue
        pages = ["" if p == "index.html" else p for p in pages]
        pages = [p.replace(".html", "") for p in pages]
        psages += [os.path.join("https://tshafer.com",relpath, p) for p in pages]
    for p in psages:
        print(p)

    # with open(os.path.join(config.site.build_dir, "sitemap.xml"), "w") as f:
    #     sitemap_cache = [
    #         "https://tshafer.com/"
    #         + re.sub(
    #             r"(index\.[^.]+$|\.md$)",
    #             "",
    #             os.path.relpath(c, config.site.build_dir),
    #             re.I,
    #         )
    #         for c in sitemap_cache
    #     ]
    #     f.write(generate_sitemap(sitemap_cache)

    # Only count full builds; here at the end
    if config.build_count_file is not None:
        path = os.path.join(
            config.site.source_dir, os.path.basename(config.build_count_file)
        )
        increment_counter(path)
