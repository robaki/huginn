#! /usr/bin/env python3

import unittest
import mnm_repr
from copy import copy

class ModelTest(unittest.TestCase):
	def setUp(self):
		self.con1 = mnm_repr.PresentEntity('ent1','comp1')
		self.con2 = mnm_repr.PresentEntity('ent2','comp2')
		self.con3 = mnm_repr.PresentEntity('ent3','comp3')
		self.con4 = mnm_repr.PresentEntity('ent4','comp4')
		self.act1 = mnm_repr.Activity('ID1', 'name1', [self.con1], [])
		self.act2 = mnm_repr.Activity('ID2', 'name2', [self.con2], [])

	def test_setup_with_lists(self):
		setup_conds = [self.con1, self.con2]
		interm_activs = [self.act1, self.act2]
		term_conds = [self.con3, self.con4]
		model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.assertEqual(model.ID, 'ID')
		self.assertEqual(model.setup_conditions, frozenset(setup_conds))
		self.assertEqual(model.intermediate_activities, frozenset(interm_activs))
		self.assertEqual(model.termination_conditions, frozenset(term_conds))


	def test_apply_intervention_add_condition(self):
		intervention = mnm_repr.Add(self.con1)
		setup_conds = [self.con2]
		interm_activs = [self.act1, self.act2]
		term_conds = [self.con3, self.con4]
		model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		model.apply_intervention(intervention)
		self.assertEqual(model.setup_conditions, frozenset([self.con2, self.con1]))


	def test_apply_intervention_remove_condition(self):
		intervention = mnm_repr.Remove(self.con1)
		setup_conds = [self.con1, self.con2]
		interm_activs = [self.act1, self.act2]
		term_conds = [self.con3, self.con4]
		model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		model.apply_intervention(intervention)
		self.assertEqual(model.setup_conditions, frozenset([self.con2]))


	def test_apply_intervention_add_activity(self):
		intervention = mnm_repr.Add(self.act1)
		setup_conds = [self.con1, self.con2]
		interm_activs = [self.act2]
		term_conds = [self.con3, self.con4]
		model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		model.apply_intervention(intervention)
		self.assertEqual(model.intermediate_activities, frozenset([self.act2, self.act1]))


	def test_apply_intervention_remove_activity(self):
		intervention = mnm_repr.Remove(self.act1)
		setup_conds = [self.con1, self.con2]
		interm_activs = [self.act1, self.act2]
		term_conds = [self.con3, self.con4]
		model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		model.apply_intervention(intervention)
		self.assertEqual(model.intermediate_activities, frozenset([self.act2]))


	def test_apply_multiple_interventions(self):
		intervention1 = mnm_repr.Add(self.con1)
		intervention2 = mnm_repr.Remove(self.con1)
		intervention3 = mnm_repr.Add(self.act1)
		intervention4 = mnm_repr.Remove(self.act1)
		setup_conds = [self.con2]
		interm_activs = [self.act2]
		term_conds = [self.con3, self.con4]
		model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		model.apply_interventions([intervention1, intervention2, intervention3, intervention4])
		self.assertEqual(model.setup_conditions, frozenset([self.con2]))
		self.assertEqual(model.intermediate_activities, frozenset([self.act2]))


	def test_apply_intervention_raise_not_intervention(self):
		intervention = 'fake intervention'
		setup_conds = [self.con1, self.con2]
		interm_activs = [self.act1, self.act2]
		term_conds = [self.con3, self.con4]
		model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.assertRaises(TypeError, model.apply_intervention, intervention)


	def test_apply_intervention_raise_not_intervention(self):
		intervention = 'fake intervention'
		setup_conds = [self.con1, self.con2]
		interm_activs = [self.act1, self.act2]
		term_conds = [self.con3, self.con4]
		model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.assertRaises(TypeError, model.apply_intervention, intervention)


	def test_apply_intervention_raise_neither_cond_nor_activity(self):
		intervention = mnm_repr.Intervention('nothing')
		setup_conds = [self.con1, self.con2]
		interm_activs = [self.act1, self.act2]
		term_conds = [self.con3, self.con4]
		model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.assertRaises(TypeError, model.apply_intervention, intervention)


	def test_copy(self):
		setup_conds = [self.con1, self.con2]
		interm_activs = [self.act1, self.act2]
		term_conds = [self.con3, self.con4]
		model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		copied_model = copy(model)
		self.assertEqual(model, copied_model)
		self.assertIsNot(model, copied_model)
