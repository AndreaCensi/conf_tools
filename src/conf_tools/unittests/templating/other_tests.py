from conf_tools.master import ConfigMaster
from conf_tools.unittests.utils import create_test_environment
from conf_tools.exceptions import ConfToolsException
from pprint import pformat

other_tests = [

{
  'good': False,
  'what': "Empty template reference with no template",
  'config': {
    'data1.things.yaml': """

- id: my-stuff
                
    """
   }
},
{
  'good': True,
  'what': "Good template",
  'config': {
    'data1.things.yaml': """

- id: "my-${thing}"
  desc: "${thing} instance"
   
- id: my-stuff
    """
   },
   'should_have': ['my-stuff']
},
{
  'good': True,
  'what': "Check the template is not in the list.",
  'config': {
    'data1.things.yaml': """

- id: "my-${thing}"
  desc: "${thing} instance"
   
    """
   },
   'should_have': []
}
]


def test_templating2_good():
    for tc in other_tests:
        if not tc['good']:
            continue

        check_can_be_loaded(tc)


def test_templating2_bad():
    for tc in other_tests:
        if tc['good']:
            continue

        try:
            check_can_be_loaded(tc)
        except ConfToolsException:
            pass
        else:
            msg = 'Expected failure of: \n%s' % pformat(tc)
            raise Exception(msg)


def check_can_be_loaded(tc):
    # Create files
    with create_test_environment(tc['config']) as dirname:
        master = ConfigMaster('veh')

        def check_entry(entry):
            if not 'desc' in entry:
                raise ValueError('No desc field')

        master.add_class('things', '*.things.yaml', check=check_entry)
        master.load(dirname)
        master.specs['things'].make_sure_everything_read()

        should_have = tc.get('should_have', None)
        if should_have is not None:
            found = set(master.specs['things'].keys())
            if set(should_have) != found:
                msg = 'Expected %r, obtained %r.' % (should_have, found)
                raise Exception(msg)



