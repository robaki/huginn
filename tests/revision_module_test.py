#! /usr/bin/env python3

import unittest
from revision_module import RevisionModule, RevC, RevCI, RevCwI, RevCIw, RevCwIw
import mnm_repr
import exp_repr


class RevisionModuleTest(unittest.TestCase):
#	def test_check_consistency(self): # just gathers info from other methods
#	def test_prepare_input_results_models(self): # just gathers info from other methods

	def test_make_derivative_models(self):
		rev = RevisionModule('archive')
		cond_subst_1 = mnm_repr.PresentEntity(mnm_repr.Metabolite('met1'), mnm_repr.Medium())
		cond_subst_2 = mnm_repr.PresentEntity(mnm_repr.Metabolite('met2'), mnm_repr.Medium())
		base_model = mnm_repr.Model('m1', [cond_subst_1], [], [])#model that is compatible with interventions
		second_mod = mnm_repr.Model('deriv_m1_0', [cond_subst_1, cond_subst_2], [], [])
		third_mod = mnm_repr.Model('deriv_m1_1', [], [], [])

		exd1 = exp_repr.ExperimentDescription(None, [mnm_repr.Add(cond_subst_2)])
		exd2 = exp_repr.ExperimentDescription(None, [mnm_repr.Remove(cond_subst_1)])
		res1 = exp_repr.Result('r1', exd1, True)
		res2 = exp_repr.Result('r2', exd2, True)
		extracted_results = [res1, res2] #need interventions in description

		models_results = rev.make_derivative_models(base_model, extracted_results)
		self.assertEqual(models_results, {base_model:[], second_mod:[res1], third_mod:[res2]})
