import os
from datetime import datetime
from typing import List, Iterable

from scrivo import blog
from scrivo.config import Config
from scrivo.page import Page
from scrivo.template import load_from_directory


def compile(source_dir: str, build_dir: str, config: Config) -> None:
    """
    Build a website from source.

    Parameters
    ----------
    source_dir : str
        Directory containing source files. This will be mirrored to build_dir.
    build_dir : str
        Directory in which to write output files.

    Returns
    -------
    None

    """
    if not os.path.isdir(source_dir):
        raise FileNotFoundError(f'source directoy {source_dir} does not exist')
    if not os.path.isdir(build_dir):
        raise FileNotFoundError(f'build directoy {build_dir} does not exist')

    templates = load_from_directory(config.templates.source_dir)
    page_paths = find_pages(source_dir)

    # Render pages in-place
    pages: List[Page] = []
    for path in page_paths:
        with open(path, 'r') as f:
            page = Page(
                source=f.read(),
                website_path=os.path.relpath(path, source_dir))
            pages += [page]
        # Destination paths
        dest = os.path.join(config.site.build_dir, page.url)
        if not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))
        # Template
        template = templates.get_template(
            config.templates.default
            if not page.meta['template']
            else page.meta['template'])
        # fixme: this is awful
        if page.website_path.find('blog/2') != -1:
            template = templates.get_template(config.templates.blog.default)
        with open(dest, 'w', encoding='utf-8') as fh:
            fh.write(page.render(template))

    # Render blogs to index, archive, etc.
    # These are weird b/c they take in collections of pages
    blogs = sorted((
        p for p in pages
        if p.website_path.find('blog/') != -1
    ), key=lambda p: p.date, reverse=True)
    with open(os.path.join(config.site.build_dir, 'blog', 'index.html'), 'w') as f:
        f.write(blog.render_index_page(
            posts=blogs,
            template=templates.get_template(config.templates.blog.home)))
    with open(os.path.join(config.site.build_dir, 'blog', 'feed.json'), 'w') as f:
        f.write(templates.get_template(config.templates.feeds.json).render(posts=blogs))
    with open(os.path.join(config.site.build_dir, 'blog', 'rss.xml'), 'w') as f:
        f.write(templates.get_template(config.templates.feeds.rss).render(
            posts=blogs, build_date=datetime.now()))

    # todo: tags, archives, etc.


def find_pages(directory: str, exts: Iterable[str] = ('md',)) -> List[str]:
    """Return a list of source paths within a top-level directory.

    Args:
        directory (str): top-level directory
        exts (iterable): file extensions to search for

    Returns:
        list: a collection of pages to be considered for processing

    """
    return [
        os.path.join(pwd, file)
        for pwd, _, files in os.walk(directory)
        for file in files
        if file.endswith(tuple(exts))
    ]
