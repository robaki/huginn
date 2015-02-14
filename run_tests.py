#! /usr/bin/env python3

import unittest
from tests import mnm_repr_test
from tests import archive_test
from tests import quality_module_test
from tests import exporter_test
from tests import revision_module_test
from tests import cost_model_test
from tests import experiment_module_test
from tests import oracle_test

suite_1 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.ModelTest)
suite_2 = unittest.TestLoader().loadTestsFromTestCase(archive_test.ArchiveTest)
suite_3 = unittest.TestLoader().loadTestsFromTestCase(quality_module_test.QualityModuleTest)
suite_4 = unittest.TestLoader().loadTestsFromTestCase(exporter_test.ExporterTest)
suite_5 = unittest.TestLoader().loadTestsFromTestCase(revision_module_test.RevisionModuleTest)
suite_6 = unittest.TestLoader().loadTestsFromTestCase(cost_model_test.CostModelTest)
suite_7 = unittest.TestLoader().loadTestsFromTestCase(experiment_module_test.ExperimentModuleTest)
suite_8 = unittest.TestLoader().loadTestsFromTestCase(oracle_test.OracleTest)

suits = [suite_8] #suite_1, suite_2, suite_3, suite_4, suite_5, suite_6, suite_7, 

for suite in suits:
	print('\n\n')
	unittest.TextTestRunner(verbosity=2).run(suite)
