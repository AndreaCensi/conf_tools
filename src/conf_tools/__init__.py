__version__ = '1.2'

import logging
logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from . import utils

from contracts import (check, contract, new_contract,
                       describe_value, describe_type)


new_contract("id_or_spec", "dict|str")

ID_FIELD = 'id'

from pprint import pformat
import yaml

from .exceptions import *
from .patterns import *
from .valid import *

from .exceptions import *
from .load_entries import *
from .checks import *
from .instantiate_utils import *
from .code_specs import *
from .code_desc import *
from .objspec import *
from .master import *


