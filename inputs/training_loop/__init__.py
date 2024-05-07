"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from typing import Dict, Callable

import gurobipy as gp

from src.model import Model

# define and register training loops
training_loops: Dict[str, Callable[[Model], gp.LinExpr]] = dict()

# import available training loops
from inputs.training_loop.no_overlap import no_overlap

# register training loops
training_loops['no_overlap'] = no_overlap
