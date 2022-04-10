"""Page rendering utilities."""

import logging
import os
from collections import defaultdict
from datetime import date
from typing import Callable

from jinja2 import Environment

from scrivo.pages import collect_blog_post_pages, page, render_pages
from scrivo.utils import ensure_dir_exists

log = logging.getLogger(__name__)

# The registry tracks the various jobs needed to build the blog
REGISTRY: dict[str, Callable[[list[page], str, Environment], list[str]]] = {}


def render_blog_index(
    pages: list[page],
    outdir: str,
    templates: Environment,
) -> list[str]:
    """Render blog/index.html.

    Args:
        pages (list[page]): All pages known to the blogging engine.
        outdir (str): Output root directory.
        templates (Environment): Jinja templating environment.

    Returns:
        list[str]: List of (relative paths for) pages generated.

    """
    target = "blog/index.html"
    log.info(f"Rendering {target}")

    template = templates.get_template(target)
    with open(os.path.join(outdir, target), "w") as outf:
        outf.write(template.render(posts=collect_blog_post_pages(pages)))

    return [target]


def render_archive(
    pages: list[page],
    outdir: str,
    templates: Environment,
) -> list[str]:
    """Render main, year, and year/month blog archives.

    Args:
        pages (list[page]): All pages known to the blogging engine.
        outdir (str): Output root directory.
        templates (Environment): Jinja templating environment.

    Returns:
        list[str]: List of (relative paths for) pages generated.

    """
    rendered_pages = []
    blog_posts = collect_blog_post_pages(pages)

    # Main archive
    log.info("Rendering blog/archive/index.html")
    ensure_dir_exists(os.path.join(outdir, "blog/archive"))

    template = templates.get_template("blog/archive.html")
    target = "blog/archive/index.html"
    with open(os.path.join(outdir, target), "w") as outf:
        outf.write(template.render(posts=blog_posts))
        rendered_pages += [target]

    # Month and year archives
    template = templates.get_template("blog/archive.html")  # FIXME
    post_dates = {p.date.date() for p in collect_blog_post_pages(pages)}

    log.info("Rendering blog/<year>/index.html")
    years = {d.year for d in post_dates}
    for year in years:
        subset = [p for p in blog_posts if p.date.year == year]
        ensure_dir_exists(os.path.join(outdir, f"blog/{year}"))
        target = f"blog/{year}/index.html"
        with open(os.path.join(outdir, target), "w") as outf:
            outf.write(template.render(posts=subset))
            rendered_pages += [target]

    log.info("Rendering blog/<year>/<month>/index.html")
    year_months = {date(year=d.year, month=d.month, day=1) for d in post_dates}
    for ym in year_months:
        year, month = ym.year, ym.month
        subset = [
            page
            for page in blog_posts
            if page.date.year == year and page.date.month == month
        ]
        target = f"blog/{year}/{month:02d}/index.html"
        ensure_dir_exists(os.path.join(outdir, os.path.dirname(target)))
        with open(os.path.join(outdir, target), "w") as outf:
            outf.write(template.render(posts=subset))
            rendered_pages += [target]

    return rendered_pages


def render_blog_tag_pages(
    pages: list[page],
    outdir: str,
    templates: Environment,
) -> list[str]:
    """Render blog/tags/index.html.

    Args:
        pages (list[page]): All pages known to the blogging engine.
        outdir (str): Output root directory.
        templates (Environment): Jinja templating environment.

    Returns:
        list[str]: List of (relative paths for) pages generated.

    """
    log.info("Rendering blog/tags/index.html")

    posts = collect_blog_post_pages(pages)
    template = templates.get_template("blog/tags.html")

    tagged_posts: dict[str, list[page]] = defaultdict(lambda: [])
    for post in sorted(posts, key=lambda p: p.date, reverse=True):
        if post.meta["tags"] is None:
            continue
        for tag in post.meta["tags"]:
            tagged_posts[tag].append(post)

    target = "blog/tags/index.html"
    ensure_dir_exists(os.path.join(outdir, os.path.dirname(target)))
    with open(os.path.join(outdir, target), "w") as outf:
        outf.write(template.render(posts=posts))

    return [target]


def render_json_feed(
    pages: list[page],
    outdir: str,
    templates: Environment,
) -> list[str]:
    """Render JSON feed.

    Args:
        pages (list[page]): All pages known to the blogging engine.
        outdir (str): Output root directory.
        templates (Environment): Jinja templating environment.

    Returns:
        list[str]: List of (relative paths for) pages generated.

    """
    log.info("Rendering blog/feed.json")
    template = templates.get_template("feeds/feed.json")
    posts = collect_blog_post_pages(pages)
    ensure_dir_exists(os.path.join(outdir, "blog"))
    target = "blog/feed.json"
    with open(os.path.join(outdir, target), "w") as outf:
        outf.write(template.render(posts=posts))

    return [target]


def render_xml_feeds(
    pages: list[page],
    outdir: str,
    templates: Environment,
) -> list[str]:
    """Render RSS feeds.

    Args:
        pages (list[page]): All pages known to the blogging engine.
        outdir (str): Output root directory.
        templates (Environment): Jinja templating environment.

    Returns:
        list[str]: List of (relative paths for) pages generated.

    """
    rendered_pages = []

    feeds = ["rss.xml", "rss-r.xml"]
    posts = collect_blog_post_pages(pages)
    ensure_dir_exists(os.path.join(outdir, "blog"))
    for feed in feeds:
        log.info(f"Rendering blog/{feed}")
        template = templates.get_template(f"feeds/{feed}")
        target = f"blog/{feed}"
        with open(os.path.join(outdir, target), "w") as outf:
            outf.write(template.render(posts=posts))
            rendered_pages += [target]

    return rendered_pages


# def generate_sitemap(
#     pages: list[page],
#     outdir: str,
#     templates: Environment,
# ) -> None:
#     pass


REGISTRY["Individual pages"] = render_pages
REGISTRY["Blog index"] = render_blog_index
REGISTRY["Blog archives"] = render_archive
REGISTRY["Blog tags"] = render_blog_tag_pages
REGISTRY["JSON feed"] = render_json_feed
REGISTRY["XML feeds"] = render_xml_feeds
