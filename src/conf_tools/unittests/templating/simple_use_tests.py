from conf_tools.master import ConfigMaster
from pprint import pformat
from conf_tools.patterns import pattern_matches
from conf_tools.unittests.utils import create_test_environment

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
               }
              ]

test_cases.append(dict(
                       config={'test.vehicles.yaml': """
- id: "s_rf_f${fov}n${n}d${disp}_n${noiselevel}"
  desc: Range-finder with ${disp|U=uniform;R=random} disposition.
  code: 
      - "vehicles.library.sensors.${disp|U=RangefinderUniform;R=RangefinderRandom}"
      - num_sensels: "${n}"
        fov_deg:     "${fov}"
        noise: 
            - vehicles.library.noises.AdditiveGaussian
            - std_dev: "${noiselevel|0=0;1=0.1;2=0.5}"
"""},
    query="s_rf_f180n180dU_n2",
    result=dict(id='s_rf_f180n180dU_n2',
            desc="Range-finder with uniform disposition.",
            code=["vehicles.library.sensors.RangefinderUniform",
                  dict(num_sensels=180, fov_deg=180,
                       noise=["vehicles.library.noises.AdditiveGaussian",
                              dict(std_dev=0.5)])])))


def test_templating1():
    for tc in test_cases:
        config = tc['config']
        query = tc['query']
        result = tc['result']
        check_case(config, query, result)


def check_case(config, query, result):
    # Create files
    with create_test_environment(config) as dirname:
        # Load configuration
        master = ConfigMaster('veh')
        master.add_class('vehicles', '*.vehicles.yaml')
        master.load(dirname)
        spec = master.specs['vehicles'][query]

        if spec != result:
            print('Obtained:\n%s' % pformat(spec))
            print(' Desired:\n%s' % pformat(result))
            raise Exception('Wrong result')


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
