import os

"""
.. module:: misc.py
   :synopsis: Misc util module

.. moduleauthor:: Daniel Wild <daniel.wild@ga.gov.au>


"""


DIRECTIONS = 'e', 'n', 'ne', 'nw', 's', 'se', 'sw', 'w'


class TestPaths:
    """
    Used to build test paths

    """

    def __init__(self):

        # static paths
        self.ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname('Wind_multipliers'), '..'))
        self.TEST_DIR = os.path.join(self.ROOT_DIR, 'tests_characterisation')
        self.BASE_TOPO_TEST_DIR = os.path.join(self.TEST_DIR, 'test_topographic')
        self.TOPO_MULTI_DIR = os.path.join(self.ROOT_DIR, 'topographic')

        # dynamic paths
        self.TOPO_TEST_DIR = None
        self.TOPO_TEST_INPUT_DIR = None
        self.TOPO_TEST_ACTUAL_OUTPUT_DIR = None
        self.TOPO_TEST_EXPECTED_OUTPUT_DIR = None


    def initTopoTestPaths(self, test_size):
        """
        Builds test dir paths depending on test_size

        :param test_size: The size of the test to run.
        :type test_size: str.
        """

        self.TOPO_TEST_DIR = os.path.join(self.BASE_TOPO_TEST_DIR, test_size + '_test')
        self.TOPO_TEST_INPUT_DIR = os.path.join(self.TOPO_TEST_DIR, 'topo_test_input')
        self.TOPO_TEST_ACTUAL_OUTPUT_DIR = os.path.join(self.TOPO_TEST_DIR, 'topo_actual_output')
        self.TOPO_TEST_EXPECTED_OUTPUT_DIR = os.path.join(self.TOPO_TEST_DIR, 'topo_expected_output')