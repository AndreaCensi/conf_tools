from .checks import check_necessary, wrap_check
from .code_specs import check_valid_code_spec, instantiate_spec
from .exceptions import BadConfig
from conf_tools import ConfToolsGlobal, logger
from contracts import describe_value
from pprint import pformat


def check_generic_code_desc(x, what=""):
    """ Checks that it has fields id,desc,code and code is a code spec. """
    if not isinstance(x, dict):
        raise BadConfig(x, 'A valid %s config must be a dictionary.' % what)
    necessary = [ 
      ('id', str),
      ('desc', str),
      ('code', list),
    ]
    check_necessary(x, necessary)
    wrap_check(x, 'checking "code" entry', check_valid_code_spec, x['code'])


def instance_generic_code_desc(entry, expected_class=None):
    try:
        instance = instantiate_spec(entry['code'])
    except:
        if ConfToolsGlobal.log_instance_error:
            msg = 'Error while trying to instantiate entry:\n' + pformat(entry)
            logger.error(msg)
        raise

    if expected_class is not None:
        check_type(entry, expected_class, instance)

    return instance


class GenericInstance(object):
    def __init__(self, check_class):
        self.check_class = check_class

    def __call__(self, entry):
        return instance_generic_code_desc(entry, self.check_class)


class GenericIsinstance(object):
    
    def __init__(self, check_class):
        self.check_class = check_class
        
    def __call__(self, value):
        if not isinstance(value, self.check_class):
            msg = 'Object is not a %s: %s' % (self.check_class, value)
            raise ValueError(msg)
        
        
class GenericCall(object):
    def __init__(self, check_function=None):
        self.check_function = check_function
        
    def __call__(self, entry):
        try:
            instance = instantiate_spec(entry['code'])
            if self.check_function is not None:
                self.check_function(instance)
            return instance
        except:
            if ConfToolsGlobal.log_instance_error:
                logger.error('Error while trying to instantiate entry:\n%s'
                         % (pformat(entry)))
            raise
         

def check_type(entry, etype, obtained):
    if not isinstance(obtained, etype):
        msg = 'Error in instantiating code spec:\n\t%s' % str(entry['code']).strip()
        msg += '\nI expected: %s\nbut I got %s' % (etype, describe_value(obtained))
        from conf_tools.exceptions import ConfToolsException
        raise ConfToolsException(msg)

