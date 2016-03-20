import traceback

from contracts import contract, new_contract

from .exceptions import BadConfig, ConfToolsException
from .instantiate_utils import instantiate
from .utils import indent


__all__ = [
    'check_valid_code_spec',
    'instantiate_spec',
    'format_code_spec',
    'format_yaml',
]


def check_valid_code_spec(x):
    if not isinstance(x, list):
        raise BadConfig(x, 'A code spec must be a list.')

    if len(x) != 2:
        msg = 'A code spec must be a list of exactly two elements.'
        raise BadConfig(x, msg)

    name = x[0]
    params = x[1]
    if not isinstance(name, str):
        raise BadConfig(x, 'The code must be given as a string.')
    if not isinstance(params, dict):
        raise BadConfig(x, 'The params must be given as a dictionary.')

new_contract('check_valid_code_spec', check_valid_code_spec)

def check_valid_code_spec_contract(x):
    """ Note that otherwise BadConfig is thrown --- 
    while it should be ValueError for PyContracts. """
    try:
        check_valid_code_spec(x)
    except BadConfig as e:
        raise ValueError(e)

new_contract('code_spec', check_valid_code_spec_contract)

@contract(code_spec='code_spec')
def instantiate_spec(code_spec):
    ''' code_spec must be a sequence  [string, dictionary], giving
        the python function (or class) to instantiate, along
        with its parameters. '''
    try:
        function_name = code_spec[0]
        parameters = code_spec[1]
        assert isinstance(function_name, str)
        assert isinstance(parameters, dict)

        return instantiate(function_name, parameters)
    except Exception as e:
        msg = 'Could not instance the spec:\n' 
        msg += indent(format_code_spec(code_spec).strip(), '  ').strip()
        msg += '\nbecause of this error:\n'
        if isinstance(e, ConfToolsException):
            st = str(e)
        else:
            st = traceback.format_exc(e) 
        msg += indent(st.strip(), '| ')
        msg = msg.strip()
        raise ConfToolsException(msg)

def format_code_spec(code_spec):
    return format_yaml(code_spec)

def format_yaml(ob):
    import yaml
    return yaml.dump(ob)
