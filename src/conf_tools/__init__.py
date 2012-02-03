__version__ = '1.1'

from .utils import *
logging.basicConfig()

logger = logging.getLogger("ConfTools")
logger.setLevel(logging.DEBUG)

from contracts import check, contract, new_contract

new_contract("id_or_spec", "dict|str")

from pprint import pformat
import yaml

from .exceptions import *
from .patterns import *
from .valid import *

from .exceptions import *
from .locate_files import *
from .load_entries import *
from .checks import *
from .instantiate_utils import *
from .code_specs import *
from .code_desc import *
from .master import *

