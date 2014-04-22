import unittest

"""
.. module:: parametrized_test_case.py
   :synopsis: Module used to facilitate parametrized unit tests

.. moduleauthor:: Daniel Wild <daniel.wild@ga.gov.au>


"""


class ParametrizedTestCase(unittest.TestCase):
    """
    TestCase classes that want to be parametrized should
    inherit from this class.

    """
    def __init__(self, methodName='runTest', param=None):
        super(ParametrizedTestCase, self).__init__(methodName)
        self.param = param

    @staticmethod
    def parametrize(testcase_klass, param=None):
        """
        Create a suite containing all tests taken from the given
        subclass, passing them the parameter 'param'.

        :param testcase_klass: The test class to be parametrized
        :param param: The param to pass in

        """
        testloader = unittest.TestLoader()
        testnames = testloader.getTestCaseNames(testcase_klass)
        suite = unittest.TestSuite()
        for name in testnames:
            suite.addTest(testcase_klass(name, param=param))
        return suite


