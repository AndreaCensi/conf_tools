import os
from contracts import contract
from conf_tools import logger
__all__ = ['expand_environment']


@contract(s='str')
def expand_environment(s):
    ''' Expands ~ and ${ENV} in the string. '''
    s = os.path.expandvars(s)
    s = os.path.expanduser(s)
    if '$' in s:
        msg = 'Unresolved environment variable in %r' % s
        logger.warn(msg)
    return s
