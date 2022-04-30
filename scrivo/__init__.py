"""
Control which modules are imported automatically.

We might want to do this (OK, we _do_ want to do this) because
some of the more complicated stuff can take a long time to load.
"""

__version_tuple__ = (0, 0, 9, 9007)
__version__ = ".".join(map(str, __version_tuple__))
