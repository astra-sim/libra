"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

# import constraints
from typing import Dict, Callable
import gurobipy as gp

# define and register training loops
constraints: Dict[str, Callable[[], None]] = dict()

# import available constraint files
from inputs.constraints.total_bw_500gbps import total_bw_500gbps_constraints
from inputs.constraints.multiple_constraints import multiple_constraints

# register available constraints function
constraints['total_bw_500gbps'] = total_bw_500gbps_constraints
constraints['multiple_constraints'] = multiple_constraints
