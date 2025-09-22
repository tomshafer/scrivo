"""Parse YAML configuration files."""

import os
from typing import Any, Dict, NamedTuple, Optional

from yaml import safe_load

__all__ = ["Config", "read_config"]


# Enforce types on the config files
class SiteConfig(NamedTuple):
    """Site YAML sub-configuration options."""

    url: str
    source_dir: str
    build_dir: str


class BlogTemplatesConfig(NamedTuple):
    """Templates YAML sub-configuration options for blog components."""

    default: str
    home: str
    archives: str
    tags: str


class FeedTemplatesConfig(NamedTuple):
    """Templates YAML sub-configuration options for feeds."""

    rss: str
    rss_tag: str
    json: str


class TemplatesConfig(NamedTuple):
    """Templates YAML sub-configuration options."""

    source_dir: str
    default: str
    blog: BlogTemplatesConfig
    feeds: FeedTemplatesConfig


class Config(NamedTuple):
    """Site YAML configuration options."""

    site: SiteConfig
    templates: TemplatesConfig
    build_count_file: Optional[str]


# Apply the NamedTuples to config.yml
# FIXME: Handle missing keys in the config file
def read_config(path: str) -> Config:
    """Read in YAML configurations."""
    if not os.path.exists(path):
        raise FileNotFoundError(f'file "{path}" cannot be found')
    with open(path, "r", encoding="utf8") as fh:
        yaml: Dict[str, Any] = safe_load(fh)
    return Config(
        site=SiteConfig(
            url=yaml["site"]["url"],
            source_dir=yaml["site"]["source_dir"],
            build_dir=yaml["site"]["build_dir"],
        ),
        templates=TemplatesConfig(
            source_dir=yaml["templates"]["source_dir"],
            default=yaml["templates"]["default"],
            blog=BlogTemplatesConfig(
                default=yaml["templates"]["blog"]["default"],
                home=yaml["templates"]["blog"]["home"],
                archives=yaml["templates"]["blog"]["archives"],
                tags=yaml["templates"]["blog"]["tags"],
            ),
            feeds=FeedTemplatesConfig(
                rss=yaml["templates"]["feeds"]["rss"],
                rss_tag=yaml["templates"]["feeds"]["rss_tag"],
                json=yaml["templates"]["feeds"]["json"],
            ),
        ),
        build_count_file=yaml["build_count_file"],
    )
