"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from enum import Enum, auto


class SolverObjective(Enum):
    """
    Solver objectives: either performance or performance-per-cost
    """
    PerfOpt = auto()
    PerfPerCostOpt = auto()
