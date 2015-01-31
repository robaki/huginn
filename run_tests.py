#! /usr/bin/env python3

import unittest
from tests import mnm_repr_test
from tests import archive_test
from tests import quality_module_test

suite_1 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.ModelTest)
suite_2 = unittest.TestLoader().loadTestsFromTestCase(archive_test.ArchiveTest)
suite_3 = unittest.TestLoader().loadTestsFromTestCase(quality_module_test.QualityModuleTest)



suits = [suite_1, suite_2, suite_3]

for suite in suits:
	print('\n\n')
	unittest.TextTestRunner(verbosity=2).run(suite)
