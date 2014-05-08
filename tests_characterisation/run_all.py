from test_topographic import test_topo
import unittest

from parametrized_test_case import ParametrizedTestCase


"""
.. module:: run_all
   :synopsis: Initiates Characterisation Test Suite for all Wind Multipliers

.. moduleauthor:: Daniel Wild <daniel.wild@ga.gov.au>


"""


def run():
    """
    Used to initiate testing across all multipliers using specified test size/coverage (defaults to small)

    """

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--size",
                        help="Test size (small, medium, large)",
                        choices=["small", "medium", "large"],
                        default="small",
                        type=str)

    args = parser.parse_args()

    suite = unittest.TestSuite()

    # Uncomment for DEM output test
    #suite.addTest(ParametrizedTestCase.parametrize(test_topo.TestOutput, param=args.size))

    # Dummy NETCDF test
    suite.addTest(ParametrizedTestCase.parametrize(test_topo.TestDummyOutput, param=args.size))

    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    run()