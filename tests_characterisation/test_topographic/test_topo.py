#!/usr/bin/python2.6
import subprocess
import unittest
import compare_output

def run():
    # run the current version of topomult.py
    args = ['mpirun',
            '-mca', 'btl', '^openib',  # don't check for inifiniband
            '-np', '8',
            'python', '../topographic/py-files/topomult.py',
            '-i', 'test_topographic/topo_test_input/dem.asc',
            '-o', 'test_topographic/topo_actual_output']

    subprocess.call(args)

    # run unit test comparison of new output against the expected
    suite = unittest.TestLoader().loadTestsFromTestCase(compare_output.TestOutput)
    unittest.TextTestRunner(verbosity=2).run(suite)
