[//]: # (This source code is licensed under the MIT license found in the)
[//]: # (LICENSE file in the root directory of this source tree.)

# LIBRA

LIBRA is a comprehensive, multi-dimensional network optimization framework. By
considering an array of target DNN models, network shapes, and design constraints, LIBRA optimizes either
end-to-end execution performance or network/system performance-per-cost. After the optimization process,
LIBRA yields a workload-aware BW configuration meeting all given design constraints.

Below figure summarizes the high-level overview of the LIBRA framework:
![LIBRA Abstraction](https://github.com/astra-sim/libra/blob/main/docs/images/libra_overview.png)

Please find more information about LIBRA in [this paper](https://arxiv.org/abs/2109.11762).
- William Won, Saeed Rashidi, Sudarshan Srinivasan, and Tushar Krishna, "LIBRA: Enabling Workload-aware Multi-dimensional Network Topology Optimization for Distributed Training of Large AI Models," Proceedings of the 2024 IEEE International Symposium on Performance Analysis of Systems and Software (ISPASS '24), May 2024.

## How to Use
### Prerequisite
- `Python >= 3.8`
- `pyyaml`
- `gurobipy` ([How to install](https://support.gurobi.com/hc/en-us/articles/360044290292-How-do-I-install-Gurobi-for-Python)) and its license

### Setting Inputs
Inputs are defined and can be updated in the `inputs/` directory.
- Network: See `inputs/network/4d_network.yml` as an example. We define per-dimension topology shape and size.
- Workload: See `inputs/workload/MSFT_1T.txt` as an example. We follow the [ASTRA-sim1.0 workload style](https://github.com/astra-sim/astra-sim/tree/ASTRA-sim-1.0/inputs/workload)
- Communicator: See `inputs/communicator/MSFT_1T_4d.yml` as an example. You define how many NPUs are involved in each DP and TP communication.
- Cost Model: See `inputs/cost_model/4d_cost_model.yml`. You define per-BW dollar cost of each network component of each dimension.
- Training Loop: See `inputs/training_loop/no_overlap.py` as an example. You define training loop in Python.
- Constraints: See `inputs/constraints/multiple_constraints.py`. You define design constraints in `gurobipy`.

After setting them, you load these in `inputs/libra_configs.py` file.

### Running LIBRA
After all inputs are set, run `./libra.sh`

## Contact Us

For any questions about LIBRA, please contact [Will Won](mailto:william.won@gatech.edu)
or [Tushar Krishna](mailto:tushar@ece.gatech.edu).
