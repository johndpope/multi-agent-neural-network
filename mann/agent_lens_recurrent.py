#!/usr/bin/env python

import logging
import random

from mann import agent
import mann.helper
import mann.lens_in_writer


class LensAgentRecurrent(agent.LensAgent):
    agent_count = 0

    def __init__(self, num_state_vars):
        """
        :parm num_state_vars: Total number of processing units in the agent
                              positive + negative banks
        :type num_state_vars: int
        """
        assert isinstance(num_state_vars, int),\
            'num_state_vars needs to be an int'
        assert num_state_vars % 2 == 0,\
            'num_state_vars needs to be an even value'

        self._agent_id = LensAgentRecurrent.agent_count
        LensAgentRecurrent.agent_count += 1

        self._agent_type = "_".join([type(self).__name__, 'attitude'])
        self._state = [0] * num_state_vars
        self._temp_new_state = None
        self._len_per_bank = int(len(self.state) / 2)
        self._predecessors = []
        self._num_update = 0

    def __hash__(self):
        return(hash(self.agent_id))

    def __eq__(self, x, y):
        return x.agent_id == y.agent_id

    def calc_new_state_values_rps_1(self, num_predecessors_pick):
        """Calculate new state values from 1 random predecessor implementation
        """
        predecessors_picked = self.pick_random_predecessor(
            num_predecessors_pick)

    def calculate_new_state_values(self,
                                   pick_method='random_predecessor_single',
                                   **kwargs):
        """Calculate new state values

        :param pick_method: how should influencing agents be picked
        :type pick_method: str

        :param **kwargs: keyword arguments to be passed into different
            calculate_new_state_values pick_method implementations

        :returns: New state values
        :rtype: tuple
        """
        assert pick_method in ['random_predecessor_single'],\
            'predecessor pick method not in list of known methods'
        new_state_values = None

        if pick_method == 'random_predecessor_single':
            new_state_values = self.calc_new_state_values_rps_1(1)

        return tuple(new_state_values)

    def get_new_state_values_from_out_file(self, file_dir, agent_type,
                                           column=0):
        """Get new state values from .out file

        :param file_dir: file directory of .out file
        :type file_dir: str

        :parm agent_type: agent type
        :type agent_type: str

        :parm column: column in the .out file to get new values from
        :type column: int

        typically agent_type is type(AGENT).__name__

        :returns: new state values
        :rtype: tuple
        """
        """Get new state values from .out file_d

        :returns: new state values
        :rtype: tuple
        """
        # creates a list and returns a tuple
        list_of_new_state = []
        read_file_path = file_dir

        with open(read_file_path, 'r') as f:
            start_bank1, end_bank1, start_bank2, end_bank2 = \
                self._start_end_update_out(f, self.agent_type)
            for line_idx, line in enumerate(f):
                # print(line)
                line_num = line_idx + 1  # python starts from line 0
                if start_bank1 <= line_num <= end_bank1 or \
                   start_bank2 <= line_num <= end_bank2:
                    # in a line that I want to save information for
                    col = line.strip().split(' ')[column]
                    list_of_new_state.append(float(col))
                    # print('list of new state', list_of_new_state)
        return tuple(list_of_new_state)

    def _update_random_n(self, update_type, n, **kwargs):
        """Uses `n` neighbors to update
        Does not handle if you pick `n` to be greater than the nunber of
        predecessors
        """
        predecessors_picked = random.sample(self.predecessors, n)
        logging.debug('predecessors_picked: {}'.format(predecessors_picked))
        lens_in_writer_helper = mann.lens_in_writer.LensInWriterHelper()
        lens_ex_file_strings = []
        agent_for_update = "{}-1".format(self.agent_id)

        agent_for_update_ex_str = \
            lens_in_writer_helper.clean_agent_state_in_file(
                agent_for_update,
                mann.helper.convert_list_to_delim_str(self.state, delim=' '))
        lens_ex_file_strings.append(agent_for_update_ex_str)

        for predecessor in predecessors_picked:
            predecessor_ex_str = \
                lens_in_writer_helper.clean_agent_state_in_file(
                    str(predecessor.agent_id),
                    mann.helper.convert_list_to_delim_str(predecessor.state,
                                                          delim=' '))
            lens_ex_file_strings.append(predecessor_ex_str)

        ex_file_strings = '\n'.join(lens_ex_file_strings)
        ex_file_path = kwargs['lens_parameters']['ex_file_path']
        with open(ex_file_path, 'w') as f:
            f.write(ex_file_strings)
        lens_in_file_path = kwargs['lens_parameters']['in_file_path']

        print(lens_in_file_path)
        print("~" * 80)
        self.call_lens(lens_in_file_path)

    def update_agent_state(self, update_type, update_algorithm, **kwargs):
        """Updates the agent

        :param update_type: Can be either 'simultaneous' or 'sequential'
        :type update_type: str

        :param update_algorithm: 'random_1', 'random_all'
        :type update_algorithm: str
        """
        if self.has_predecessor():
            if update_algorithm == 'random_1':
                self._update_random_n(update_type, 1, kwargs)
            elif update_algorithm == 'random_all':
                self._update_random_n(update_type, len(self.predecessors),
                                      **kwargs)
            else:
                raise ValueError("update algorithm unknown")
        else:
            logging.debug('Agent {} has no precessors.'.
                          format(self.agent_id))

    @property
    def agent_id(self):
        return self._agent_id

    @agent_id.setter
    def agent_id(self, value):
        try:
            self._agent_id
            raise mann.agent.AssignAgentIdError
        except NameError:
            if value < 0:
                raise ValueError("Agent ID cannot be less than 0")
            else:
                self._agent_id = value
                # LensAgentRecurrent.agent_count += 1

    @property
    def len_per_bank(self):
        return self._len_per_pos_neg_bank

    @len_per_bank.setter
    def len_per_bank(self, value):
        self._len_per_bank

    @property
    def agent_type(self):
        return self._agent_type

    @agent_type.setter
    def agent_type(self, value):
        self._agent_type = value

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state_values):
        print('len new state values: {}'.format(len(new_state_values)))
        print('len old state values: {}'.format(len(self.state)))
        assert len(new_state_values) == len(self.state)
        self._state = new_state_values[:]

    # @property
    # def temp_new_state(self):
    #     return self._temp_new_state
    # @temp_new_state.setter
    # def temp_new_state(self, temp_state_values):
    #     assert len(temp_state_values) == len(self.state)
    #     self._temp_new_state = temp_state_values[:]

    @property
    def predecessors(self):
        return self._predecessors

    @predecessors.setter
    def predecessors(self, predecessors_list):
        self._predecessors = predecessors_list

    @property
    def num_update(self):
        return self._num_update

    @num_update.setter
    def num_update(self, value):
        if value == self.num_update:
            raise ValueError("Number update cannot be equal current count")
        elif value < self.num_update:
            raise ValueError(
                "Number update cannot be lower than current count")
        else:
            self._num_update = value
