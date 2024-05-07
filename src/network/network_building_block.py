"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from enum import Enum, auto


class NetworkBuildingBlock(Enum):
    """
    Network building blocks per each dimension.
    """
    Ring = auto()
    FullyConnected = auto()
    Switch = auto()
