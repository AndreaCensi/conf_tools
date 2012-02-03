from . import SyntaxMistake, SemanticMistake, logger, yaml
from pprint import pformat
from yaml import YAMLError
import os
from conf_tools.valid import check_valid_id_or_pattern
from contracts import describe_type
from conf_tools.exceptions import ConfToolsException


def load_entries_from_file(filename, check_entry):
    ''' 
        It is assumed that the file contains a list of dictionaries.
        Each dictionary MUST have the field 'id' and it must be unique.
        
        If a field name starts with 'file:', it is processed to resolve
        the relative filename.
        
        For example, {'file:data': 'data.pickle'}, 
        we add {'data': '/path/data.pickle'}
    '''
    if not os.path.exists(filename):
        msg = 'File %r does not exist.' % filename
        raise SemanticMistake(msg)

    def enumerate_entries():
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

    name2where = {}
    all_entries = {}
    for where, x in enumerate_entries():
        try:
            for key in list(x.keys()):
                if key.startswith('file:'):
                    nkey = key[5:]
                    val = x[key]
                    if not isinstance(val, str):
                        msg = ('Only strings can be used as keys, not %s.'
                               % describe_type(val))
                        raise SyntaxMistake(msg)
                    if nkey in x:
                        raise SemanticMistake('Key %r alread exists' % nkey)
                    joined = os.path.join(os.path.dirname(where[0]), val)
                    nval = os.path.realpath(joined)
                    x[nkey] = nval

            try:
                check_entry(x)
            except Exception as e:
                raise SemanticMistake(e)

            # Warn about this?
            name = x['id']
            check_valid_id_or_pattern(name)

            if name in all_entries and name2where[name] != where:
                msg = ('Entry %r already know from:\n %s (entry #%d)' %
                                (name,
                                  name2where[name][0], name2where[name][1]))
                raise SemanticMistake(msg)

            name2where[name] = where
            all_entries[name] = x
        except ConfToolsException as e:
            msg = ('Error while loading entry #%d '
                   ' from file\n   %r\n%s\nError: %s' %
                   (where[1] + 1, where[0], pformat(x), e))
            logger.error(msg)  # XXX
            raise
    return all_entries


