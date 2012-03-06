from . import (ConfToolsException, ID_FIELD, SyntaxMistake, SemanticMistake,
    logger, yaml, check_valid_id_or_pattern, describe_type, contract, pformat)
from .utils import friendly_path, locate_files
from yaml import YAMLError
import os


def load_entries_from_dir(dirname, pattern):
    try:
        filenames = list(locate_files(dirname, pattern))
        for filename in filenames:
            for x in load_entries_from_file(filename):
                yield x
    except:
        logger.error('Error while loading dir %r' % friendly_path(dirname))
        raise


def load_entries_from_file(filename):
    ''' 
        It is assumed that the file contains a list of dictionaries.
        
        Each dictionary MUST have the field 'id' and it must be unique.
 
        yields (filename, counter), entry 
    
        *Special fields*
        
        If a field name starts with 'file:', it is processed to resolve
        the relative filename.
        
        For example, if we find: ..
        
            {'file:data': 'data.pickle'}, 
        
        we add: .. 
        
            {'data': '/path/data.pickle'}
    '''
    if not os.path.exists(filename):
        msg = 'File %r does not exist.' % filename
        raise SemanticMistake(msg)

    name2where = {}
    for where, x in enumerate_entries_from_file(filename):
        try:
            if not ID_FIELD in x:
                msg = 'Entry does not have the %r field' % ID_FIELD
                raise SemanticMistake(msg)

            substitute_special(x, dirname=os.path.dirname(where[0]))

            # Warn about this?
            name = x[ID_FIELD]
            check_valid_id_or_pattern(name)

            if name in name2where and name2where[name] != where:
                msg = ('Entry %r already know from:\n %s (entry #%d)' %
                        (name, name2where[name][0], name2where[name][1]))
                raise SemanticMistake(msg)

            name2where[name] = where

            yield where, x

        except ConfToolsException as e:
            msg = ('Error while loading entry #%d '
                   ' from file\n   %r\n%s\nError: %s' %
                   (where[1] + 1, where[0], pformat(x), e))
            logger.error(msg)  # XXX
            raise


@contract(entry='dict(str:*)')
def substitute_special(entry, dirname):
    ''' Special stuff for "file:" entries. '''
    for key in list(entry.keys()):
        if key.startswith('file:'):
            nkey = key[5:]
            val = entry[key]
            if not isinstance(val, str):
                msg = ('Only strings can be used as keys, not %s.'
                       % describe_type(val))
                raise SyntaxMistake(msg)
            if nkey in entry:
                raise SemanticMistake('Key %r alread exists' % nkey)
            joined = os.path.join(dirname, val)
            nval = os.path.realpath(joined)
            entry[nkey] = nval


def enumerate_entries_from_file(filename):
    ''' yields (filename, num_entry), entry '''
    with open(filename) as f:
        try:
            parsed = yaml.load(f)
        except YAMLError as e:
            msg = 'Cannot parse YAML file %s:\n%s' % (filename, e)
            raise SyntaxMistake(msg) # TODO: make UserError

        if parsed is None:
            logger.warning('Empty file %r.' % filename)
        else:
            if (not isinstance(parsed, list) or
                not all([isinstance(x, dict) for x in parsed])):
                msg = ('Expect the file %r to contain a list of dicts.' %
                        filename)
                raise SyntaxMistake(msg)

            if not parsed:
                logger.warning('Empty file %r.' % filename)

            for num_entry, entry in enumerate(parsed):
                yield (filename, num_entry), entry
