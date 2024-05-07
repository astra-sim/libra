"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from typing import Optional
from src.model import Model

import gurobipy as gp

def total_bw_500gbps_constraints() -> None:
    model = Model._gp_model
    bw = Model._bw

    # apply total bandwidth constraint
    model.addLConstr(gp.quicksum(bw) == 500)
