import os

from contracts import contract, describe_type

from conf_tools import logger

from .exceptions import SyntaxMistake
from .utils import expand_environment


# TODO: put it somewhere
def recursive_subst_keys(struct, function):
    """ Recursive substitution in a structure
        for key/value pairs in dictionaries.
        function: (key, value) -> (key, value)  """
    if isinstance(struct, dict):
        # TODO: check no overwriting?
        return dict([function(k, recursive_subst_keys(v, function)) 
                     for k, v in struct.items()])
    elif isinstance(struct, list):
        return [recursive_subst_keys(x, function) for x in struct]
    else:
        return struct


@contract(entry='dict(str:*)', returns='dict(str:*)')
def substitute_special(entry, dirname):
    ''' Special stuff for "file:" and "file*" entries. '''
    function = lambda k, v: substitute_special_keys(k, v, dirname)
    newentry = recursive_subst_keys(entry, function)
    # logger.warn('from:\n%s\nto\n%s' % (pformat(entry), pformat(newentry)))
    return newentry

        
def substitute_special_keys(key, val, dirname):
    if not isinstance(key, str):
        return key, val
    if key.startswith('file:'):
        if not isinstance(val, str):
            # XXX
            pass 
        nkey = key[5:]
        nval = intepret_as_filename(val, dirname)
        check_exists(key, nval)
        return nkey, nval
    elif key.startswith('file') and isinstance(val, str):
        nval = intepret_as_filename(val, dirname)
        check_exists(key, nval)
        return key, nval
    else:
        return key, val

def intepret_as_filename(val, dirname):
    # First expand
    val = expand_environment(val)
    return make_relative(val, dirname)
            
def make_relative(val, dirname):
    if not isinstance(val, str):
        msg = ('Only strings can be used as keys, not %s.'
               % describe_type(val))
        raise SyntaxMistake(msg)
    joined = os.path.join(dirname, val)
    nval = os.path.realpath(joined)
    return nval


def check_exists(key, filename):
    if not os.path.exists(filename):
        msg = ('I resolved the key %r to the path\n\t%r\nbut it does not exist.'
               % (key, filename))
        logger.warning(msg)
               
