"""Miscellaneous utilities."""

import logging
import time
from typing import Callable, Sized

__all__ = ["logtime", "get_package_version", "s"]


def logtime(fn: Callable) -> Callable:
    """Wrap a function with a performance logging statement.

    Args:
        fn (Callable): The function to be timed.

    Returns:
        Callable: The wrapped version of `fn`.

    """
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


def get_package_version(path: str = "scrivo/__init__.py") -> str:
    """Find and return the package version.

    Args:
        path: Path to the Python file with the version string.

    Raises:
        VersionNotFoundError: If the version string can't be found.

    Returns:
        The current package version string.

    """
    with open(path) as file:
        for line in file:
            if "__version__" in line:
                return line.strip().split("=").pop().strip('" ')
    raise VersionNotFoundError("Could not find version number")


def s(word: str, collection: Sized, suffix: str = "s") -> str:
    """Pluralize a word based on collection size.

    Args:
        word (str): The unit of measure ot be pluralized.
        collection (Sized): The collection to measure for pluralization.
        suffix (str): Optional suffix to atttach if is needed.

    Returns:
        str: A pluralized version of `word` if needed.

    """
    return word + suffix * (len(collection) != 1)
