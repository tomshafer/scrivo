"""Blog-specific utilities.

To consider:

- word clouds
- topic models
- Doc2Vec
- Blog post generator via char-level RCNN
- Sentiment analysis

"""
from collections import OrderedDict, defaultdict
from datetime import datetime
from typing import DefaultDict, Iterable, List, Optional

from dateparser import parse as parse_date
from jinja2 import Template

from scrivo.page import Page

__all__ = ["render_archives_page", "render_tags_page"]


# For typing
Posts = Iterable[Page]


def render_archives_page(
    posts: Posts,
    template: Template,
    year: Optional[int] = None,
    month: Optional[int] = None,
) -> str:
    """Render a blog archives page according to a template.

    Args:
        posts: a collection of blog posts
        template: a Jinja2 template
        year (optional, int): the archive year (for formatting)
        month (optional, int): the archive month (for formatting)

    """
    archive_date: Optional[datetime] = None
    date_format: str = "%B %d, %Y"
    if year is not None:
        archive_str = f"{year:04d}"
        if month is not None:
            archive_str += f"-{month:02d}-01"
            archive_date = parse_date(archive_str).strftime("%B %Y")
        else:
            date_format = "%B %Y"
            archive_str += "-01-01"
            archive_date = parse_date(archive_str).strftime("%Y")
    return template.render(
        posts=sorted(posts, key=lambda p: p.date),
        archive_title=archive_date,
        date_format=date_format,
    )


def render_tags_page(posts: Posts, template: Template) -> str:
    """Render blog archived by tag.

    Args:
        posts (Posts): a collection of blog posts
        template: a Jinja2 template

    Returns:
        a rendered document with blogs organized by tag

    """
    tagged_posts: DefaultDict[str, List[Page]] = defaultdict(lambda: [])
    for post in sorted(posts, key=lambda p: p.date, reverse=True):
        if post.meta["tags"]:
            for tag in post.meta["tags"]:
                tagged_posts[tag] += [post]
        else:
            tagged_posts["miscellaneous"] += [post]
    # Hack to re-sort untagged to the bottom
    out = OrderedDict()
    for k in sorted(set(tagged_posts).difference({"miscellaneous"})):
        out[k] = tagged_posts[k]
    out["miscellaneous"] = tagged_posts["miscellaneous"]
    return template.render(tags=out)
