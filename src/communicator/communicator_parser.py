"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

import os

import yaml

from src.communicator.communicator import Communicator
from src.communicator.communicator_error import CommunicatorError


class CommunicatorParser:
    """
    CommunicatorParser helps parse the yaml communicator.
    """

    def __init__(self):
        """
        CommunicatorParser initializer.
        """
        pass

    def parse(self, path: str) -> Communicator:
        """
        Parse the given yaml communicator file.

        :param path: path to the yaml communicator
        :return: parsed Communicator
        """
        # check the file exists
        if not os.path.exists(path):
            raise CommunicatorError(f"Communicator {path} does not exist.")

        # load yaml file
        with open(path, 'r') as yaml_file:
            communicator_data = yaml.safe_load(yaml_file)

        # parse yaml data
        forward_communicator = communicator_data['Forward']
        input_grad_communicator = communicator_data['InputGrad']
        weight_grad_communicator = communicator_data['WeightGrad']

        # create and return communicator
        return Communicator(forward_communicator=forward_communicator,
                            input_grad_communicator=input_grad_communicator,
                            weight_grad_communicator=weight_grad_communicator)
