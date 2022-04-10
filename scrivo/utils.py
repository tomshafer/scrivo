"""Miscellaneous utilities."""

import logging
import os
from typing import Sized

log = logging.getLogger(__name__)

__all__ = ["get_package_version", "s", "ensure_dir_exists"]


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


def ensure_dir_exists(dirpath: str) -> str:
    """Create a directory if it doesn't already exist.

    Args:
        dirpath (str): The directory to create if not already existing.

    Returns:
        str: The absolute path to the target directory.

    """
    absdir = os.path.abspath(dirpath)
    if not os.path.exists(absdir):
        log.debug(f"Creating directory {absdir}")
        os.mkdir(absdir)
    return absdir
