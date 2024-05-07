"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from inputs.libra_configs import libra_configs
from src.communicator import CommunicatorError
from src.cost_model import CostModelError
from src.model import Model, ModelError
from src.network import NetworkError
from src.workload import WorkloadError


def libra() -> None:
    # print LIBRA program header
    print("=" * 80)
    print("LIBRA:")
    print("=" * 80)
    print("QP Optimization:")

    # load libra configs
    configs = libra_configs()
    network = configs['network']
    workload = configs['workload']
    communicator = configs['communicator']
    training_loop = configs['training_loop']
    cost_model = configs['cost_model']
    constraint = configs['constraint']
    objective = configs['objective']

    # initialize model
    Model.initialize_model(network=network, cost_model=cost_model)

    # apply constraints
    constraint()

    # instantiate target models
    model = Model(workload=workload, communicator=communicator, training_loop=training_loop)

    # execute QP solver
    model.solve(objective=objective, verbose=True)


def main() -> None:
    try:
        libra()
    except NetworkError as e:
        print(f"Network Error: {e}")
    except WorkloadError as e:
        print(f"Workload Error: {e}")
    except CostModelError as e:
        print(f"Cost Model Error: {e}")
    except CommunicatorError as e:
        print(f"Communicator Error: {e}")
    except ModelError as e:
        print(f"Model Error: {e}")


if __name__ == '__main__':
    main()
