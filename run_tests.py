#! /usr/bin/env python3

import unittest
from tests import mnm_repr_test
from tests import exp_repr_test


suite = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.ModelTest)





suits = [suite]

for suite in suits:
	print('\n\n')
	unittest.TextTestRunner(verbosity=2).run(suite)
