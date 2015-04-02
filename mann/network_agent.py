#! /usr/bin/env python

import random
import re

import networkx as nx
import matplotlib.pyplot as plt

from mann import agent
from mann import agent_lens_recurrent


class NetworkAgent(object):
    def __init__(self):
        pass

    def __eq__(self, x, y):
        return x.agent_id == y.agent_id

    def create_multidigraph_of_agents_from_edge_list(
            self, number_of_agents, edge_list, fig_path,
            agent_type=tuple(['None']), **kwargs):
        # create the graph
        self.G = nx.MultiDiGraph()

        # dictonary container for agents, key values will be the agent.get_key
        all_agents = {}

        # create all the agents
        for i in range(number_of_agents):
            print("creating agent # ", i)
            # createing the different types of agents for the network
            if agent_type[0] == 'binary':
                new_agent = agent.BinaryAgent()
            elif agent_type[0] == 'lens':
                if agent_type[2] == 'feed_forward_global_cascade':
                    new_agent = agent.LensAgent(agent_type[1])
                    new_agent.create_weight_file(kwargs.get('weight_in_file'),
                                                 kwargs.get('weight_dir'),
                                                 kwargs.get('base_example'),
                                                 kwargs.get(
                                                     'num_train_examples'),
                                                 kwargs.get(
                                                     'prototype_mutation_prob'),
                                                 kwargs.get(
                                                     'training_criterion'))
                elif agent_type[2] == 'recurrent_attitude':
                    # nothing really happens after the agent gets created
                    # this is more of a place holder for later training
                    # procedures
                    new_agent = agent_lens_recurrent.LensAgentRecurrent(
                        agent_type[1])
                else:
                    raise ValueError('Unknown Lens Agent Type')
            else:
                raise agent.UnknownAgentTypeError(
                    'Unknown agent specified as nodes for network')

            print("agent ", new_agent.get_key(), " created",
                  "; type: ", type(new_agent))

            all_agents[new_agent.agent_id] = new_agent

        print('total number of agents created: ', new_agent.agent_count)

        self.G.add_nodes_from(all_agents.values())
        print('number of nodes created: ', len(self.G))

        for edge in edge_list:
            u, v = edge
            self.G.add_edge(all_agents[u], all_agents[v])

        nx.draw_circular(self.G)
        # plt.show()
        plt.savefig(fig_path)

        return self.G

    def set_predecessors_for_each_node(self):
        # iterate through all nodes in network
        for node_agent in self.G.nodes_iter():
            # look up the predessors for each node
            predecessors = self.G.predecessors(node_agent)
            # since the nodes are an Agent class we can
            # assign the predecessors agent instance variable to the iter
            node_agent.set_predecessors(predecessors)

    def sample_network(self, number_of_agents_to_sample):
        '''
        From the random.sample documentation:
        Return a k length list of unique elements
        chosen from the population sequence or set.
        Used for random sampling without replacement.
        '''
        agents_picked = random.sample(self.G.nodes(),
                                      number_of_agents_to_sample)
        return agents_picked

    def str_list_with_out_brackets(self, list_to_str):
        # reg ex str replace multiple
        # http://stackoverflow.com/questions/6116978/python-replace-multiple-strings
        # dict.iteritems() is a python 2 syntax
        # python 3 has dict.itemd()
        rep = {"[": "", "]": "", "(": "", ")": ""}
        rep = dict((re.escape(k), v) for k, v in rep.items())
        pattern = re.compile("|".join(rep.keys()))
        text = pattern.sub(lambda m: rep[re.escape(m.group(0))],
                           str(list_to_str))
        return text

    def write_network_agent_step_info(self, time_step,
                                      file_to_write, file_mode):
        '''Write agent info for each time step

        Writes the following information respectively
        - time step
        - agent id
        - total number of updates
        - update state for this time step
        - infl agent ID
        - agent state at end of time
        - input agent state
        - lens target
        - prototype
        '''
        with open(file_to_write, mode=file_mode, encoding='utf-8') as f:
            for node in self.G.__iter__():
                f.write(",".join([str(time_step),  # time step
                                  str(node.get_key()),  # agent ID
                                  str(node.num_update),  # total num updates
                                  # update state
                                  # str(node.step_update_status),
                                  # str(node.step_input_agent_id),  # infl ID
                                  # agent state
                                  self.str_list_with_out_brackets(
                                      node.state)  # ,
                                  # input state
                                  # self.str_list_with_out_brackets(
                                  #     node.step_input_state_values),
                                  # lens target
                                  # self.str_list_with_out_brackets(
                                  #     node.step_lens_target),
                                  # prototype
                                  # self.str_list_with_out_brackets(
                                  #     node.prototype)
                                  ]) + "\n")
                node.reset_step_variables()
