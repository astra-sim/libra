"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from enum import Enum, auto


class CostElement(Enum):
    """
    Cost elements, consists of Link, Switch, Nic, and Npu.
    """
    Link = auto()
    Switch = auto()
    Nic = auto()
    Npu = auto()
