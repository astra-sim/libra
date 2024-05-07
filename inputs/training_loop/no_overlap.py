"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

import gurobipy as gp

from src.model import Model


def no_overlap(model: Model) -> gp.LinExpr:
    # workload and collective time info
    workload = model.workload
    coll_time = model.coll_time

    # compute end-to-end time
    e2e_time = gp.LinExpr()

    # forward pass
    for layer_idx, layer in enumerate(workload.layers):
        e2e_time += layer.forward.compute_time
        e2e_time += coll_time[layer_idx, 0]

    # backward pass
    for layer_idx, layer in enumerate(reversed(workload.layers)):
        e2e_time += layer.input_grad.compute_time
        e2e_time += coll_time[layer_idx, 1]

        e2e_time += layer.weight_grad.compute_time
        e2e_time += coll_time[layer_idx, 2]

    # return e2e time
    return e2e_time
