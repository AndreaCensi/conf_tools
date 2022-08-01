from typing import List

from . import logger
from collections import defaultdict

import fnmatch
import os

__all__ = [
    "locate_files",
]


def locate_files(
    directory: str,
    pattern: str,
    followlinks: bool = True,
    include_directories: bool = False,
    include_files: bool = True,
) -> List[str]:
    # print('locate_files %r %r' % (directory, pattern))
    filenames = []

    for root, dirnames, files in os.walk(directory, followlinks=followlinks):
        if include_files:
            for f in files:
                if fnmatch.fnmatch(f, pattern):
                    filename = os.path.join(root, f)
                    filenames.append(filename)

        if include_directories:
            for d in dirnames:
                if fnmatch.fnmatch(d, pattern):
                    filename = os.path.join(root, d)
                    filenames.append(filename)

    real2norm = defaultdict(list)
    for norm in filenames:
        real = os.path.realpath(norm)
        real2norm[real].append(norm)
        # print('%s -> %s' % (real, norm))

    for k, v in real2norm.items():
        if len(v) > 1:
            msg = "In directory:\n\t%s\n" % directory
            msg += "I found %d paths that refer to the same file:\n"
            for n in v:
                msg += "\t%s\n" % n
            msg += "refer to the same file:\n\t%s\n" % k
            msg += "I will silently eliminate redundancies."
            logger.warning(v)

    return list(real2norm.keys())
