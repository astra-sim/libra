"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""


class NetworkError(Exception):
    """
    An error to be thrown when there's any issue with the network.
    """

    def __init__(self, message: str):
        """
        NetworkError initializer.

        :param message: exception error message
        """
        self.message = message
        super().__init__(self.message)
