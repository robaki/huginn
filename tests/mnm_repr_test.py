#! /usr/bin/env python3

import unittest
import mnm_repr

class ModelTest(unittest.TestCase):

	def test_setup_with_lists(self):
		con1 = mnm_repr.PresentEntity('ent1','comp1')
		con2 = mnm_repr.PresentEntity('ent2','comp2')
		con3 = mnm_repr.PresentEntity('ent3','comp3')
		con4 = mnm_repr.PresentEntity('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1', [], [])
		act2 = mnm_repr.Activity('ID2', 'name2', [], [])
		setup_conds = [con1, con2]
		interm_activs = [act1, act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.assertEqual(self.model.ID, 'ID')
		self.assertEqual(self.model.setup_conditions, frozenset(setup_conds))
		self.assertEqual(self.model.intermediate_activities, frozenset(interm_activs))
		self.assertEqual(self.model.termination_conditions, frozenset(term_conds))


	def test_apply_intervention_add_condition(self):
		con1 = mnm_repr.PresentEntity('ent1','comp1')
		con2 = mnm_repr.PresentEntity('ent2','comp2')
		con3 = mnm_repr.PresentEntity('ent3','comp3')
		con4 = mnm_repr.PresentEntity('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1', [], [])
		act2 = mnm_repr.Activity('ID2', 'name2', [], [])
		intervention = mnm_repr.Add(con1)
		setup_conds = [con2]
		interm_activs = [act1, act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.model.apply_intervention(intervention)
		self.assertEqual(self.model.setup_conditions, frozenset([con2, con1]))


	def test_apply_intervention_remove_condition(self):
		con1 = mnm_repr.PresentEntity('ent1','comp1')
		con2 = mnm_repr.PresentEntity('ent2','comp2')
		con3 = mnm_repr.PresentEntity('ent3','comp3')
		con4 = mnm_repr.PresentEntity('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1', [], [])
		act2 = mnm_repr.Activity('ID2', 'name2', [], [])
		intervention = mnm_repr.Remove(con1)
		setup_conds = [con1, con2]
		interm_activs = [act1, act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.model.apply_intervention(intervention)
		self.assertEqual(self.model.setup_conditions, frozenset([con2]))


	def test_apply_intervention_add_activity(self):
		con1 = mnm_repr.PresentEntity('ent1','comp1')
		con2 = mnm_repr.PresentEntity('ent2','comp2')
		con3 = mnm_repr.PresentEntity('ent3','comp3')
		con4 = mnm_repr.PresentEntity('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1', [], [])
		act2 = mnm_repr.Activity('ID2', 'name2', [], [])
		intervention = mnm_repr.Add(act1)
		setup_conds = [con1, con2]
		interm_activs = [act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.model.apply_intervention(intervention)
		self.assertEqual(self.model.intermediate_activities, frozenset([act2, act1]))


	def test_apply_intervention_remove_activity(self):
		con1 = mnm_repr.PresentEntity('ent1','comp1')
		con2 = mnm_repr.PresentEntity('ent2','comp2')
		con3 = mnm_repr.PresentEntity('ent3','comp3')
		con4 = mnm_repr.PresentEntity('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1', [], [])
		act2 = mnm_repr.Activity('ID2', 'name2', [], [])
		intervention = mnm_repr.Remove(act1)
		setup_conds = [con1, con2]
		interm_activs = [act1, act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.model.apply_intervention(intervention)
		self.assertEqual(self.model.intermediate_activities, frozenset([act2]))


	def test_apply_multiple_interventions(self):
		con1 = mnm_repr.PresentEntity('ent1','comp1')
		con2 = mnm_repr.PresentEntity('ent2','comp2')
		con3 = mnm_repr.PresentEntity('ent3','comp3')
		con4 = mnm_repr.PresentEntity('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1', [], [])
		act2 = mnm_repr.Activity('ID2', 'name2', [], [])
		intervention1 = mnm_repr.Add(con1)
		intervention2 = mnm_repr.Remove(con1)
		intervention3 = mnm_repr.Add(act1)
		intervention4 = mnm_repr.Remove(act1)
		setup_conds = [con2]
		interm_activs = [act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.model.apply_interventions([intervention1, intervention2, intervention3, intervention4])
		self.assertEqual(self.model.setup_conditions, frozenset([con2]))
		self.assertEqual(self.model.intermediate_activities, frozenset([act2]))


	def test_apply_intervention_raise_not_intervention(self):
		con1 = mnm_repr.PresentEntity('ent1','comp1')
		con2 = mnm_repr.PresentEntity('ent2','comp2')
		con3 = mnm_repr.PresentEntity('ent3','comp3')
		con4 = mnm_repr.PresentEntity('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1', [], [])
		act2 = mnm_repr.Activity('ID2', 'name2', [], [])
		intervention = 'fake intervention'
		setup_conds = [con1, con2]
		interm_activs = [act1, act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.assertRaises(TypeError, self.model.apply_intervention, intervention)


	def test_apply_intervention_raise_not_intervention(self):
		con1 = mnm_repr.PresentEntity('ent1','comp1')
		con2 = mnm_repr.PresentEntity('ent2','comp2')
		con3 = mnm_repr.PresentEntity('ent3','comp3')
		con4 = mnm_repr.PresentEntity('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1', [], [])
		act2 = mnm_repr.Activity('ID2', 'name2', [], [])
		intervention = 'fake intervention'
		setup_conds = [con1, con2]
		interm_activs = [act1, act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.assertRaises(TypeError, self.model.apply_intervention, intervention)


	def test_apply_intervention_raise_neither_cond_nor_activity(self):
		con1 = mnm_repr.PresentEntity('ent1','comp1')
		con2 = mnm_repr.PresentEntity('ent2','comp2')
		con3 = mnm_repr.PresentEntity('ent3','comp3')
		con4 = mnm_repr.PresentEntity('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1', [], [])
		act2 = mnm_repr.Activity('ID2', 'name2', [], [])
		intervention = mnm_repr.Intervention('nothing')
		setup_conds = [con1, con2]
		interm_activs = [act1, act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.assertRaises(TypeError, self.model.apply_intervention, intervention)
