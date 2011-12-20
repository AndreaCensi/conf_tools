from . import BadConfig, instantiate
from contracts import contract, new_contract


@new_contract
def check_valid_code_spec(x):
    if not isinstance(x, list):
        raise BadConfig(x, 'A code spec must be a list.')

    if len(x) != 2:
        raise BadConfig(x,
                        'A code spec must be a list of exactly two elements.')

    name = x[0]
    params = x[1]
    if not isinstance(name, str):
        raise BadConfig(x, 'The code must be given as a string.')
    if not isinstance(params, dict):
        raise BadConfig(x, 'The code params be given as a dictionary.')


@contract(code_spec='check_valid_code_spec')
def instantiate_spec(code_spec):
    ''' code_spec must be a sequence  [string, dictionary], giving
        the python function (or class) to instantiate, along
        with its parameters. '''
    function_name = code_spec[0]
    parameters = code_spec[1]
    assert isinstance(function_name, str)
    assert isinstance(parameters, dict)
    return instantiate(function_name, parameters)

