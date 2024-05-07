"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

import math
from typing import Dict

import gurobipy as gp

from src.cost_model.cost_element import CostElement
from src.cost_model.cost_model_error import CostModelError
from src.network import Network, NetworkBuildingBlock


class CostModel:
    """
    Cost model defines the cost of each CostElement per each given dimensions.
    """

    def __init__(self):
        """
        Initialize emtpy cost model.
        """
        # cost model
        self.cost_model: Dict[str, Dict[CostElement, float]] = dict()

        # network variable to be set
        self.network: Network = None

    def set_network(self, network: Network) -> None:
        """
        Attach the network object to the cost model.

        :param network: target network
        """
        self.network = network

    def set_unit_cost(self, cost_dim: str, cost_element: CostElement, cost: float) -> None:
        """
        Set the cost of the given network element of a specific dimension.

        :param cost_dim: cost dimension of the network to query
        :param cost_element: cost element type
        :param cost: unit cost of the element
        """
        # check whether the dimension exists
        if cost_dim not in self.cost_model:
            self.cost_model[cost_dim] = dict()

        # check the cost is not set
        if cost_element in self.cost_model[cost_dim]:
            raise CostModelError(f"{cost_element.name} is already set for dim {cost_dim}.")

        # check the cost validity
        if cost <= 0:
            raise CostModelError(
                f"{cost_element.name} cost at dim {cost_dim} ({cost}) should be a positive value.")

        # set the cost
        self.cost_model[cost_dim][cost_element] = cost

    def compute_network_cost(self, bw: gp.tupledict) -> gp.LinExpr:
        """
        Calculate the cost of the network.

        :param bw: bandwidth (per NPU) of each network dimensions.
        :return: estimated network cost of the given topology.
        """
        # initialize network costs
        network_cost = gp.LinExpr()

        # iterate over all dimensions
        for dim in range(self.network.dims_count):
            # get the number of (building block) topologies and their cost
            topologies_count = self._get_topologies_count(dim)
            topology_cost = self._get_topology_cost(dim=dim,
                                                    bandwidth=bw[dim])
            # increment the total network cost
            network_cost += topologies_count * topology_cost

        # return network cost
        return network_cost

    def _get_unit_cost(self, cost_dim: str, cost_element: CostElement) -> float:
        """
        Return the unit cost of the queried cost element at a specific network dimension.

        :param cost_dim: dimension of the network to query
        :param cost_element: cost element type
        :return: unit cost
        """
        # check the validity
        if cost_dim not in self.cost_model:
            raise CostModelError(f"Dim {cost_dim} doesn't exist.")

        if cost_element not in self.cost_model[cost_dim]:
            raise CostModelError(f"{cost_element} doesn't exist in dim {cost_dim}.")

        # return unit cost
        return self.cost_model[cost_dim][cost_element]

    def _get_topologies_count(self, dim: int) -> int:
        """
        Get the number of basic topologies for the given dimension.

        :param dim: target dimension to query
        :return: the number of basic building blocks (of the target dim) in the entire network topology.
        """
        # get values of the target dimension
        topology = self.network.topology[dim]
        npus_count = self.network.npus_count[dim]

        # get the number of NetworkBuildingBlocks of the current dimension
        if topology == NetworkBuildingBlock.Ring or topology == NetworkBuildingBlock.FullyConnected:
            return self.network.total_npus_count // npus_count

        if topology == NetworkBuildingBlock.Switch:
            # assumption: we use one big switch up to the given dimension
            return math.prod(self.network.npus_count[(dim + 1):])

        # should not reach here
        raise CostModelError(f"Unknown topology: {topology.name}")

    def _get_topology_cost(self,
                           dim: int,
                           bandwidth: gp.Var) -> gp.LinExpr:
        """
        Calculate the cost of each basic network topology of the queried dimension.

        :param dim: dimension to query
        :param bandwidth: bandwidth (per NPU) of the target dimension.
        :return: cost of the basic network topology
        """
        # calculate topology cost
        topology_cost = gp.LinExpr()

        # dimension data
        topology = self.network.topology[dim]
        cost_dimension = self.network.cost_dimension[dim]

        # calculate link cost
        link_cost = self._get_unit_cost(cost_dim=cost_dimension, cost_element=CostElement.Link)
        link_bandwidth = self._get_link_bandwidth(dim=dim, bandwidth=bandwidth)
        links_count = self._get_links_count(dim=dim)

        topology_cost += link_cost * link_bandwidth * links_count

        # if the network is switch, add NIC and Switch costs
        if topology == NetworkBuildingBlock.Switch:
            # NIC cost
            nic_cost = self._get_unit_cost(cost_dim=cost_dimension, cost_element=CostElement.Nic)
            topology_cost += nic_cost * link_bandwidth * links_count

            # switch cost
            switch_cost = self._get_unit_cost(cost_dim=cost_dimension, cost_element=CostElement.Switch)
            topology_cost += switch_cost * link_bandwidth * links_count

        # return the calculated cost
        return topology_cost

    def _get_link_bandwidth(self,
                            dim: int,
                            bandwidth: gp.Var) -> gp.Var:
        """
        Get the bandwidth of each link, by dividing the given bw
        by the number of links of the given topology.

        :param dim: dimension of the network
        :param bandwidth: total bandwidth of the dimension

        :return: link bandwidth of the dimension
        """
        # get values of the target dimension
        topology = self.network.topology[dim]
        npus_count = self.network.npus_count[dim]

        if topology == NetworkBuildingBlock.Ring:
            return bandwidth / 2

        if topology == NetworkBuildingBlock.FullyConnected:
            return bandwidth / (npus_count - 1)

        if topology == NetworkBuildingBlock.Switch:
            return bandwidth

        # should not reach here
        raise CostModelError(f"Unknown topology: {topology.name}")

    def _get_links_count(self, dim: int) -> int:
        """
        Return the number of total links within the given basic topology building block.

        :param dim: target dimension of the network
        :return: number of links of the target basic topology
        """
        # get values of the target dimension
        topology = self.network.topology[dim]
        npus_count = self.network.npus_count[dim]

        if topology == NetworkBuildingBlock.Ring:
            return npus_count * 2  # bidirectional

        if topology == NetworkBuildingBlock.FullyConnected:
            return npus_count * (npus_count - 1)

        if topology == NetworkBuildingBlock.Switch:
            # assumption: we use one big switch up to the given dimension
            return math.prod(self.network.npus_count[:(dim + 1)])

        # should not reach here
        raise CostModelError(f"Unknown topology: {topology.name}")
