"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from typing import Optional
from src.model import Model

import gurobipy as gp

def multiple_constraints() -> None:
    model = Model._gp_model
    bw = Model._bw

    # apply total bandwidth constraint
    model.addLConstr(gp.quicksum(bw) == 1000)

    # apply abritrary design constraints
    model.addLConstr(bw[0] == 500)
    model.addLConstr(bw[0] >= bw[1])
    model.addLConstr(bw[1] >= bw[2])
    model.addLConstr(bw[2] + bw[3] == 200)
