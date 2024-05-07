"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

import os
from typing import List

import yaml

from src.network.network import Network
from src.network.network_building_block import NetworkBuildingBlock
from src.network.network_error import NetworkError


class NetworkParser:
    """
    NetworkParser helps parse the network yaml configuration file.
    """

    def __init__(self):
        """
        NetworkParser initializer.
        """
        pass

    def parse(self, path: str) -> Network:
        """
        Parse the given yaml network model.

        :param path: path to the yaml network model
        :return: parsed Network
        """
        # check the file exists
        if not os.path.exists(path):
            raise NetworkError(f"Network model {path} does not exist.")

        # load yaml file
        with open(path, 'r') as yaml_file:
            network_data = yaml.safe_load(yaml_file)

        # parse data
        topology_names = network_data['Topology']
        topology = NetworkParser.parse_topology_name(topology_names)

        npus_count = network_data['NpusCount']
        cost_dimension = network_data['CostDimension']

        # create and return parsed network
        return Network(topology=topology,
                       npus_count=npus_count,
                       cost_dimension=cost_dimension)

    @staticmethod
    def parse_topology_name(topology_names: List[str]) -> List[NetworkBuildingBlock]:
        """
        Parse the given topology (in str) into the list of NetworkBuildingBlock elements.

        :param topology_names: List of topology names (e.g., ['Ring', 'FullyConnected']
        :return: List of NetworkBuildingBlock elements (e.g., [Ring, FullyConnected]).
        """
        topology: List[NetworkBuildingBlock] = list()

        for name in topology_names:
            try:
                topology.append(NetworkBuildingBlock[name])
            except KeyError:
                raise NetworkError(f"{name} is not a valid topology name.")

        return topology
