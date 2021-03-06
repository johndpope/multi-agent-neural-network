#! /usr/bin/env python
###############################################################################
import nose
import sys
import io
import random
import os
import glob
import subprocess
import numpy.testing

from mann import agent

here = os.path.abspath(os.path.dirname(__file__))


###############################################################################
# Unit tests for the LensAgent class
###############################################################################
def reset_LensAgent():
    agent.LensAgent.prototypes = [[0, 1, 1, 0]]
    agent.LensAgent.agent_count = 0


def reset_LensAgent_20():
    reset_LensAgent()
    agent.LensAgent.prototypes = [[0, 1, 0, 0, 0, 0, 1, 1, 0, 0,
                                   1, 1, 0, 0, 1, 0, 0, 1, 0, 1]]


@nose.with_setup(reset_LensAgent)
def test_lens_agent_get_key_single():
    test_lens_agent = agent.LensAgent(4)
    assert test_lens_agent.get_key() == 0


@nose.with_setup(reset_LensAgent)
def test_lens_agent_get_key_multiple():
    list_of_test_agents = []
    for i in range(10):
        test_multiple_lens_agent = agent.LensAgent(4)
        list_of_test_agents.append(test_multiple_lens_agent)
    assert list_of_test_agents[0].get_key() == 0
    assert list_of_test_agents[-1].get_key() == 9


@nose.with_setup(reset_LensAgent)
def test_lens_agent_state_init():
    test_lens_agent = agent.LensAgent(4)
    assert test_lens_agent.get_state() == [0] * 4


@nose.with_setup(reset_LensAgent)
def test_lens_agent_set_get_state():
    test_lens_agent = agent.LensAgent(4)
    test_lens_agent.set_state([1, 2, 3, 4])
    assert test_lens_agent.get_state() == [1, 2, 3, 4]

    try:
        test_lens_agent.set_state([1, 2])
    except ValueError:
        assert test_lens_agent.get_state() == [1, 2, 3, 4]
        assert True
    else:
        assert False


@nose.with_setup(reset_LensAgent)
def test_list_to_str_delim():
    test_lens_agent = agent.LensAgent(4)
    expected_string = "1 3 5"
    output_string = test_lens_agent._list_to_str_delim([1, 3, 5], delim=" ")
    assert output_string == expected_string


@nose.with_setup(reset_LensAgent_20)
def test_create_weight_file():
    test_lens_agent = agent.LensAgent(20)
    assert test_lens_agent.get_key() == 0

    search_file = os.path.join(here, 'lens', 'weights', 'AgentWgt000000.wt')
    if os.path.exists(search_file):
        globed = glob.glob(search_file)
        print('glob: ', globed)
        os.remove(globed[0])

    # where I want the weight file saved
    weight_output_dir = os.path.join(here, 'lens', 'weights')
    # where the .in file to create weights is
    weight_in_file = os.path.join(here, 'lens', 'AutoEncoderArch.in')

    prototype = agent.LensAgent.prototypes[0]
    assert(isinstance(prototype, list))

    # create the weight file
    test_lens_agent.create_weight_file(weight_in_file,
                                       weight_output_dir,
                                       prototype,
                                       50, 0, 3)

    # search directory for weight file
    expected_weight_file_name = os.path.join(here, 'lens', 'weights',
                                             'wgt000000.wt')
    assert os.path.exists(expected_weight_file_name) is True


@nose.with_setup(reset_LensAgent_20)
def test_lens_agent_seed_agent_no_update():
    test_lens_agent = agent.LensAgent(20)
    assert test_lens_agent.get_state() == [0] * 20
    weight_base_example = '0, 1, 0, 0, 0, 0, 1, 1, 0, 0,' +\
                          '1, 1, 0, 0, 1, 0, 0, 1, 0, 1'
    test_lens_agent.seed_agent_no_update(weight_base_example)

    expected_state = [0, 1, 0, 0, 0, 0, 1, 1, 0, 0,
                      1, 1, 0, 0, 1, 0, 0, 1, 0, 1]
    assert(test_lens_agent.get_state() == expected_state)


