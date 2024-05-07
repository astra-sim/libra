"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from typing import Optional, List, Callable

import gurobipy as gp
from gurobipy import GRB

from src.communicator import Communicator
from src.cost_model import CostModel
from src.model.model_error import ModelError
from src.model.solver_objective import SolverObjective
from src.network import Network
from src.workload import Workload, Collective, Phase


class Model:
    # Gurobi Model
    _gp_model = gp.Model("LibraSolver")

    # Network Bandwidths: LIBRA object to optimize for
    _bw: Optional[gp.tupledict] = None
    _bw_inv: Optional[gp.tupledict] = None

    # Objective Variables
    _e2e_time = gp.LinExpr(0)
    _perf_per_cost = gp.LinExpr(0)
    _network_cost = _gp_model.addVar(lb=0, vtype=GRB.CONTINUOUS)

    # other models
    network: Optional[Network] = None
    cost_model: Optional[CostModel] = None

    def __init__(self, workload: Workload, communicator: Communicator, training_loop: Callable[['Model'], gp.LinExpr]):
        # set class variables
        self.workload = workload
        self.communicator = communicator

        # communication time per each dim * phase
        # required for Gurobi implementation purposes

        # self.dim_time[layer][phase][dim]
        self.dim_time = Model._gp_model.addVars(workload.layers_count, 3, Model.network.dims_count, lb=0,
                                                vtype=GRB.CONTINUOUS)

        # self.coll_time[layer][phase]
        self.coll_time = Model._gp_model.addVars(workload.layers_count, 3, lb=0, vtype=GRB.CONTINUOUS)

        # apply constraints
        self._apply_dim_time_constraints()
        self._apply_coll_time_constraints()

        # increment e2e time
        self._update_e2e_time(training_loop=training_loop)

    @classmethod
    def solve(cls, objective: SolverObjective.PerfOpt, verbose: bool = False) -> None:
        """
        Set the objective and run the QP solver.

        :param objective: objective type.
        :param verbose: True if verbose mode is enabled, false otherwise
        """
        # set solver parameters
        cls._gp_model.setParam(paramname='OutputFlag', newval=verbose)  # verbose
        cls._gp_model.setParam(paramname='NonConvex', newval=2)  # QP problem
        cls._gp_model.setParam(paramname='ScaleFlag', newval=2)  # scaling for numerical stability

        # set solver objective
        cls._set_objective(objective=objective)

        # print statement if verbose if false
        if not verbose:
            print("(Optimization Log Skipped)")

        # run optimization
        cls._gp_model.optimize()

        # print result
        print("=" * 80)
        print("LIBRA Optimization Result:")
        cls._print_bw()

    @classmethod
    def _set_objective(cls, objective: SolverObjective) -> None:
        if objective == SolverObjective.PerfOpt:
            # set minimize(perf) as objective
            cls._gp_model.setObjective(expr=cls._e2e_time, sense=GRB.MINIMIZE)
        elif objective == SolverObjective.PerfPerCostOpt:
            # set minimize(perf-per-cost) as objective
            cls._perf_per_cost = cls._e2e_time * cls._network_cost / 1e10
            cls._gp_model.setObjective(expr=cls._perf_per_cost, sense=GRB.MINIMIZE)
        else:
            # should not reach here
            raise ModelError(f"Objective {objective} is unknown.")

    @classmethod
    def _print_bw(cls) -> None:
        """
        Print self.bw list.
        """
        # get optimized self.bw
        bandwidths = cls._gp_model.getAttr('x', cls._bw.values())

        # print BW
        for bw in bandwidths:
            print(f"{bw:.2f}", end="\t")
        print()

    @classmethod
    def initialize_model(cls, network: Network, cost_model: CostModel) -> None:
        # set class variables
        cls.network = network
        cls.cost_model = cost_model

        # attach network to the cost model
        cls.cost_model.set_network(network=cls.network)

        # initialize bw variables
        cls._bw = cls._gp_model.addVars(network.dims_count, lb=0, vtype=GRB.CONTINUOUS)
        cls._bw_inv = cls._gp_model.addVars(network.dims_count, lb=0, vtype=GRB.CONTINUOUS)

        # apply (trivial) initial constraints
        cls._apply_trivial_constraints()

    @classmethod
    def _apply_trivial_constraints(cls) -> None:
        # bw and bw_inv reciprocity
        for i in range(cls.network.dims_count):
            cls._gp_model.addConstr(cls._bw[i] * cls._bw_inv[i] == 1)

        # calculate cost
        network_cost = cls.cost_model.compute_network_cost(bw=cls._bw)
        cls._gp_model.addLConstr(cls._network_cost == network_cost)

    def _apply_coll_time_constraints(self) -> None:
        # for every layer and phase:
        for layer in range(self.workload.layers_count):
            for phase in range(3):
                # coll time = max[dim time]
                coll_time = gp.max_([self.dim_time[layer, phase, dim] for dim in range(self.network.dims_count)])
                Model._gp_model.addConstr(self.coll_time[layer, phase] == coll_time)

    def _apply_dim_time_constraints(self) -> None:
        # for every layer and phase:
        for layer in range(self.workload.layers_count):
            self._apply_dim_time_sub_constraints(layer_idx=layer, phase_idx=0,
                                                 phase=self.workload.layers[layer].forward,
                                                 communicator=self.communicator.forward_communicator)

            # input grad pass
            self._apply_dim_time_sub_constraints(layer_idx=layer, phase_idx=1,
                                                 phase=self.workload.layers[layer].input_grad,
                                                 communicator=self.communicator.input_grad_communicator)

            self._apply_dim_time_sub_constraints(layer_idx=layer, phase_idx=2,
                                                 phase=self.workload.layers[layer].weight_grad,
                                                 communicator=self.communicator.weight_grad_communicator)

    def _apply_dim_time_sub_constraints(self, layer_idx: int, phase_idx: int, phase: Phase,
                                        communicator: List[int]) -> None:
        # calculate message sizes per each dimension
        msg_sizes_per_dim: List[float] = [0.0 for _ in range(self.network.dims_count)]

        # carry over processed chunk size of last dimension
        last_chunk_size = phase.comm_size

        if phase.comm_type == Collective.NoComm:
            # just keep message size as 0, so that the collective time becomes 0 as well
            pass
        elif phase.comm_type == Collective.AllReduce:
            for dim, communicator_size in enumerate(communicator):
                if communicator_size < 0:
                    continue

                # set collective size
                all_reduce_size = 2 * last_chunk_size / communicator_size * (communicator_size - 1)
                msg_sizes_per_dim[dim] = all_reduce_size

                # resize last_chunk_size
                last_chunk_size /= communicator_size
        elif phase.comm_type == Collective.AllGather:
            for dim in range(self.network.dims_count - 1, -1, -1):
                # All-gather traverses in reversed order
                communicator_size = communicator[dim]

                # All-Gather traverses dimensions in reverse order
                if communicator_size < 0:
                    continue

                # set collective size
                all_gather_size = last_chunk_size * (communicator_size - 1)
                msg_sizes_per_dim[dim] = all_gather_size

                # resize last_chunk_size
                last_chunk_size *= communicator_size
        elif phase.comm_type == Collective.ReduceScatter:
            for dim, communicator_size in enumerate(communicator):
                if communicator_size < 0:
                    continue

                # set collective size
                reduce_scatter_size = last_chunk_size / communicator_size * (communicator_size - 1)
                msg_sizes_per_dim[dim] = reduce_scatter_size

                # resize last_chunk_size
                last_chunk_size /= communicator_size
        elif phase.comm_type == Collective.AllToAll:
            for dim, communicator_size in enumerate(communicator):
                if communicator_size < 0:
                    continue

                # set collective size
                all_to_all_size = last_chunk_size / communicator_size * (communicator_size - 1)
                msg_sizes_per_dim[dim] = all_to_all_size

                # don't resize since it's All-to-All
        else:
            # shouldn't reach here
            raise ModelError(f"Unknown communicator type: {phase.comm_type}")

        # calculate dim_time
        for dim in range(self.network.dims_count):
            dim_time = msg_sizes_per_dim[dim] * Model._bw_inv[dim]
            Model._gp_model.addLConstr(self.dim_time[layer_idx, phase_idx, dim] == dim_time)

    def _update_e2e_time(self, training_loop: Callable[['Model'], gp.LinExpr]) -> None:
        # get e2e time
        e2e_time = training_loop(self)

        # update global e2e time
        self._e2e_time += e2e_time
