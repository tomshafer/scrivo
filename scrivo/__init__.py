"""
Control which modules are imported automatically.

We might want to do this (OK, we _do_ want to do this) because
some of the more complicated stuff can take a long time to load.
"""

from scrivo import blog, build, config, ml, page  # noqa: F401
from scrivo.build import compile_site  # noqa: F401
from scrivo.config import Config, read_config  # noqa: F401
from scrivo.page import Page, load_templates_from_dir  # noqa: F401

__version__ = "0.0.3.9001"
