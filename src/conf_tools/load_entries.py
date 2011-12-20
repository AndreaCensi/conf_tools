from . import locate_files
from . import logger, check, contract, yaml
import os
from pprint import pformat


@contract(directory='str', pattern='str')
def load_configuration_entries(directory, pattern, check_entry):
    ''' 
        Loads all .dynamics.yaml files recursively in the directory. 
        It is assumed that each file contains a list of dictionaries.
        Each dictionary MUST have the field 'id' and it must be unique.
        
        If a field name starts with 'file:', it is processed to resolve
        the relative filename.
        
        For example, {'file:data': 'data.pickle'}, 
        we add {'data': '/path/data.pickle'}
    '''
    if not os.path.exists(directory):
        msg = 'Directory %r does not exist.' % directory
        raise ValueError(msg)

    def enumerate_entries():
        for filename in locate_files(directory, pattern):
            filename = os.path.realpath(filename)
            with open(filename) as f:
                parsed = yaml.load(f)
                if parsed is None:
                    raise Exception('Empty file %r.' % filename)
                check('list(dict)', parsed)

                if not parsed:
                    raise Exception('Empty file %r.' % filename)
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
                        raise Exception('Only strings can be used, not %s.'
                                        % val)
                    if nkey in x:
                        raise Exception('Key %r alread exists' % nkey)
                    joined = os.path.join(os.path.dirname(where[0]), val)
                    nval = os.path.realpath(joined)
                    x[nkey] = nval

            check_entry(x)
            # Warn about this?
            name = x['id']
            if name in all_entries and name2where[name] != where:
                msg = ('While loading %r from:\n %s (entry #%d),\n'
                       'already know from:\n %s (entry #%d)' %
                                (name, where[0], where[1],
                                  name2where[name][0], name2where[name][1]))
                raise Exception(msg)

            name2where[name] = where
            all_entries[name] = x
        except Exception as e:
            msg = ('Error while loading entry'
                   ' from file %r #%d.\n%s\nError: %s' %
                   (where[0], where[1], pformat(x), e))
            logger.error(msg)  # XXX
            raise
    return all_entries

