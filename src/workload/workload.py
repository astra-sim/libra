"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from typing import List

from src.workload.layer import Layer


class Workload:
    """
    Workload encapsulates all workload-related data
    such as communication type, size, or computation times.
    """

    def __init__(self, layers: List[Layer]):
        """
        Initializer.

        :param layers: all layers of the workload.
        """
        self.layers = layers
        self.layers_count = len(layers)
