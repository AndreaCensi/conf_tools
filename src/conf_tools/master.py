from . import logger, load_entries_from_file, locate_files
from UserDict import IterableUserDict
from abc import abstractmethod
from contracts import contract


class ObjectSpec(IterableUserDict):
    def __init__(self, name, pattern, check, instance_method, master):
        self.name = name
        self.pattern = pattern
        self.check = check
        self.instance_method = instance_method
        self.master = master
        IterableUserDict.__init__(self)

    @contract(id_object='str')
    def instance(self, id_object):
        self.master.make_sure_loaded()
        if not id_object in self.data:
            msg = ('No %s %r known; I know %s'
                    % (self.name, id_object, self.data.keys()))
            raise ValueError(msg)
        return self.instance_spec(self.data[id_object])

    @contract(spec='dict')
    def instance_spec(self, spec):
        self.master.make_sure_loaded()
        if self.instance_method is None:
            msg = 'No instance method specified for %r' % self.name
            raise ValueError(msg)
        return self.instance_method(spec)


class ConfigMaster:

    def __init__(self, name=None):
        self.loaded = False
        self.specs = {}
        self.prefix = "%s: " % name if name else ""
        self.files_read = set()

    def add_class(self, name, pattern, check=None, instance=None):
        self.specs[name] = ObjectSpec(name, pattern, check, instance, self)
        self.__dict__[name] = self.specs[name]

    @abstractmethod
    def get_default_dir(self):
        pass

    def make_sure_loaded(self):
        ''' 
            If the configuration is not been loaded yet, load the default one. 
        '''
        if not self.loaded:
            self.load(None)

    def load(self, directory=None):
        if directory is None:
            directory = self.get_default_dir()
        self.debug('Loading config from %r.' % directory)

        self.loaded = True
        found = []
        for spec in self.specs.values():
            pattern = spec.pattern
            check = spec.check

            nfound = 0

            for filename in locate_files(directory, pattern):
                #self.debug('Considering %r' % filename)
                if filename in self.files_read:
                    #self.debug('Skipping %r' % filename)
                    continue

                self.files_read.add(filename)

                entries = load_entries_from_file(filename, check_entry=check)

                for entry in entries:
                    if entry in spec.data:
                        msg = 'Entry %r already found.' % entry
                        raise ValueError(msg)

                spec.data.update(entries)

                nfound += len(entries)

            found.append((spec.name, nfound))
            # TODO: check redudancy

        lists = ', '.join('%s: %d' % (a, b) for (a, b) in found)
        self.debug('Found ' + lists + '.')

    def debug(self, s):
        logger.debug('%s%s' % (self.prefix, s))
