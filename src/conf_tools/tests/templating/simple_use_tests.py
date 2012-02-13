import tempfile
import os
from conf_tools.master import ConfigMaster
from pprint import pformat
from contextlib import contextmanager
from conf_tools.patterns import pattern_matches

test_cases = [
              {'config': {
                           'test.vehicles.yaml': '''
# A vehicle with a top and a bottom.
- id: "d-${top}-${bottom}"
  desc: "${top} / ${bottom}"
  code: code
                            '''},
                'query': 'd-TOP-BOTTOM',
                'result': dict(id="d-TOP-BOTTOM",
                               desc='TOP / BOTTOM', code='code')
               }]


def test_templating1():
    for tc in test_cases:
        config = tc['config']
        query = tc['query']
        result = tc['result']
        check_case(config, query, result)


def check_case(config, query, result):
    # Create files
    with create_tmp_dir() as dirname:

        for filename, contents in config.items():
            with open(os.path.join(dirname, filename), 'w') as f:
                f.write(contents)

        # Load configuration
        master = ConfigMaster()
        master.add_class('vehicles', '*.vehicles.yaml')
        master.load(dirname)

        if not query in  master.specs['vehicles']:
            msg = ('Could not find %s in config. (%s)' %
                   (query, master.specs.items()))
            raise Exception(msg)
        spec = master.specs['vehicles'][query]

        print('Obtained: %s' % pformat(spec))
        assert spec == result


@contextmanager
def create_tmp_dir():
    dirname = tempfile.mkdtemp()
    try:
        yield dirname
    except:
        raise


def test_basic_templating():

    result = pattern_matches('r-${robot}', 'r-ciao')
    assert result == dict(robot='ciao'), result

    result = pattern_matches('r2-${robot}', 'r-ciao')
    assert result == None, result


def test_ignoring_partial1():
    result = pattern_matches('${robot}-nuisance', 'myrobot-nuisance-other')
    assert result == None, result


def test_ignoring_partial2():
    result = pattern_matches('nuisance-${robot}', 'other-nuisance-myrobot')
    assert result == None, result