@nose.with_setup(reset_LensAgent_20)
def test_lens_agent_seed():
    test_lens_agent = agent.LensAgent(20)
    assert test_lens_agent.get_state() == [0] * 20

    expected_prototype = [0, 1, 0, 0, 0, 0, 1, 1, 0, 0,
                          1, 1, 0, 0, 1, 0, 0, 1, 0, 1]
    assert(expected_prototype == test_lens_agent.prototype)

    weight_base_example = '0, 1, 0, 0, 0, 0, 1, 1, 0, 0,' +\
                          '1, 1, 0, 0, 1, 0, 0, 1, 0, 1'
    lens_in_file = os.path.join(here, 'lens', 'AutoEncoderArch-update.in')
    agent_self_ex_file = os.path.join(here, 'lens', 'Infl.ex')
    agent_self_out_file = os.path.join(here, 'lens', 'AgentState.out')
    criterion = 3
    epsilon = 0.2
    test_lens_agent.seed_agent_no_update(weight_base_example)

    test_lens_agent.seed_agent(weight_base_example,
                               lens_in_file,
                               agent_self_ex_file,
                               agent_self_out_file,
                               criterion, epsilon)
    print('new state: ', test_lens_agent.get_state(), file=sys.stderr)

    expected_state = [0.00535452, 0.995756, 0.00328139, 0.00315037, 0.00399676,
                      0.00647343, 0.994951, 0.994197, 0.0038641, 0.00499099,
                      0.994252, 0.995074, 0.00527825, 0.00148673, 0.995454,
                      0.00472569, 0.00459107, 0.994304, 0.00434961, 0.998149]

    print('\ncannot fully test lens_agent_seed until we can seed LENS\n',
          file=sys.stderr)
    assert(len(test_lens_agent.get_state()) == len(expected_state))
    assert(len(expected_state) == 20)
    # assert test_lens_agent.get_state() == expected_state


@nose.with_setup(reset_LensAgent)
def test_update_agent_state_default():
    pass


@nose.with_setup(reset_LensAgent_20)
def test_update_agent_state():
    list_of_predecessors = []
    for i in range(3):
        lens_agent_predecessor = agent.LensAgent(20)
        list_of_predecessors.append(lens_agent_predecessor)
    test_lens_agent = agent.LensAgent(20)
    assert test_lens_agent.get_key() == 3

    test_lens_agent.set_predecessors(list_of_predecessors)
    assert test_lens_agent.predecessors[0].get_key() == 0
    assert test_lens_agent.predecessors[-1].get_key() == 2

    weight_in_file = os.path.join(here, 'lens', 'AutoEncoderArch.in')
    weight_output_dir = os.path.join(here, 'lens', 'weights')
    prototype = agent.LensAgent.prototypes[0]
    test_lens_agent.create_weight_file(weight_in_file,
                                       weight_output_dir,
                                       prototype,
                                       50, 0, 3)

    lens_in_file = os.path.join(here, 'lens', 'AutoEncoderArch-update.in')
    agent_ex_file = os.path.join(here, 'lens', 'AgentState.ex')
    infl_ex_file = os.path.join(here, 'lens', 'Infl.ex')
    agent_out_file = os.path.join(here, 'lens', 'AgentState.out')
    criterion = 3

    test_lens_agent.update_agent_state(lens_in_file=lens_in_file,
                                       agent_ex_file=agent_ex_file,
                                       infl_ex_file=infl_ex_file,
                                       agent_state_out_file=agent_out_file,
                                       criterion=criterion)
    expected_state = [0.0165341, 0.970908, 0.0182914, 0.00488143, 0.015797,
                      0.0392513, 0.979719, 0.987717, 0.00827398, 0.0158307,
                      0.972111, 0.978402, 0.0253079, 0.00824886, 0.976305,
                      0.015317, 0.00684265, 0.986226, 0.00730182, 0.982301]
    print('agent state: ', test_lens_agent.get_state(), file=sys.stderr)
    print('\ncannot fully test update_agent_state until we can seed LENS\n',
          file=sys.stderr)
    assert(len(test_lens_agent.get_state()) == len(expected_state))

    # numpy.testing.assert_allclose(test_lens_agent.get_state(),
    #                               expected_state,
    #                               rtol=1e-00,
    #                               verbose=True)


@nose.with_setup(reset_LensAgent_20)
def test_get_new_state_values_from_out_file():
    test_lens_agent = agent.LensAgent(20)

    agent_state_out_file_dir = os.path.join(here, 'lens', 'AgentState.out')
    calculated_state = test_lens_agent._get_new_state_values_from_out_file(
        agent_state_out_file_dir)
    expected_state = [0.00575073, 0.99771, 0.00475418, 0.00453887, 0.00774883,
                      0.00334972, 0.995966, 0.995523, 0.00518261, 0.00274538,
                      0.994989, 0.995876, 0.00276238, 0.00623561, 0.993709,
                      0.00702017, 0.00484292, 0.994042, 0.00391492, 0.99492]
    print('agent state: ', calculated_state, file=sys.stderr)
    print('\ncannot fully test update_agent_state until we can seed LENS\n',
          file=sys.stderr)

    assert(len(test_lens_agent.get_state()) == len(expected_state))
    # numpy.testing.assert_allclose(calculated_state, expected_state,
    #                               rtol=1e-07, verbose=True)


