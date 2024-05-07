"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from src.workload.phase import Phase


class Layer:
    """
    Layer represents a workload layer
    Which has three phases: Forward, InputGrad, and WeightGrad.
    """

    def __init__(self,
                 forward: Phase,
                 input_grad: Phase,
                 weight_grad: Phase):
        """
        Initializer

        :param forward: forward phase of the layer
        :param input_grad: input gradient phase of the layer
        :param weight_grad: weight gradient phase of the layer
        """
        self.forward = forward
        self.input_grad = input_grad
        self.weight_grad = weight_grad
