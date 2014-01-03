from conf_tools.master import ConfigMaster
from pprint import pformat
from conf_tools.unittests.utils import create_test_environment
from abc import ABCMeta, abstractmethod


class ConfGroup:
    __abc__ = ABCMeta
    
    @abstractmethod
    def evaluate(self, objspec):
        pass
    
class BasicGroup:
    
    
    @staticmethod
    def from_yaml(self, entry):
        assert isinstance(entry, dict)
        assert 'id' in entry
        assert 'desc' in entry
        assert 'contains' in entry
            

test_cases = [
              {'config': {
                           'test.vehicles.yaml': '''

- id: entry1
  desc: Just some entry
  code: code1

- id: entry2
  desc: Just another entry
  code: code2

- id: entry22
  desc: Just another entry
  code: code2


''',

'test.vehicles-groups.yaml': 

'''

- id: all-entries
  desc: All entries
  contains: 
  - all

- id: g2
  desc: other
  contains: 
  - entry1
  - entry2
                            '''},
                'query': 'g2',
                'expected': ['entry1', 'entry2']
               }
              ]


if False:
    def test_groups1():
        for tc in test_cases:
            config = tc['config']
            query = tc['query']
            expected = tc['expected']
            check_group_case(config, query, expected)


def check_group_case(config, query, expected):
    with create_test_environment(config) as dirname:
        # Load configuration
        master = ConfigMaster('veh')
        master.add_class('vehicles', '*.vehicles.yaml')
        master.load(dirname)

        result = master.vehicles.expand_names(query)

        if set(expected) != set(result):
            print('Obtained:\n%s' % pformat(expected))
            print(' Desired:\n%s' % pformat(result))
            raise Exception('Wrong result')