@nose.with_setup(reset_LensAgent_20)
def test_get_new_state_values_from_out_file_standalone():
    test_lens_agent = agent.LensAgent(20)

    agent_state_out_file_dir = os.path.join(here, 'lens',
                                            'AgentState_10PU_N_ex.out')

    calculated_state = test_lens_agent.get_new_state_values_from_out_file(
        agent_state_out_file_dir, 10)
    expected_state = [0.61267, 0.593237, 0.620111, 0.604982, 0.602024,
                      0.584436, 0.578927, 0.560431, 0.565787, 0.57802]
    print(calculated_state, file=sys.stderr)
    assert calculated_state == expected_state

    # print('agent state: ', calculated_state, file=sys.stderr)
    # print('\ncannot fully test update_agent_state until we can seed LENS\n',
    #       file=sys.stderr)

    # assert(len(test_lens_agent.get_state()) == len(expected_state))

expected_ex_file = '''name: sit1
B: 0 1 0 0 0 0 1 1 0 0 1 1 0 0 1 0 0 1 0 1 ;
'''


@nose.with_setup(reset_LensAgent_20)
def test_string_agent_state_to_ex():
    test_lens_agent = agent.LensAgent(20)

    weight_base_example = '0, 1, 0, 0, 0, 0, 1, 1, 0, 0,' +\
                          '1, 1, 0, 0, 1, 0, 0, 1, 0, 1'
    lens_in_file = os.path.join(here, 'lens', 'AutoEncoderArch-update.in')
    agent_self_ex_file = os.path.join(here, 'lens', 'Infl.ex')
    agent_self_out_file = os.path.join(here, 'lens', 'AgentState.out')
    criterion = 3
    epsilon = 0.2
    test_lens_agent.seed_agent_no_update(weight_base_example)

    test_lens_agent.seed_agent(weight_base_example,
                               lens_in_file,
                               agent_self_ex_file,
                               agent_self_out_file,
                               criterion, epsilon)

    # test_lens_agent.seed_agent()
    print('state: ', test_lens_agent.get_state(), file=sys.stderr)

    # expected_state = [0.00320154, 0.996163, 0.00439015, 0.00400144, 0.00232756,
    #                   0.0035433, 0.997151, 0.99518, 0.00139811, 0.00388239,
    #                   0.993956, 0.993552, 0.00417568, 0.0041836, 0.995494,
    #                   0.00426954, 0.0057836, 0.998099, 0.00273839, 0.996264]
    # assert test_lens_agent.get_state() == expected_state
    # generated_file = test_lens_agent._string_agent_state_to_ex()
    # numpy.testing.assert_allclose(test_lens_agent.get_state(),
    # expected_state,
    #                               rtol=1e-07, verbose=True)
    # assert generated_file == expected_ex_file
    print('\ncannot fully test update_agent_state until we can seed LENS\n',
          file=sys.stderr)


@nose.with_setup(reset_LensAgent)
def test_length_per_bank():
    test_lens_agent = agent.LensAgent(10)
    calculated_bank_length = test_lens_agent._length_per_bank()
    expected_bank_length = 5
    assert calculated_bank_length == expected_bank_length


@nose.with_setup(reset_LensAgent)
def test_get_pos_neg_bank_values():
    test_lens_agent = agent.LensAgent(10)

    set_state_values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    test_lens_agent.set_state(set_state_values)
    assert test_lens_agent.get_state() == set_state_values

    pos, neg = test_lens_agent.get_pos_neg_bank_values()
    assert pos == [0, 1, 2, 3, 4]
    assert neg == [5, 6, 7, 8, 9]


@nose.with_setup(reset_LensAgent)
def test_export_state_to_env():
    test_lens_agent = agent.LensAgent(10)

    set_state_values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    test_lens_agent.set_state(set_state_values)
    assert test_lens_agent.get_state() == set_state_values
    env = test_lens_agent.get_env_for_pos_neg_bank_values()
    # print(env, file=sys.stderr)
    print(env.get('p0'))
    assert env.get('p0') == '0'
    assert env.get('p4') == '4'
    assert env.get('n0') == '5'
    assert env.get('n4') == '9'


@nose.with_setup(reset_LensAgent)
def test_flip_1_0_value():
    test_lens_agent = agent.LensAgent(10)
    assert test_lens_agent._flip_1_0_value(1) == 0
    assert test_lens_agent._flip_1_0_value(0) == 1
    nose.tools.assert_raises(ValueError, test_lens_agent._flip_1_0_value, -1)
    nose.tools.assert_raises(ValueError, test_lens_agent._flip_1_0_value, 5)


