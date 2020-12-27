__version__ = "6.0.4"
__date__ = ""

from zuper_commons import ZLogger

logger = ZLogger(__name__)

logger.hello_module(
    name=__name__, filename=__file__, version=__version__, date=__date__
)


from . import utils

#
# from contracts import (new_contract)
#
# new_contract("id_or_spec", "dict|str")

ID_FIELD = "id"


class ConfToolsGlobal(object):
    log_instance_error = True


from .exceptions import *
from .patterns import *
from .valid import *

from .exceptions import *
from .special_subst import *
from .load_entries import *
from .checks import *
from .instantiate_utils import *
from .code_specs import *
from .code_desc import *
from .objspec import *
from .master import *
from .global_config import *
