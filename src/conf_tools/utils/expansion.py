import os

from . import logger

__all__ = [
    "expand_environment",
]


def expand_environment(s: str) -> str:
    """Expands ~ and ${ENV} in the string."""
    s = os.path.expandvars(s)
    s = os.path.expanduser(s)
    if "$" in s:
        msg = "Unresolved environment variable in %r" % s
        logger.warn(msg)
    return s
