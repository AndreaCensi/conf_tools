from . import (BadConfig, check_necessary, wrap_check, check_valid_code_spec,
    logger, instantiate_spec, describe_value, pformat)


def check_generic_code_desc(x, what):
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
        logger.error('Error while trying to instantiate entry:\n%s'
                     % (pformat(entry)))
        raise

    if expected_class is not None:
        check_type(entry, expected_class, instance)

    return instance


class GenericInstance():
    def __init__(self, check_class):
        self.check_class = check_class

    def __call__(self, entry):
        return instance_generic_code_desc(entry,
                                          expected_class=self.check_class)


def check_type(entry, etype, obtained):
    if not isinstance(obtained, etype):
        msg = 'Error in instantiating code spec:\n\t%s\n' % entry['code']
        msg += 'I expected a %s, got %s' % (etype, describe_value(obtained))
        raise Exception(msg)

