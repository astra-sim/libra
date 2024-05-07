"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

import math
from typing import List

from src.network.network_building_block import NetworkBuildingBlock
from src.network.network_error import NetworkError


class Network:
    """
    Network class encapsulates all network related information
    such as Topology, NpusCount, or CostDimensions.
    """

    def __init__(self,
                 topology: List[NetworkBuildingBlock],
                 npus_count: List[int],
                 cost_dimension: List[str]):
        """
        Initializer.

        :param topology: network building blocks per each dimension
        :param npus_count: npus_count per each dimensino
        :param cost_dimension: cost_dimension name per each dimensino
        """
        # set values
        self.topology = topology
        self.npus_count = npus_count
        self.cost_dimension = cost_dimension
        self.dims_count = len(self.topology)

        # check validity
        if len(self.npus_count) != self.dims_count:
            raise NetworkError(f"Given NpusCount ({self.npus_count}) is not {self.dims_count}D.")

        if len(self.cost_dimension) != self.dims_count:
            raise NetworkError(f"Given CostDimension ({self.cost_dimension} is not {self.dims_count}D.")

        for dim in range(self.dims_count):
            if self.npus_count[dim] <= 1:
                raise NetworkError(f"NpusCount at dim {dim + 1} ({self.npus_count[dim]}) should be larger than 1.")

        # calculate total NPUs count
        self.total_npus_count = math.prod(npus_count)
