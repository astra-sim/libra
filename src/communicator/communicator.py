"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from typing import List

from src.communicator.communicator_error import CommunicatorError


class Communicator:
    def __init__(self,
                 forward_communicator: List[int],
                 input_grad_communicator: List[int],
                 weight_grad_communicator: List[int]):
        self.forward_communicator = forward_communicator
        self.input_grad_communicator = input_grad_communicator
        self.weight_grad_communicator = weight_grad_communicator

        # check communicator validity
        if len(self.forward_communicator) != len(self.input_grad_communicator):
            raise CommunicatorError(
                f"Forward communicator {self.forward_communicator} and "
                f"InputGrad communicator {self.input_grad_communicator} length mismatches.")

        if len(self.input_grad_communicator) != len(self.weight_grad_communicator):
            raise CommunicatorError(
                f"InputGrad communicator {self.input_grad_communicator} and "
                f"WeightGrad communicator {self.weight_grad_communicator} length mismatches.")

        if len(self.forward_communicator) != len(self.weight_grad_communicator):
            raise CommunicatorError(
                f"Forward communicator {self.forward_communicator} and "
                f"WeightGrad communicator {self.weight_grad_communicator} length mismatches.")
