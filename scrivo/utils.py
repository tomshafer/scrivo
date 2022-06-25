"""Miscellaneous utilities."""

import logging
import shlex
import subprocess as sp
import time
from datetime import timedelta, timezone

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


def get_tz() -> timezone:
    """Get the current timezone using 'date'"""
    zone = sp.run(shlex.split("date '+%z'"), stdout=sp.PIPE).stdout.strip()
    return timezone(offset=timedelta(hours=int(zone[:3]), minutes=int(zone[3:])))
