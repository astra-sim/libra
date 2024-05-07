from typing import Any, Dict
from src.communicator import CommunicatorParser, CommunicatorError
from src.cost_model import CostModelParser, CostModelError
from src.model import Model, ModelError, SolverObjective
from src.network import NetworkParser, NetworkError
from src.workload import WorkloadParser, WorkloadError
from inputs.constraints import constraints
from inputs.training_loop import training_loops
from src.model import SolverObjective


# parse network, workload, cost_model, communicator, constraints, and training loop
def libra_configs():
    configs: Dict[str, Any] = dict()

    # ==========================================================
    network_parser = NetworkParser()
    network = network_parser.parse(path='./inputs/network/4d_network.yml')

    workload_parser = WorkloadParser()
    workload = workload_parser.parse(path='./inputs/workload/GPT_3.txt')

    cost_model_parser = CostModelParser()
    cost_model = cost_model_parser.parse(path='./inputs/cost_model/4d_cost_model.yml')

    communicator_parser = CommunicatorParser()
    communicator = communicator_parser.parse(path='./inputs/communicator/GPT_3_4d.yml')

    constraint = constraints['multiple_constraints']
    training_loop = training_loops['no_overlap']

    objective = SolverObjective.PerfOpt
    # objective = SolverObjective.PerfPerCostOpt
    # ==========================================================

    # setup and return configs
    configs['network'] = network
    configs['workload'] = workload
    configs['cost_model'] = cost_model
    configs['communicator'] = communicator
    configs['constraint'] = constraint
    configs['training_loop'] = training_loop
    configs['objective'] = objective

    return configs
