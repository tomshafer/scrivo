"""
YACS-powered configuration system.

See the YACS documentation for how I've set this up:
https://github.com/rbgirshick/yacs/blob/master/README.md
"""

from typing import Optional

from yacs.config import CfgNode as CN

__all__ = ["get_default_cfg", "load_config"]


_C = CN()

_C.site = CN()
# The base URL for the website. Used for absolute link generation.
_C.site.url = None
# The root source directory for processing.
_C.site.source_dir = None
# The root directory for the static site output.
_C.site.output_dir = None


def get_default_cfg() -> CN:
    """Provide a baseline configuration.

    Returns:
        A CfgNode compatible with this application.
    """
    return _C.clone()


def load_config(path: Optional[str] = None) -> CN:
    """Load a configuration and merge with the default.

    Args:
        path: Path to a config file to merge with the default.

    Returns:
        A CfgNode instance with default values plus any new
        values overriding and extending the defaults.
    """
    base = get_default_cfg()
    return base if path is None else base.merge_from_file(path)
Î
