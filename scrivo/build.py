"""Compile a static site from Markdown files."""
import logging
import os
from datetime import datetime
from typing import Iterable, List

from scrivo.blog import render_archives_page, render_tags_page
from scrivo.config import Config
from scrivo.page import Page, load_templates_from_dir

# cf: https://docs.python.org/3/howto/logging.html
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    fmt="{name} {levelname:<8s} {funcName} :: {message}", style="{"
)
ch.setFormatter(formatter)
logger.addHandler(ch)


def increment_counter(dest: str) -> None:
    """Increment a Siracusa-style process counter."""
    mode = "r+" if os.path.exists(dest) else "a+"
    with open(dest, mode) as f:
        contents = f.read()
        count = int(contents) if contents else 0
        logger.info("build count: %d", count + 1)
        f.seek(0)
        f.write(str(count + 1) + "\n")
        # From SO -- need this to get correct behavior
        f.truncate()


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
                    logger.warning("path %s exists but isn't already a link", dest_link)
                continue
            os.symlink(src_link, dest_link)


def compile_site(source_dir: str, build_dir: str, config: Config) -> None:
    """Build a website from source.

    Args:
        source_dir (str): directory containing source files
        build_dir (str): directory in which to write output files
        config (Config): site configuration
    """
    if not os.path.isdir(source_dir):
        raise FileNotFoundError(f"source directoy {source_dir} does not exist")
    if not os.path.isdir(build_dir):
        raise FileNotFoundError(f"build directoy {build_dir} does not exist")

    symlink_directory(source_dir, build_dir)

    blogs: List[Page] = []
    templates = load_templates_from_dir(config.templates.source_dir)

    for path in find_pages(source_dir):
        with open(path, "r") as f:
            page = Page(source=f.read(), website_path=os.path.relpath(path, source_dir))
        # Track blogs
        if page.website_path.startswith("blog/"):
            blogs += [page]
        # Think through a better way to do this
        if page.meta["template"]:
            template = templates.get_template(page.meta["template"])
        elif page.website_path.startswith("blog/"):
            template = templates.get_template(config.templates.blog.default)
        else:
            template = templates.get_template(config.templates.default)
        # Destination paths
        dest = os.path.join(config.site.build_dir, page.url)
        if not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))
        # Rendering
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(page.render(template))

    # Blogs get their own collection
    blogs = sorted(
        (b for b in blogs if not b.meta["draft"]), key=lambda p: p.date, reverse=True
    )

    # Index page
    with open(os.path.join(config.site.build_dir, "blog/index.html"), "w") as f:
        template = templates.get_template(config.templates.blog.home)
        f.write(template.render(posts=blogs, template=template))

    # Archive pages
    template = templates.get_template(config.templates.blog.archives)

    # Main archive
    url = os.path.join(config.site.build_dir, f"blog/archive/index.html")
    if not os.path.exists(url):
        os.makedirs(os.path.dirname(url))
    with open(url, "w") as f:
        f.write(render_archives_page(blogs, template))

    # Year and month archives
    for year in {b.date.year for b in blogs}:
        year_blogs = [b for b in blogs if b.date.year == year]
        url = os.path.join(config.site.build_dir, f"blog/{year:04d}/index.html")
        with open(url, "w") as f:
            f.write(render_archives_page(year_blogs, template, year=year))
        for month in {b.date.month for b in year_blogs}:
            month_blogs = [b for b in year_blogs if b.date.month == month]
            url = os.path.join(
                config.site.build_dir, f"blog/{year:04d}/{month:02d}/index.html"
            )
            with open(url, "w") as f:
                f.write(
                    render_archives_page(month_blogs, template, year=year, month=month)
                )

    # Tags page
    url = os.path.join(config.site.build_dir, "blog/tags/index.html")
    if not os.path.exists(url):
        os.makedirs(os.path.dirname(url))
    with open(url, "w") as f:
        template = templates.get_template(config.templates.blog.tags)
        f.write(render_tags_page(posts=blogs, template=template))

    # JSON feed
    with open(os.path.join(config.site.build_dir, "blog", "feed.json"), "w") as f:
        template = templates.get_template(config.templates.feeds.json)
        f.write(template.render(posts=blogs))

    # RSS feed
    with open(os.path.join(config.site.build_dir, "blog", "rss.xml"), "w") as f:
        template = templates.get_template(config.templates.feeds.rss)
        f.write(template.render(posts=blogs, build_date=datetime.now()))

    # Conly count full builds; here at the end
    if config.build_count_file is not None:
        path = os.path.join(
            config.site.source_dir, os.path.basename(config.build_count_file)
        )
        increment_counter(path)
