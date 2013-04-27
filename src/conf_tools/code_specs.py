from . import BadConfig, instantiate, contract, new_contract
from pprint import pformat
from conf_tools.utils.indent_string import indent
from conf_tools.exceptions import ConfToolsException
import traceback

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
new_contract('code_spec', check_valid_code_spec)

@contract(code_spec='code_spec')
def instantiate_spec(code_spec):
    ''' code_spec must be a sequence  [string, dictionary], giving
        the python function (or class) to instantiate, along
        with its parameters. '''
    function_name = code_spec[0]
    parameters = code_spec[1]
    assert isinstance(function_name, str)
    assert isinstance(parameters, dict)
    try:
        return instantiate(function_name, parameters)
    except Exception as e:
        msg = 'Could not instance the spec:\n' 
        msg += indent(pformat(code_spec), '| ')  
        msg += '\nbecause of this error:\n'
        msg += indent(traceback.format_exc(e).strip(), '> ')
        raise ConfToolsException(msg)
