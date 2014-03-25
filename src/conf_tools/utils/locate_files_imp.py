from collections import defaultdict
import fnmatch
import os

from contracts import contract

from . import logger


__all__ = ['locate_files']


@contract(returns='list(str)', directory='str',
          pattern='str', followlinks='bool')
def locate_files(directory, pattern, followlinks=True):
    filenames = []
    
    for root, _, files in os.walk(directory, followlinks=followlinks):
        for f in files:
            if fnmatch.fnmatch(f, pattern):
                filename = os.path.join(root, f)
                filenames.append(filename)

    real2norm = defaultdict(lambda: [])
    for norm in filenames:
        real = os.path.realpath(norm)
        real2norm[real].append(norm)
        # print('%s -> %s' % (real, norm))

    for k, v in real2norm.items():
        if len(v) > 1:
            msg = 'In directory:\n\t%s\n' % directory
            msg += 'I found %d paths that refer to the same file:\n'
            for n in v:
                msg += '\t%s\n' % n
            msg += 'refer to the same file:\n\t%s\n' % k
            msg += 'I will silently eliminate redundancies.'
            logger.warning(v)

    return real2norm.keys()

