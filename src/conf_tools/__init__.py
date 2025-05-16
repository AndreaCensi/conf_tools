__version__ = "7.3"
__date__ = ""

from zuper_commons import ZLogger

logger = ZLogger(__name__)

logger.hello_module(name=__name__, filename=__file__, version=__version__, date=__date__)
ID_FIELD = "id"


class ConfToolsGlobal:
    log_instance_error = True


from . import utils
from .checks import *
from .code_desc import *
from .code_specs import *

#
# from contracts import (new_contract)
#
# new_contract("id_or_spec", "dict|str")
from .exceptions import *
from .global_config import *
from .instantiate_utils import *
from .load_entries import *
from .master import *
from .objspec import *
from .patterns import *
from .special_subst import *
from .valid import *

logger.hello_module_finished(__name__)
