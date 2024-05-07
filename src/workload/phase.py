"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from src.workload.collective import Collective
from src.workload.workload_error import WorkloadError


class Phase:
    """
    Phase class encapsulates the information for each layer sub-phase
    i.e., Forward, InputGrad, and WeightGrad.
    """

    def __init__(self,
                 compute_time: float,
                 comm_type: Collective,
                 comm_size: float):
        """
        Initializer.

        :param compute_time: phase compute time (in ns)
        :param comm_type: phase collective type
        :param comm_size: phase collective "initial" communication size (in Bytes)
        """
        self.compute_time = compute_time
        self.comm_type = comm_type
        self.comm_size = comm_size

        # check validity
        if self.compute_time < 0:
            raise WorkloadError(f"Compute time given ({self.compute_time}) should be >= 0")

        if self.comm_size < 0:
            raise WorkloadError(f"Communication size given ({self.comm_size}) should be >= 0")
