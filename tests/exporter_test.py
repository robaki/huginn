#! /usr/bin/env python3

import unittest
import exporter
import mnm_repr
import exp_repr

class ExporterTest(unittest.TestCase):
	def test_export_entities_alone(self):
		# get one of entity types; no need to test all (they do the same thing)
		ent1 = mnm_repr.Gene('e1')
		ent2 = mnm_repr.Metabolite('e2')
		ent3 = mnm_repr.Protein('e3')
		ent4 = mnm_repr.Complex('e4')
		exported = exporter.export_entities([ent1, ent2, ent3, ent4])
		self.assertEqual("\ngene(e1,None).", exported[0])
		self.assertEqual("\nmetabolite(e2,None).", exported[1])
		self.assertEqual("\nprotein(e3,None).", exported[2])
		self.assertEqual("\ncomplex(e4,None).", exported[3])

	def test_export_entities_properties(self):
		# entity with properties to test the second part of the method
		ent3 = mnm_repr.Protein('e3', None, None, [mnm_repr.Catalyses(mnm_repr.Activity('a1', None, [], []))])
		ent4 = mnm_repr.Complex('e4', None, None, [mnm_repr.Transports(mnm_repr.Activity('a2', None, [], []))])
		exported = exporter.export_entities([ent3, ent4])
		self.assertEqual("\nprotein(e3,None).", exported[0])
		self.assertEqual("\ncatalyses(e3,None,a1).", exported[1])
		self.assertEqual("\ncomplex(e4,None).", exported[2])
		self.assertEqual("\ntransports(e4,None,a2).", exported[3])

	def test_export_compartments(self):
		# a couple of compartments
		c1 = mnm_repr.Medium()
		c2 = mnm_repr.CellMembrane()
		c3 = mnm_repr.CellMembraneOuterSide()
		exported = exporter.export_compartments([c1, c2, c3])
		self.assertEqual("\ncompartment(c_01;c_02;c_03).", exported[0])

	def test_export_activity(self):
		# one substrate, one catalyst, one transporter; one product
		cond_subst = mnm_repr.PresentEntity(mnm_repr.Metabolite('met1'), mnm_repr.Medium())
		cond_cat = mnm_repr.PresentCatalyst(mnm_repr.Medium())
		cond_trp = mnm_repr.PresentTransporter(mnm_repr.Medium())
		prod = mnm_repr.PresentEntity(mnm_repr.Metabolite('met2'), mnm_repr.Medium())
		act = mnm_repr.Activity('a1', None, [cond_subst, cond_cat, cond_trp], [prod])
		exported = exporter.export_activity(act)
		self.assertIn('\nsubstrate(met1,None,c_01,a1).', exported)
		self.assertIn('\nenz_required(a1).', exported)
		self.assertIn('\nenz_compartment(c_01,a1).', exported)
		self.assertIn('\ntransp_required(a1).', exported)
		self.assertIn('\ntransp_compartment(c_01,a1).', exported)
		self.assertIn('\nproduct(met2,None,c_01,a1).', exported)

	def test_export_results(self):
		# one of exp types; no need to test all (they do the same thing)
		exp_type = exp_repr.LocalisationEntity('p1', 'c_02')
		res = exp_repr.Result('res1', exp_repr.ExperimentDescription(exp_type, []), True)
		exported = exporter.export_results([res])
		self.assertIn('\nresult(res1, experiment(localisation_entity_exp, p1, c_02), True).', exported)

	def test_export_model_specification(self):
		# 2 conds + 2 activ
		cond_subst_1 = mnm_repr.PresentEntity(mnm_repr.Metabolite('met1'), mnm_repr.Medium())
		cond_subst_2 = mnm_repr.PresentEntity(mnm_repr.Metabolite('met2'), mnm_repr.Medium())
		act_1 = mnm_repr.Activity('a1', None, ['1'], [])
		act_2 = mnm_repr.Activity('a2', None, ['2'], [])
		m = mnm_repr.Model('m1', [cond_subst_1, cond_subst_2], [act_1, act_2], [])
		exported = exporter.export_model_specification(m)
		self.assertIn('\nadded_to_model(setup_present(met1,None,c_01),m1).', exported)
		self.assertIn('\nadded_to_model(setup_present(met2,None,c_01),m1).', exported)
		self.assertIn('\nadded_to_model(a1,m1).', exported)
		self.assertIn('\nadded_to_model(a2,m1).', exported)

	def test_export_termination_conds(self):
		# one cond
		cond_subst_1 = mnm_repr.PresentEntity(mnm_repr.Metabolite('met1'), mnm_repr.Medium())
		cond_subst_2 = mnm_repr.PresentEntity(mnm_repr.Metabolite('met2'), mnm_repr.Medium())
		m = mnm_repr.Model('m1', [], [], [cond_subst_1, cond_subst_2])
		exported = exporter.export_termination_conds(m)
		self.assertIn('\n#example synthesizable(met1, None, c_01, m1).', exported)
		self.assertIn('\n#example synthesizable(met2, None, c_01, m1).', exported)

	def test_export_relevancy_results(self):
		# one ignored result, one not ignored
		res1 = exp_repr.Result('res1', None, None)
		res2 = exp_repr.Result('res2', None, None)
		m = mnm_repr.Model('m1', [], [], [])
		m.ignored_results = frozenset([res1])

		base_model = m
		models_results = {m:[res1, res2]}

		exported = exporter.export_relevancy_results(models_results, base_model)

		self.assertNotIn('\nrelevant(res1, m1).', exported)
		self.assertNotIn('\n#example not inconsistent(m1, res1).', exported)
		self.assertIn('\nrelevant(res2, m1).', exported)
		self.assertIn('\n#example not inconsistent(m1, res2).', exported)

