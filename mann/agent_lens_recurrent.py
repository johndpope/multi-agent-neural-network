#!/usr/bin/env python
import logging
import random
import numpy.random

from mann import agent
import mann.helper
import mann.lens_in_writer

logger = logging.getLogger(__name__)


def setup_logger(fh, formatter):
    logger.setLevel(logging.DEBUG)
    fh = fh
    # fh.setLevel(logging.DEBUG)
    fh.setLevel(logging.CRITICAL)
    formatter = formatter
    fh.setFormatter(formatter)
    global logger
    logger.addHandler(fh)
    logger.debug('Setup logger in agent_lens_recurrent.py')
    return logger


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

    def create_weight_file(self, weight_in_file_path, weight_directory,
                           ex_file_path, **kwargs):
        """Creates the weights for agent_lens_recurrent
        This involves creating an .ex file (Typically Infl.ex)
        calling lens (which will generate weights,
        read in the .ex file, and train)
        """
        logger.debug("creating weight file")
        padded_agent_number = self.get_padded_agent_id()

        # write a LENS ex file before calling lens to create weights

        # number of predecessors
        np = len(self.predecessors)
        logger.debug("Number of predecessors: {}".format(str(np)))

        self.write_lens_ex_file(
            ex_file_path,
            list_to_write_into_string=self.sample_predecessor_values(np))

        logger.debug('Calling lens from agent_lens_recurrent.create_weight_file')
        self.call_lens(lens_in_file_dir=weight_in_file_path,
                       lens_env={'a': padded_agent_number,
                                 'bm': kwargs['between_mean'],
                                 'bs': kwargs['between_sd'],
                                 'wm': kwargs['within_mean'],
                                 'ws': kwargs['within_sd'],
                                 'cs': kwargs['clamp_strength']})
        logger.debug('Finished alling lens from agent_lens_recurrent.create_weight_file')

    # def get_new_state_values_from_out_file(self, file_dir, agent_type,
    #                                        column=0):
    #     """Get new state values from .out file

    #     :param file_dir: file directory of .out file
    #     :type file_dir: str

    #     :parm agent_type: agent type
    #     :type agent_type: str

    #     :parm column: column in the .out file to get new values from
    #     :type column: int

    #     typically agent_type is type(AGENT).__name__

    #     :returns: new state values
    #     :rtype: tuple
    #     """
    #     """Get new state values from .out file_d

    #     :returns: new state values
    #     :rtype: tuple
    #     """
    #     # creates a list and returns a tuple
    #     list_of_new_state = []
    #     read_file_path = file_dir

    #     with open(read_file_path, 'r') as f:
    #         start_bank1, end_bank1, start_bank2, end_bank2 = \
    #             self._start_end_update_out(f, self.agent_type)
    #         for line_idx, line in enumerate(f):
    #             # print(line)
    #             line_num = line_idx + 1  # python starts from line 0
    #             if start_bank1 <= line_num <= end_bank1 or \
    #                start_bank2 <= line_num <= end_bank2:
    #                 # in a line that I want to save information for
    #                 col = line.strip().split(' ')[column]
    #                 list_of_new_state.append(float(col))
    #                 # print('list of new state', list_of_new_state)
    #     return tuple(list_of_new_state)

    def _pick_self(self):
        lens_in_writer_helper = mann.lens_in_writer.LensInWriterHelper()
        lens_ex_file_strings = []
        agent_for_update = "{}-1".format(self.agent_id)

        agent_for_update_ex_str = \
            lens_in_writer_helper.clean_agent_state_in_file(
                agent_for_update,
                mann.helper.convert_list_to_delim_str(self.state, delim=' '))
        lens_ex_file_strings.append(agent_for_update_ex_str)
        return(lens_ex_file_strings)

    def _pick_network(self, n):
        """Picks n from the predecessors and returns a list, lens_ex_file_string
        where each element in the list is the example case used to write an .ex
        LENS file
        """
        predecessors_picked = random.sample(self.predecessors, n)
        logger.debug('predecessors_picked: {}'.format(predecessors_picked))
        lens_in_writer_helper = mann.lens_in_writer.LensInWriterHelper()
        lens_ex_file_strings = []
        lens_ex_file_string_self_1 = self._pick_self()
        # agent_for_update = "{}-1".format(self.agent_id)

        # agent_for_update_ex_str = \
        #     lens_in_writer_helper.clean_agent_state_in_file(
        #         agent_for_update,
        #         mann.helper.convert_list_to_delim_str(self.state, delim=' '))
        # lens_ex_file_strings.append(agent_for_update_ex_str)
        for predecessor in predecessors_picked:
            predecessor_ex_str = \
                lens_in_writer_helper.clean_agent_state_in_file(
                    str(predecessor.agent_id),
                    mann.helper.convert_list_to_delim_str(
                        predecessor.state,
                        delim=' '))
            lens_ex_file_strings.append(predecessor_ex_str)
            # print(lens_ex_file_strings)
        lens_ex_file_string_self_1.extend(lens_ex_file_strings)
        return(lens_ex_file_string_self_1)

    def _pick_manual_predecessor_inputs(self, manual_predecessor_inputs, n):
        """Pick manually entered predecessor inputs
        """
        lens_ex_file_string_self_1 = self._pick_self()
        predecessors_picked = manual_predecessor_inputs[
            numpy.random.choice(manual_predecessor_inputs.shape[0],
                                size=n,
                                replace=False),
            :]
        logger.debug('manual_predecessors_picked: {}'.
                      format(predecessors_picked))
        lens_ex_file_strings = []
        lens_in_writer_helper = mann.lens_in_writer.LensInWriterHelper()
        for idx, predecessor in enumerate(predecessors_picked):
            predecessor_ex_str = \
                lens_in_writer_helper.clean_agent_state_in_file(
                    str(idx) + "_manual",
                    mann.helper.convert_list_to_delim_str(
                        predecessor,
                        delim=' '))
            lens_ex_file_strings.append(predecessor_ex_str)
        lens_ex_file_string_self_1.extend(lens_ex_file_strings)
        return(lens_ex_file_string_self_1)

    def write_lens_ex_file(self, file_to_write,
                           string_to_write=None,
                           list_to_write_into_string=None):
        """Takes a string or list and writes an .ex file for lens
        """
        print("-"*80)
        print("string", string_to_write)
        print("list", list_to_write_into_string)
        with open(file_to_write, 'w') as f:
            if string_to_write is None and list_to_write_into_string is not None:
                # passed in a list of stings to write and not a full string
                ex_file_strings = '\n'.join(list_to_write_into_string)
                logger.debug('writing ex file {}:\n{}\n{}\n{}'.format(
                    file_to_write,
                    '*' * 80,
                    ex_file_strings,
                    '*' * 80))
                f.write(ex_file_strings)
            elif string_to_write is not None and list_to_write_into_string is None:
                # passed in just a string to directly write
                logger.debug('writing ex file {}:\n{}\n{}\n{}'.format(
                    file_to_write,
                    '*' * 80,
                    string_to_write,
                    '*' * 80))
                f.write(string_to_write)
            else:
                s = "Unknown combination of strings or list passed"
                logger.fatal(s)
                raise(ValueError, s)

    def sample_predecessor_values(self, n, manual_predecessor_inputs=None):
        """Returns a list of strings that represent the inputs of n predecessors
        Each element of the string will have the agent number, and a string
        representation of the selected agent's activation values
        """
        if n > len(self.predecessors):
            raise(ValueError, "n is greater than number of predecessors")

        # manual_predecessor_inputs = None
        if manual_predecessor_inputs is not None:
            logger.debug('Picking from manual_predecessor_inputs')
            lens_ex_file_strings = self._pick_manual_predecessor_inputs(
                manual_predecessor_inputs, n)
        else:
            logger.debug('Picking from self.predecessors')
            lens_ex_file_strings = self._pick_network(n)
        return(lens_ex_file_strings)

    def _update_random_n(self, update_type, n, manual_predecessor_inputs,
                         **kwargs):
        """Uses `n` neighbors to update
        """

        lens_ex_file_strings = self.sample_predecessor_values(
            n,
            manual_predecessor_inputs=manual_predecessor_inputs)

        # manual_predecessor_inputs = None
        # if manual_predecessor_inputs is not None:
        #     logger.debug('Picking from manual_predecessor_inputs')
        #     lens_ex_file_strings = self._pick_manual_predecessor_inputs(
        #         manual_predecessor_inputs, n)
        # else:
        #     logger.debug('Picking from self.predecessors')
        #     lens_ex_file_strings = self._pick_network(n)

        ex_file_strings = '\n'.join(lens_ex_file_strings)
        ex_file_path = kwargs['lens_parameters']['ex_file_path']

        self.write_lens_ex_file(ex_file_path, string_to_write=ex_file_strings)
        # with open(ex_file_path, 'w') as f:
        #     f.write(ex_file_strings)
        print('kwargs: ', kwargs['lens_parameters'])
        print(kwargs['lens_parameters']['between_mean'])
        lens_in_file_path = kwargs['lens_parameters']['in_file_path']
        self.call_lens(lens_in_file_path,
                       lens_env={'a': self.get_padded_agent_id(),
                                 'bm': kwargs['lens_parameters']['between_mean'],
                                 'bs': kwargs['lens_parameters']['between_sd'],
                                 'wm': kwargs['lens_parameters']['within_mean'],
                                 'ws': kwargs['lens_parameters']['within_sd'],
                                 'cs': kwargs['lens_parameters']['clamp_strength']})
        if update_type == 'sequential':
            new_state_path = kwargs['lens_parameters']['new_state_path']
            new_state = self.get_new_state_values_from_out_file(new_state_path)
            self.state = new_state
        else:
            raise ValueError('Only implemented sequential updating so far')

    def update_agent_state(self, update_type, update_algorithm,
                           manual_predecessor_inputs, **kwargs):
        """Updates the agent

        :param update_type: Can be either 'simultaneous' or 'sequential'
        :type update_type: str

        :param update_algorithm: 'random_1', 'random_all'
        :type update_algorithm: str
        """
        if self.has_predecessor():
            if update_algorithm == 'random_1':
                self._update_random_n(update_type, 1,
                                      manual_predecessor_inputs, **kwargs)
            elif update_algorithm == 'random_all':
                if manual_predecessor_inputs is not None:
                    n = len(manual_predecessor_inputs)
                elif manual_predecessor_inputs is None:
                    n = len(self.predecessors)
                else:
                    raise ValueError
                self._update_random_n(update_type, n,
                                      manual_predecessor_inputs, **kwargs)
            else:
                raise ValueError("update algorithm unknown")
        else:
            logger.debug('Agent {} has no precessors.'.
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
        print('len new state values: {}'.format((new_state_values)))
        print('len old state values: {}'.format((self.state)))
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
