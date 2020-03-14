"""
Blog-specific utilities.

To consider:

- word clouds
- topic models
- Doc2Vec
- Blog post generator via char-level RCNN
- Sentiment analysis

"""
from typing import Iterable

from jinja2 import Template
from scrivo.page import Page


# For typing
Posts = Iterable[Page]


def render_index_page(posts: Posts, template: Template) -> str:
    """Render a blog index page according to a template."""
    return template.render(posts=posts, )


def render_tags_page(posts: Posts, template: Template) -> str:
    """Render a blog tags page according to a template."""
    return ''


def render_archives_page(posts: Posts, template: Template) -> str:
    """Render a blog archives page according to a template."""
    return ''
