"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from enum import Enum, auto


class Collective(Enum):
    """
    Collective types
    """
    NoComm = auto()
    ReduceScatter = auto()
    AllGather = auto()
    AllReduce = auto()
    AllToAll = auto()
