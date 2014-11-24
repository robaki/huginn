#! /usr/bin/env python3

import unittest
from tests import mnm_repr_test


suite1 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.ElementTest)

suite2 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.EntityTest)

suite3 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.GeneTest)

suite4 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.MetaboliteTest)

suite5 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.ProteinTest)

suite6 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.ComplexTest)

suite7 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.ActivityTest)

suite8 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.GrowthTest)

suite9 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.ExpressionTest)

suite10 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.NonEnzymaticReactionTest)

suite11 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.EnzymaticReactionTest)

suite12 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.TransporterNotRequiredTest)

suite13 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.TransporterRequiredTest)



suits = [suite1, suite2, suite3, suite4, suite5, suite6, suite7, suite8, suite9, suite10, suite11, suite12, suite13]

for suite in suits:
	print('\n\n')
	unittest.TextTestRunner(verbosity=2).run(suite)
