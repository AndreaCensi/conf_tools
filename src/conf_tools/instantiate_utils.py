from . import contract, SemanticMistake
import traceback


def instantiate(function_name, parameters):
    try:
        function = import_name(function_name)
    except ValueError as e:
        msg = 'Cannot find function or constructor %r: %s' % (function_name, e)
        raise SemanticMistake(msg)

    try:
        #XXX TypeError is too broad, we should bind the params explicitly
        return function(**parameters)
    except TypeError as e:
        params = ', '.join(['%s=%r' % (k, v) for (k, v) in parameters.items()])
        msg = ('Could not call function %s(%s): %s' % 
               (function_name, params, e))
        msg += traceback.format_exc(e)
        raise SemanticMistake(msg)


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
                raise ValueError(msg)

            if not field in module.__dict__:
                msg = 'No field %r found in module %r.' % (field, module)
                raise ValueError(msg)

            return module.__dict__[field]
        else:
            msg = 'Cannot import name %r, and cannot split: %s' % (name, e)
            raise ValueError(msg)

