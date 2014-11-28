#! /usr/bin/env python3

import unittest
from tests import mnm_repr_test
from tests import exp_repr_test


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

suite14 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.PresentTest)

suite15 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.InterventionTest)

suite16 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.AddTest)

suite17 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.RemoveTest)

suite18 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.ModelTest)

suite19 = unittest.TestLoader().loadTestsFromTestCase(exp_repr_test.ExperimentTypeTest)

suite20 = unittest.TestLoader().loadTestsFromTestCase(exp_repr_test.ReconstructionActivityTest)

suite21 = unittest.TestLoader().loadTestsFromTestCase(exp_repr_test.ReconstructionEnzReactionTest)

suite22 = unittest.TestLoader().loadTestsFromTestCase(exp_repr_test.ReconstructionTransporterRequiredTest)

suite23 = unittest.TestLoader().loadTestsFromTestCase(exp_repr_test.DetectionActivityTest)

suite24 = unittest.TestLoader().loadTestsFromTestCase(exp_repr_test.DetectionEntityTest)

suite25 = unittest.TestLoader().loadTestsFromTestCase(exp_repr_test.LocalisationEntityTest)

suite26 = unittest.TestLoader().loadTestsFromTestCase(exp_repr_test.ExperimentDescriptionTest)

suite27 = unittest.TestLoader().loadTestsFromTestCase(exp_repr_test.ResultTest)

suite28 = unittest.TestLoader().loadTestsFromTestCase(exp_repr_test.ExperimentTest)



suits = [suite1, suite2, suite3, suite4, suite5, suite6, suite7, suite8, suite9, suite10, suite11, suite12, suite13, suite14, suite15, suite16, suite17, suite18, suite19, suite20, suite21, suite22, suite23, suite24, suite25, suite26, suite27, suite28]

for suite in suits:
	print('\n\n')
	unittest.TextTestRunner(verbosity=2).run(suite)
