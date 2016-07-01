from . import logger
from .utils import dir_from_package_name, expand_environment
from contracts import check_isinstance, contract
import os

__all__ = [ 
    'GlobalConfig', 
    'ConfigState',
    'reset_config',
]


class GlobalConfig(object):
    """
    
        To correctly restore configuration with compmake: ::
        
        
            comp(f, GlobalConfig.get_state(), param=2)
        
            def f(config_state, param):
                config_state.restore()
                        
        
    """
    # A list
    # str -> ConfigMaster
    _masters = {}

    # class -> instance of ObjSpec
    _singletons = {}

    # Directories previously loaded (in case somebody registers later)
    _dirs = []

    @staticmethod
    def register_master(name, master):
        """ 
            Register a master so that we can keep track of them,
            and load configuration in all of them at the same time. 
        """
        if not isinstance(name, str):
            raise ValueError('Required a string, got %s.' % name.__repr__())

        if name in GlobalConfig._masters:
            msg = 'Name %r already present.' % name
            raise ValueError(msg)

        GlobalConfig._masters[name] = master
        # print('registering %r' % name)

        for dirname in GlobalConfig._dirs:
            # print('Now deferred loading %r %r' % (name, dirname))
            master.load(dirname)

    @staticmethod
    @contract(config_dirs='list(str)')
    def global_load_dirs(config_dirs):
        """ The environments variable will all be expanded 
            (so that it can be used from other threads. """
        for c in config_dirs:
            GlobalConfig.global_load_dir(c)

    @staticmethod
    @contract(config_dir='str')
    def global_load_dir(config_dir):
        """ 
            Load the configuration for all the different masters. 
            
            The environment variables are expanded.
            
            Also, if it looks like a package name,
            it will be expanded using resource_filename.
        """
        config_dir0 = config_dir
        
        if looks_like_package_name(config_dir):
            config_dir = dir_from_package_name(config_dir)
        
        config_dir = expand_environment(config_dir)

        if config_dir != 'default':
            if not os.path.exists(config_dir):
                msg = 'Config dir does not exist: %s' % config_dir
                raise ValueError(msg)
        
        masters = GlobalConfig._masters

        for name, master in masters.items():  # @UnusedVariable
            # print('now loading %s / %s' % (name, config_dir))
            master.load(config_dir)

        logger.info('loaded global config dir %r' % config_dir)
        if config_dir0 != config_dir:
            logger.info('Expanded from %r' % config_dir0)
        GlobalConfig._dirs.append(config_dir)

    @staticmethod
    def get_state():
        return ConfigState()

    @staticmethod
    def set_state(state):
        state.restore()

    @staticmethod
    def clear_for_tests():
        """ Resets the state by unregistering everything; useful for mcdp_lang_tests. """
        GlobalConfig._masters = {}
        GlobalConfig._singletons = {}
        GlobalConfig._dirs = []


def reset_config():
    # Reset all the config
    setattr(GlobalConfig, '_dirs', [])
    for _, m in GlobalConfig._masters.items():
        from conf_tools.master import ConfigMaster
        check_isinstance(m, ConfigMaster)

        for spec in m.specs.values():
            spec.clear()
            spec.clear()
            # List of files already read        
            spec.files_read = set()
            spec.dirs_read = []
            spec.dirs_to_read = []
            
            # ID -> file where it was found
            spec.entry2file = {}
            spec.templates = {}

        # all the dirs that were passed to load(), in case we miss any
        setattr(m, '_dirs', [])


@contract(d='str')
def looks_like_package_name(d):

    try:
        dir_from_package_name(d)
        return True
    except ValueError:
        return False
#
#
#     if d == '.':
#         return False
#     tokens = d.split('.')
#     has_dot = len(tokens) == 2
#     return has_dot and not '/' in d

            
class ConfigState(object):

    def __init__(self):
        self.masters = GlobalConfig._masters
        self.singletons = GlobalConfig._singletons
        self.dirs = GlobalConfig._dirs

    def restore(self):
        # print('Restoring config state')
        # print('directories: %s' % self.dirs)
        # print('masters: %s' % self.masters)
        # print('singletons: %s' % self.singletons)
        GlobalConfig._masters = self.masters
        GlobalConfig._dirs = self.dirs
        GlobalConfig._singletons = self.singletons
