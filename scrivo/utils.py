"""Miscellaneous utilities."""

import logging
import time

__all__ = ["logtime"]


def logtime(fn):
    """Wrap a function with a performance logging statement."""
    logger = logging.getLogger(__name__)
    fname = fn.__name__

    def wrap(*args, **kwargs):
        timer_start = time.time()
        out = fn(*args, **kwargs)
        logger.info("%s() finished in %.03f sec", fname, time.time() - timer_start)
        return out

    return wrap


class VersionNotFoundError(Exception):
    pass


def get_package_version(init_path: str = "scrivo/__init__.py") -> str:
    with open(init_path) as file:
        for line in file:
            if "__version__" in line:
                return line.strip().split("=").pop().strip('" ')
    raise VersionNotFoundError("Could not find version number")
