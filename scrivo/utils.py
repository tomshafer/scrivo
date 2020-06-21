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
