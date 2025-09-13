"""This is the scrivo package."""

from importlib.metadata import version as _get_version

from scrivo import blog, build, config, ml, page  # noqa: F401
from scrivo.build import compile_site  # noqa: F401
from scrivo.config import Config, read_config  # noqa: F401
from scrivo.page import Page, load_templates_from_dir  # noqa: F401

__version__ = _get_version("scrivo")
