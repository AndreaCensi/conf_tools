from . import logger, contract
import traceback


def instantiate(function_name, parameters):
    function = import_name(function_name)
    try:
        return function(**parameters)
    except TypeError as e:
        msg = ('Could not instantiate [%r, %s]:\n\t%s' %
               (function_name, parameters, e))
        logger.error(msg)
        #raise Exception(msg)
        raise


@contract(name='str')
def import_name(name):
    ''' 
        Loads the python object with the given name. 
    
        Note that "name" might be "module.module.name" as well.
    '''
    try:
        return __import__(name, fromlist=['dummy'])
    except ImportError as e:
        # split in (module, name) if we can
        if '.' in name:
            tokens = name.split('.')
            field = tokens[-1]
            module_name = ".".join(tokens[:-1])

            try:
                module = __import__(module_name, fromlist=['dummy'])
            except ImportError as e:
                msg = ('Cannot load %r (tried also with %r): %s.' %
                       (name, module_name, e))
                msg += '\n' + traceback.format_exc()
                raise Exception(msg)

            if not field in module.__dict__:
                msg = 'No field %r found in module %r.' % (field, module)
                raise Exception(msg)

            return module.__dict__[field]
        else:
            msg = 'Cannot import name %r, and cannot split: %s' % (name, e)
            raise Exception(msg)

