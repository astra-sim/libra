"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

import os
from typing import List

from src.workload import Layer
from src.workload.collective import Collective
from src.workload.phase import Phase
from src.workload.workload import Workload
from src.workload.workload_error import WorkloadError


class WorkloadParser:
    """
    WorkloadParser helps parse the workload yaml configuration file.
    """

    def __init__(self):
        """
        WorkloadParser initializer.
        """
        pass

    def parse(self, path: str) -> Workload:
        """
        Parse the given yaml workload model.

        :param path: path to the yaml workload model
        :return: parsed Workload
        """
        # check the file exists
        if not os.path.exists(path):
            raise WorkloadError(f"Workload model {path} does not exist.")

        # load workload info
        with open(path, 'r') as workload_file:
            layer_strings = workload_file.readlines()

        # parse each layer
        layers: List[Layer] = list()

        for layer_str in layer_strings:
            layer = WorkloadParser.parse_layer_str(layer_str)
            layers.append(layer)

        # create and return workload
        return Workload(layers=layers)

    @staticmethod
    def parse_layer_str(layer_str: str) -> Layer:
        """
        Parse a given string with layer info (in ASTRA-sim1.0 format)
        and create a Layer instance from it.

        :param layer_str: string with layer information (in ASTRA-sim1.0 format)
        :return: Layer instance
        """
        # split layer info
        layer_info = layer_str.strip().split()

        # assert it has 12 info (ASTRA-sim1.0 workload format)
        if len(layer_info) != 12:
            raise WorkloadError(
                f"Make sure layer ({layer_str.strip()}) follows the ASTRA-sim1.0 workload representation format.")

        # create layer phases
        forward_phase = WorkloadParser.create_phase(info=layer_info[2:5])
        input_grad_phase = WorkloadParser.create_phase(info=layer_info[5:8])
        weight_grad_phase = WorkloadParser.create_phase(info=layer_info[8:11])

        # create and return layer
        layer = Layer(forward=forward_phase,
                      input_grad=input_grad_phase,
                      weight_grad=weight_grad_phase)
        return layer

    @staticmethod
    def create_phase(info: List[str]) -> Phase:
        """
        Create a Phase object by parsing the phase information.

        :param info: [compute time, comms type, commms size] (in strings)
        :return: Phase instance
        """
        try:
            compute_time = float(info[0])
            comm_type = WorkloadParser.get_comms_type(name=info[1])
            comm_size = float(info[2])

            return Phase(compute_time=compute_time,
                         comm_type=comm_type,
                         comm_size=comm_size)
        except ValueError:
            raise WorkloadError(f"Invalid phase info: {info}.")

    @staticmethod
    def get_comms_type(name: str) -> Collective:
        """
        Translate a communication name into a Collective instance.
        - "NONE" -> NoComm
        - "REDUCESCATTER" -> ReduceScatter
        - "ALLGATHER" -> AllGather
        - "ALLREDUCE" -> AllReduce
        - "ALLTOALL" -> AllToAll

        name is case-insensitive, but shouldn't have hyphens (e.g., "All-Reduce" wouldn't work).

        :param name: name of the communication
        :return: Collective instance
        """
        query = name.strip().lower()

        if query == 'none':
            return Collective.NoComm

        if query == 'reducescatter':
            return Collective.ReduceScatter

        if query == 'allgather':
            return Collective.AllGather

        if query == 'allreduce':
            return Collective.AllReduce

        if query == 'alltoall':
            return Collective.AllToAll

        # shouldn't reach here
        raise WorkloadError(f"{name} is not a valid communication type.")
