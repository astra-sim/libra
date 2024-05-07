"""
This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""


class CommunicatorError(Exception):
    """
    An error to be thrown when there's any issue with the communicator.
    """

    def __init__(self, message: str):
        """
        CommunicatorError initializer.

        :param message: exception error message
        """
        self.message = message
        super().__init__(self.message)
