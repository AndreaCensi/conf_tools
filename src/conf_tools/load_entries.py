import os
from pprint import pformat

from contracts import describe_type, contract
from yaml import YAMLError
import yaml

from conf_tools import logger

from . import ID_FIELD, check_valid_id_or_pattern, substitute_special
from .exceptions import ConfToolsException, SyntaxMistake, SemanticMistake
from .patterns import is_pattern
from .utils import friendly_path, locate_files


def load_entries_from_dir(dirname, pattern):
    """ calls load_entries_from_file for each file in dirname respecting
        the pattern. Environment is not expanded. """
    # logger.debug('Loading %r from %r' % (dirname, pattern))
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
        msg = 'File %r does not exist.' % friendly_path(filename)
        raise SemanticMistake(msg)

    name2where = {}
    for where, x in enumerate_entries_from_file(filename):
        try:
            if not ID_FIELD in x:
                msg = 'Entry does not have the %r field' % ID_FIELD
                raise SemanticMistake(msg)

            name = x[ID_FIELD]

            if not is_pattern(name):
                # Otherwise it will complain of missing env variables
                x = substitute_special(x, dirname=os.path.dirname(where[0]))

            # Warn about this?

                
            check_valid_id_or_pattern(name)

            if name in name2where and name2where[name] != where:
                msg = ('Entry %r already know from:\n %s (entry #%d)' % 
                        (name,
                         friendly_path(name2where[name][0]),
                         name2where[name][1]))
                raise SemanticMistake(msg)

            name2where[name] = where

            yield where, x

        except ConfToolsException as e:
            msg = ('Error while loading entry #%d '
                   ' from file\n   %r\n%s\nError: %s' % 
                   (where[1] + 1, friendly_path(where[0]), pformat(x), e))
            logger.error(msg)  # XXX
            raise


def enumerate_entries_from_file(filename):
    ''' Yields (filename, num_entry), entry '''
    with open(filename) as f:
        try:
            parsed = yaml.load(f)
        except YAMLError as e:
            msg = 'Cannot parse YAML file %s:\n%s' % (friendly_path(filename), e)
            raise SyntaxMistake(msg)  # TODO: make UserError

        if parsed is None:
            logger.warning('Found an empty file %r.' % friendly_path(filename))
        else:
            if not isinstance(parsed, list):
                msg = ('Expect the file %r to contain a list of dicts,'
                        ' found %s.' % (friendly_path(filename),
                                         describe_type(parsed)))
                raise SyntaxMistake(msg)
                 
            if  not all([isinstance(x, dict) for x in parsed]):
                msg = ('Expect the file %r to contain a list of dicts.' % 
                        filename)
                raise SyntaxMistake(msg)

            if not parsed:
                logger.warning('Found an empty file %r.' % friendly_path(filename))

            for num_entry, entry in enumerate(parsed):
                yield (filename, num_entry), entry

@contract(entries='list(dict)')
def write_entries(entries, filename_yaml):
    # TODO: check that we can read them back
    logger.info('Writing to %r ' % friendly_path(filename_yaml))
    with open(filename_yaml, 'w') as f:
        yaml.dump(entries, f,
                  default_flow_style=False, explicit_start=True)
