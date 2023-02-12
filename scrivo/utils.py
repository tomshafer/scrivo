"""Miscellaneous utilities."""

import logging
import os
from typing import Sized

log = logging.getLogger(__name__)


__all__ = ["ensure_dir_exists", "s"]


# Custom package exceptions ------------------------------------------


class VersionNotFoundError(Exception):
    pass


# Utility functions --------------------------------------------------


def s(word: str, collection: Sized, suffix: str = "s") -> str:
    """Pluralize a word based on collection size.

    Args:
        word: Unit of measure to be pluralized
        collection: What to measure for pluralization
        suffix: Suffix to attach to token
    """
    return word + suffix * (len(collection) != 1)


def ensure_dir_exists(dirpath: str) -> str:
    """Create a directory if it doesn't already exist."""
    absdir = os.path.abspath(dirpath)
    if not os.path.exists(absdir):
        log.debug(f"Creating directory {absdir}")
        os.mkdir(absdir)
    return absdir
