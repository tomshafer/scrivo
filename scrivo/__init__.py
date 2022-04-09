"""
Control which modules are imported automatically.

We might want to do this (OK, we _do_ want to do this) because
some of the more complicated stuff can take a long time to load.
"""

from scrivo.config import load_config  # noqa: F401

__version__ = "0.0.3.9003"
