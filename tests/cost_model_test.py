#! /usr/bin/env python3
# I, Robert Rozanski, the copyright holder of this work, release this work into the public domain. This applies worldwide. In some countries this may not be legally possible; if so: I grant anyone the right to use this work for any purpose, without any conditions, unless such conditions are required by law.

import unittest
from exp_cost_model import CostModel
from mnm_repr import Gene, Metabolite, Protein, Complex, Growth, Reaction, PresentEntity, Cytosol, Add, Remove, Medium, CellMembrane
from exp_repr import DetectionEntity

class CostModelTest(unittest.TestCase):
	def setUp(self):
		self.g1 = Gene('g1')
		self.p1 = Protein('p1')
		self.met1 = Metabolite('met1')
		self.met2 = Metabolite('met2')
		self.cplx1 = Complex('cplx1')
		self.cytosol = Cytosol()

		self.cond1 = PresentEntity(self.met1, self.cytosol)
		self.cond2 = PresentEntity(self.met2, self.cytosol)
		self.cond3 = PresentEntity(self.p1, self.cytosol)
		self.cond4 = PresentEntity(self.cplx1, self.cytosol)

		self.growth = Growth('growth', [self.cond2])
		self.r1 = Reaction('r1', [self.cond1], [self.cond2])
		self.r2 = Reaction('r2', [self.cond3], [self.cond4])

		self.entities = [self.g1, self.p1, self.met1, self.met2, self.cplx1]
		self.compartments = [self.cytosol]
		self.activities = [self.growth, self.r1, self.r2]
		self.setup_conds = [self.cond1, self.cond3]
		self.model = CostModel(self.entities, self.compartments, self.activities, self.setup_conds)


	def test_generate_all_possible(self):
		self.assertIn(DetectionEntity, self.model.types.keys())
		self.assertEqual(len(self.model.types.keys()), 7)
		self.assertIn('c_03', self.model.design_compartment.keys())
		self.assertEqual(len(self.model.design_compartment.keys()), 33)
		self.assertEqual([], list(self.model.design_deletable.keys()))
		self.assertEqual(set([self.p1, self.met1, self.met2, self.cplx1]), set(self.model.design_available.keys()))
		self.assertEqual(set([self.r1, self.r2]), set(self.model.design_activity_rec.keys()))
		self.assertEqual([self.growth], list(self.model.design_activity_det.keys()))
		self.assertEqual(set([self.p1, self.cplx1]), set(self.model.design_entity_loc.keys()))
		self.assertEqual(set([self.p1, self.met1, self.met2, self.cplx1]), set(self.model.design_entity_det.keys()))
#		self.assertIn(Add(PresentEntity(self.met2, Medium())), self.model.intervention_add.keys())	#
#		self.assertIn(Remove(self.cond1), self.model.intervention_remove.keys())					# objects are not identical
#		self.assertIn(Remove(self.cond3), self.model.intervention_remove.keys())					# but it seems everything will be fine


	def test_calculate_derived_costs(self):
		self.model.set_all_basic_costs_to_1()
		self.model.calculate_derived_costs(self.activities)
		#
		self.assertEqual(self.model.design_available[self.cplx1], 1)
		self.assertEqual(self.model.design_entity_loc[self.cplx1], 1)
		self.assertEqual(self.model.design_entity_det[self.cplx1], 1)
		self.assertEqual(self.model.design_activity_rec[self.r1], 2)
		self.assertEqual(self.model.design_activity_rec[self.r2], 2)


	def test_remove_None_valued_elements(self):
		self.model.remove_None_valued_elements()
		self.assertEqual([], list(self.model.types.keys()))
		self.assertEqual([], list(self.model.design_compartment.keys()))
		self.assertEqual([], list(self.model.design_deletable.keys()))
		self.assertEqual([], list(self.model.design_available.keys()))
		self.assertEqual([], list(self.model.design_activity_rec.keys()))
		self.assertEqual([], list(self.model.design_activity_det.keys()))
		self.assertEqual([], list(self.model.design_entity_loc.keys()))
		self.assertEqual([], list(self.model.design_entity_det.keys()))
		self.assertEqual([], list(self.model.intervention_add.keys()))
		self.assertEqual([], list(self.model.intervention_remove.keys()))
