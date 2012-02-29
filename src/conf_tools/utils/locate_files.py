import os
import fnmatch

__all__ = ['locate_files']


def locate_files(directory, pattern, followlinks=True):
    for root, _, files in os.walk(directory, followlinks=followlinks):
        for f in files:
            if fnmatch.fnmatch(f, pattern):
                yield os.path.realpath(os.path.join(root, f))

