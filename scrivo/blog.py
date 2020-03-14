"""
Blog-specific utilities.

To consider:

- word clouds
- topic models
- Doc2Vec
- Blog post generator via char-level RCNN
- Sentiment analysis

"""
from typing import Iterable, Optional
from datetime import datetime
from jinja2 import Template
from dateparser import parse as parse_date
from scrivo.page import Page


# For typing
Posts = Iterable[Page]


def render_index_page(posts: Posts, template: Template) -> str:
    """Render a blog index page according to a template."""
    return template.render(posts=posts)


def render_tags_page(posts: Posts, template: Template) -> str:
    """Render a blog tags page according to a template."""
    raise NotImplementedError
    return ''


def render_archives_page(
        posts: Posts,
        template: Template,
        year: Optional[int] = None,
        month: Optional[int] = None
) -> str:
    """Render a blog archives page according to a template.

    Args:
        posts: a collection of blog posts
        template: a Jinja2 template
        year (optional, int): the archive year (for formatting)
        month (optional, int): the archive month (for formatting)

    """
    archive_date: Optional[datetime] = None
    date_format: str = '%B %d, %Y'
    if year is not None:
        archive_str = f'{year:04d}'
        if month is not None:
            archive_str += f'-{month:02d}-01'
            archive_date = parse_date(archive_str).strftime('%B %Y')
        else:
            date_format = '%B %Y'
            archive_str += '-01-01'
            archive_date = parse_date(archive_str).strftime('%Y')
    return template.render(
        posts=sorted(posts, key=lambda p: p.date),
        archive_title=archive_date,
        date_format=date_format)