@nose.with_setup(reset_LensAgent)
def test_create_weight_training_examples():
    test_lens_agent = agent.LensAgent(20)
    base_train_example = [0, 1, 0, 0, 0, 0, 1, 1, 0, 0]
    expected_training_list = [[0, 1, 1, 0, 0, 0, 1, 1, 0, 0],
                              [0, 1, 0, 0, 0, 0, 1, 1, 0, 1]]
    for idx, list in enumerate(expected_training_list):
        assert expected_training_list[idx] != base_train_example
    assert len(base_train_example) == 10
    random.seed(1)
    # if the path does not exist, create it
    # TODO might want to move this so it is run at beginning of unit test
    # that is, outside any funciton, but part of the script on the top
    weight_training_examples_dir = here + '/lens/weight_training_examples'
    if not os.path.exists(weight_training_examples_dir):
        os.makedirs(weight_training_examples_dir)
    filename = (weight_training_examples_dir + '/train_weight' +
                test_lens_agent.get_key(pad_0_left=True) + '.ex')
    training_list = test_lens_agent._create_weight_training_examples(
        filename, base_train_example, 2, 1)
    # print(training_list, file=sys.stderr)
    # assert training_list == expected_training_list
    print('\ncannot fully test update_agent_state until we can seed LENS\n',
          file=sys.stderr)


@nose.with_setup(reset_LensAgent)
def test_mutate():
    test_lens_agent = agent.LensAgent(10)
    random.seed(1)
    prototype = [1, 1, 1, 1, 1,
                 1, 1, 1, 1, 1]
    assert(isinstance(prototype, list))
    post_mutation = test_lens_agent.mutate(prototype, 0)
    assert(post_mutation == prototype)

    post_mutation = test_lens_agent.mutate(prototype, 1)
    assert(post_mutation == [0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0])

    post_mutation = test_lens_agent.mutate(prototype, .7)
    print(post_mutation, file=sys.stderr)
    assert(post_mutation == [1, 0, 1, 0, 0, 1, 0, 1, 1, 0])

@nose.with_setup(reset_LensAgent)
def test_write_ex_attitude_agent():
    test_lens_agent = agent.LensAgent(10)
    test_lens_agent.set_state([1, 0, 1, 0, 1,
                               0, 1, 0, 1, 0])
    ex_file = os.path.join(here, 'lens', 'test_write_ex_attitude')
    test_lens_agent.write_ex_attitude(test_lens_agent.get_state(),
                                      'old_state',
                                      1,
                                      ex_file, mode='w')

@nose.with_setup(reset_LensAgent)
def test_write_ex_attitude_agent_infl():
    test_lens_agent = agent.LensAgent(10)
    print(str((test_lens_agent.get_state())), file=sys.stderr)
    test_lens_agent.set_state([1, 0, 1, 0, 1,
                               0, 1, 0, 1, 0])
    print(str((test_lens_agent.get_state())), file=sys.stderr)
    test_lens_infl = agent.LensAgent(10)
    test_lens_infl.set_state([0, 1, 0, 1, 0,
                              1, 0, 1, 0, 1])
    print(str(test_lens_infl.get_state()), file=sys.stderr)

    ex_file = os.path.join(here, 'lens', 'test_write_ex_attitude')
    print(ex_file, file=sys.stderr)
    test_lens_agent.write_ex_attitude(test_lens_agent.get_state(),
                                      'old_state',
                                      1,
                                      ex_file, mode='w')
    test_lens_infl.write_ex_attitude(test_lens_infl.get_state(),
                                     'update',
                                      1,
                                      ex_file, mode='a')


###############################################################################
# Unit Test notes
###############################################################################
# To write to 'file', write to StringIO
# use getvalue() to get and check its final contents
# writer.getvalue()
# nose.assert_almost_equals()
Data = '''0 0 1 1
1 0 2 1
2 0 3 1
'''


def count_lines_in(reader):
    count = 0
    for line in reader:
        count += 1
    return count


def count_lines(filename):
    reader = open(filename, 'r')
    reader.close()
    result = count_lines_in(reader)
    return result


def test_count_lines():
    # print("testing count lines", file=sys.stderr)
    reader = io.StringIO(Data)
    assert count_lines_in(reader) == 3


# Fixtures
# something we run a test on
# nose has a function called setup
# will be run before any of the tests
# use nose.with_setup to apply the
# function before each test
