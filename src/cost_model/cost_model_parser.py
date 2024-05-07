"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

import os

import yaml

from src.cost_model.cost_element import CostElement
from src.cost_model.cost_model import CostModel
from src.cost_model.cost_model_error import CostModelError


class CostModelParser:
    """
    CostModelParser helps parse the yaml cost model file.
    """

    def __init__(self):
        """
        CostModelParser initializer.
        """
        pass

    def parse(self, path: str) -> CostModel:
        """
        Parse the given yaml cost model.

        :param path: path to the yaml cost model
        :return: parsed CostModel
        """
        # check the file exists
        if not os.path.exists(path):
            raise CostModelError(f"Cost model {path} does not exist.")

        # create cost_model
        cost_model = CostModel()

        # load yaml file
        with open(path, 'r') as yaml_file:
            cost_data = yaml.safe_load(yaml_file)

        # iterate over all dimensions
        for dim, costs in cost_data.items():
            # iterate over all cost elements
            for cost_element_name, unit_cost in costs.items():
                # insert this cost element to the cost model
                try:
                    cost_element = CostElement[cost_element_name]
                    cost_model.set_unit_cost(dim, cost_element, unit_cost)
                except KeyError:
                    raise CostModelError(f"{cost_element_name} is not a valid cost element.")

        # return parsed cost_model
        return cost_model
