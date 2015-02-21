#! /usr/bin/env python3

import unittest
from revision_module import RevisionModule, RevCAddB, RevCIAddB
import mnm_repr
import exp_repr
from archive import Archive, AdditionalModels, NewResults


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


	def test_check_consistency_positive(self):
		met1 = mnm_repr.Metabolite('met1')
		met2 = mnm_repr.Metabolite('met2')
		comp1 = mnm_repr.Medium()
		cond_subst_1 = mnm_repr.PresentEntity(met1, comp1)
		cond_subst_2 = mnm_repr.PresentEntity(met2, comp1)
		base_model = mnm_repr.Model('m1', [cond_subst_1, cond_subst_2], [], [])
		exd = exp_repr.ExperimentDescription(exp_repr.DetectionEntity('met1'), [])
		res = exp_repr.Result('r1', exd, 'true')
		exp = exp_repr.Experiment('exp1', [res])

		arch = Archive()
		arch.mnm_entities = [met1, met2]
		arch.mnm_compartments = [comp1]
		ev1 = AdditionalModels([base_model])
		ev2 = NewResults(exp)
		arch.record(ev1)
		arch.record(ev2)

		rev = RevisionModule(arch)
		out = rev.check_consistency(base_model)
		self.assertEqual(True, out)


	def test_check_consistency_negative(self):
		met1 = mnm_repr.Metabolite('met1')
		met2 = mnm_repr.Metabolite('met2')
		comp1 = mnm_repr.Medium()
		cond_subst_1 = mnm_repr.PresentEntity(met1, comp1)
		cond_subst_2 = mnm_repr.PresentEntity(met2, comp1)
		base_model = mnm_repr.Model('m1', [cond_subst_1, cond_subst_2], [], [])
		exd = exp_repr.ExperimentDescription(exp_repr.DetectionEntity('met1'), [])
		res = exp_repr.Result('r1', exd, 'false')
		exp = exp_repr.Experiment('exp1', [res])

		arch = Archive()
		arch.mnm_entities = [met1, met2]
		arch.mnm_compartments = [comp1]
		ev1 = AdditionalModels([base_model])
		ev2 = NewResults(exp)
		arch.record(ev1)
		arch.record(ev2)

		rev = RevisionModule(arch)
		out = rev.check_consistency(base_model)
		self.assertEqual(False, out)


	def test_calculate_max_number_activities(self):
		# model with activities, archive with results that have add activity in interventions
		a1 = mnm_repr.Activity('act1', None, ['a'], [])
		a2 = mnm_repr.Activity('act1', None, ['b'], [])
		a3 = mnm_repr.Activity('act1', None, ['c'], [])
		a4 = mnm_repr.Activity('act1', None, ['d'], [])

		base_model = mnm_repr.Model('m1', [], [a1], [])

		des1 = exp_repr.ExperimentDescription(None, [mnm_repr.Add(a2), mnm_repr.Add(a1)])
		des2 = exp_repr.ExperimentDescription(None, [mnm_repr.Add(a3)])
		des3 = exp_repr.ExperimentDescription(None, [mnm_repr.Add(a4), mnm_repr.Add(a3)])

		res1 = exp_repr.Result('r1', des1, None)
		res2 = exp_repr.Result('r2', des2, None)
		res3 = exp_repr.Result('r3', des3, None)

		exp1 = exp_repr.Experiment('exp1', [res1])
		exp2 = exp_repr.Experiment('exp2', [res2])
		exp3 = exp_repr.Experiment('exp3', [res3])

		arch = Archive()
		arch.known_results = [exp1, exp2, exp3]

		rev = RevisionModule(arch)

		out = rev.calculate_max_number_activities(base_model)

		self.assertEqual(out, 4)


	def test_RevCAddB_revise_positive(self):
		met1 = mnm_repr.Metabolite('met1')
		met2 = mnm_repr.Metabolite('met2')
		comp1 = mnm_repr.Medium()
		cond_subst_1 = mnm_repr.PresentEntity(met1, comp1)
		cond_subst_2 = mnm_repr.PresentEntity(met2, comp1)
		a1 = mnm_repr.Reaction('act1', [], [cond_subst_1])
		a2 = mnm_repr.Reaction('act1', [], [cond_subst_2])
		# model to be revised
		mod = mnm_repr.Model('m', [], [a1], [])
		# results
		des1 = exp_repr.ExperimentDescription(exp_repr.DetectionEntity('met1'), [])
		des2 = exp_repr.ExperimentDescription(exp_repr.DetectionEntity('met2'), [])
		res1 = exp_repr.Result('r1', des1, 'false')
		res2 = exp_repr.Result('r2', des2, 'true')
		exp1 = exp_repr.Experiment('exp1', [res1])
		exp2 = exp_repr.Experiment('exp2', [res2])
		# archive with results and parts for revision
		arch = Archive()
		arch.known_results = [exp1, exp2]
		arch.mnm_activities = [a1, a2]
		arch.mnm_entities = [met1, met2]
		arch.mnm_compartments = [comp1]

		rev = RevCAddB(arch)
		out = rev.revise(mod)

		self.assertEqual(out[1], False)
		self.assertEqual(out[0][0].intermediate_activities, frozenset([]))


	def test_RevCAddB_revise_negative(self):
		met1 = mnm_repr.Metabolite('met1')
		met2 = mnm_repr.Metabolite('met2')
		comp1 = mnm_repr.Medium()
		cond_subst_1 = mnm_repr.PresentEntity(met1, comp1)
		cond_subst_2 = mnm_repr.PresentEntity(met2, comp1)
		a1 = mnm_repr.Reaction('act1', [], [cond_subst_1, cond_subst_2])
		a1.remove_cost = None
		a2 = mnm_repr.Reaction('act1', [], [cond_subst_1])
		# model to be revised
		mod = mnm_repr.Model('m', [], [a1], [])
		# results
		des1 = exp_repr.ExperimentDescription(exp_repr.DetectionEntity('met1'), [])
		des2 = exp_repr.ExperimentDescription(exp_repr.DetectionEntity('met2'), [])
		res1 = exp_repr.Result('r1', des1, 'false')
		res2 = exp_repr.Result('r2', des2, 'true')
		exp1 = exp_repr.Experiment('exp1', [res1])
		exp2 = exp_repr.Experiment('exp2', [res2])
		# archive with results and parts for revision
		arch = Archive()
		arch.known_results = [exp1, exp2]
		arch.mnm_activities = [a1, a2]
		arch.mnm_entities = [met1, met2]
		arch.mnm_compartments = [comp1]

		rev = RevCAddB(arch)
		out = rev.revise(mod)
		self.assertEqual(out, False)

	def test_RevCIAddB_revise_ignoring(self):
		met1 = mnm_repr.Metabolite('met1')
		met2 = mnm_repr.Metabolite('met2')
		comp1 = mnm_repr.Medium()
		cond_subst_1 = mnm_repr.PresentEntity(met1, comp1)
		cond_subst_2 = mnm_repr.PresentEntity(met2, comp1)
		a1 = mnm_repr.Reaction('act1', [], [cond_subst_1, cond_subst_2])
		a1.remove_cost = None
		a2 = mnm_repr.Reaction('act1', [], [cond_subst_1])
		# model to be revised
		mod = mnm_repr.Model('m_0', [], [a1], [])
		# results
		des1 = exp_repr.ExperimentDescription(exp_repr.DetectionEntity('met1'), [])
		des2 = exp_repr.ExperimentDescription(exp_repr.DetectionEntity('met2'), [])
		res1 = exp_repr.Result('res_0', des1, 'false')
		res2 = exp_repr.Result('res_1', des2, 'true')
		exp1 = exp_repr.Experiment('exp_0', [res1])
		exp2 = exp_repr.Experiment('exp_1', [res2])
		# archive with results and parts for revision
		arch = Archive()
		arch.known_results = [exp1, exp2]
		arch.mnm_activities = [a1, a2]
		arch.mnm_entities = [met1, met2]
		arch.mnm_compartments = [comp1]

		rev = RevCIAddB(arch)
		out = rev.revise(mod)
		self.assertEqual(out[0], [])
		self.assertEqual(out[1], True)
