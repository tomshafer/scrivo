"""Miscellaneous utilities."""

from __future__ import annotations

import logging
import os
import time
from typing import Sized

log = logging.getLogger(__name__)


__all__ = ["ensure_dir_exists", "s"]


# Custom package exceptions ------------------------------------------


class VersionNotFoundError(Exception):
    pass


# Utility functions --------------------------------------------------


def s(word: str, collection: Sized | int, suffix: str = "s") -> str:
    """Pluralize a word based on collection size.

    Args:
        word: Unit of measure to be pluralized
        collection: What to measure for pluralization, or the size
        suffix: Suffix to attach to token
    """
    n = collection if isinstance(collection, int) else len(collection)
    return word + suffix * (n != 1)


def ensure_dir_exists(dirpath: str) -> str:
    """Create a directory if it doesn't already exist."""
    absdir = os.path.abspath(dirpath)
    if not os.path.exists(absdir):
        log.debug("Creating directory %s", absdir)
        os.mkdir(absdir)
    return absdir


class timer:
    """Time an enclosing scope."""

    def __init__(
        self,
        level: int = logging.INFO,
        logger: logging.Logger | None = None,
        msg: str | None = None,
        silent: bool = False,
    ) -> None:
        self._level = level
        self._logger = logger or logging.getLogger(__name__)
        self._msg = msg if msg is not None else "Completed in"
        self._silent = silent

    def __enter__(self) -> timer:
        # Return self to use the result outside of the context
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.end = time.perf_counter()
        self.elapsed = self.end - self.start
        if not self._silent:
            self._logger.log(self._level, "%s %s", self._msg, self)

    def __str__(self) -> str:
        return f"{self.elapsed:.3f} s"
