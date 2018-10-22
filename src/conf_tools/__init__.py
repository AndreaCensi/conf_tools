__version__ = '1.9.7'

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from . import utils

from contracts import (new_contract)
                    
new_contract("id_or_spec", "dict|str")

ID_FIELD = 'id'

class ConfToolsGlobal():
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

