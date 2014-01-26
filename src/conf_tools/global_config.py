from contracts import contract

from conf_tools import logger


__all__ = [ 'GlobalConfig', 'ConfigState']


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
        for c in config_dirs:
            GlobalConfig.global_load_dir(c)

    @staticmethod
    def global_load_dir(config_dir):
        """ 
            Load the configuration for all the different masters. 
            This could be a list of dirs separated by ":".
        """
        masters = GlobalConfig._masters

        for name, master in masters.items():  # @UnusedVariable
            # print('now loading %s / %s' % (name, config_dir))
            master.load(config_dir)

        logger.info('loaded global config dir %r' % config_dir)
        GlobalConfig._dirs.append(config_dir)

    @staticmethod
    def get_state():
        return ConfigState()

    @staticmethod
    def set_state(state):
        state.restore()

    @staticmethod
    def clear_for_tests():
        """ Resets the state by unregistering everything; useful for tests. """
        GlobalConfig._masters = {}
        GlobalConfig._singletons = {}
        GlobalConfig._dirs = []


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
