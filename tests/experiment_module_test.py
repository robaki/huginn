#! /usr/bin/env python3

import unittest
from experiment_module import ExperimentModule
from mnm_repr import Gene, Metabolite, Protein, Complex, Growth, Reaction, PresentEntity, Cytosol, Add, Remove, Medium, CellMembrane, Model, Add, Remove
import exp_repr
from archive import Archive
from exp_cost_model import CostModel
from exp_repr import DetectionEntity, LocalisationEntity, DetectionActivity, AdamTwoFactorExperiment, ReconstructionActivity, ReconstructionEnzReaction, ReconstructionTransporterRequired, ExperimentDescription


class ExperimentModuleTest(unittest.TestCase):
	def setUp(self):
		# models:
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

		self.mod1 = Model('m0', self.setup_conds, [self.growth, self.r1], [])
		self.mod2 = Model('m1', self.setup_conds, [self.growth, self.r2], [])

		# cost_module:
		self.cost_model = CostModel(self.entities, self.compartments, self.activities, self.setup_conds)
		self.cost_model.set_all_basic_costs_to_1()
		self.cost_model.calculate_derived_costs(self.activities)
		self.cost_model.remove_None_valued_elements()

		# known results (one exp, both models consistent)
		self.exd = exp_repr.ExperimentDescription(exp_repr.DetectionEntity('met1'), [])
		self.res = exp_repr.Result('res1', self.exd, 'true')
		self.exp = exp_repr.Experiment('exp1', [self.res])

		# archive
		self.arch = Archive()
		self.arch.working_models = [self.mod1, self.mod2]
		self.arch.known_results = [self.exp]
		self.arch.mnm_compartments = self.compartments
		self.arch.mnm_entities = self.entities
		self.arch.mnm_activities = self.activities

		# exp module
		self.exp_module = ExperimentModule(self.arch, self.cost_model, False)


	def test_calculate_constant_for_scores(self):
		self.assertEqual(self.exp_module.calculate_constant_for_scores(), 10)


	def test_design_experiments_nocost(self): # cost=False
		exps = self.exp_module.design_experiments()
		self.assertEqual(exps[0].experiment_type.activity_id, 'growth')
		self.assertIsInstance(exps[0].experiment_type, DetectionActivity)
		self.assertEqual(exps[0].interventions, frozenset([]))


	def test_design_experiments_cost(self): # cost=True
		self.exp_module.use_costs = True
		exps = self.exp_module.design_experiments()
		self.assertEqual(exps[0].experiment_type.activity_id, 'growth')
		self.assertIsInstance(exps[0].experiment_type, DetectionActivity)
		self.assertEqual(exps[0].interventions, frozenset([]))

#
# processing output:
#

#	def test_process_output(self):
#		process_output(out)  need some input with interventions


	def test_get_answers(self):
		strings = ['clasp version 3.0.3', 'Reading from stdin', 'Solving...',
		'Answer: 1', 'design_type(detection_activity_exp) design_activity_det(growth)',
		'Optimization: 0', 'OPTIMUM FOUND', 'Models       : 1     ',
		'  Optimum    : yes', 'Optimization : 0', 'Calls        : 1',
		'Time         : 0.020s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)',
		'CPU Time     : 0.010s']
		ans = self.exp_module.get_answers(strings)
		self.assertEqual('design_type(detection_activity_exp) design_activity_det(growth)', ans[0])


	def test_get_expType(self):
		components = ['design_type(detection_activity_exp)', 'design_activity_det(growth)']
		ty = self.exp_module.get_expType(components)
		self.assertEqual('design_type(detection_activity_exp)', ty)


	def test_process_exp_type_adam_two_factor(self):
		components = ['design_deletable(g_1)', 'design_available(met_1)']
		extype = self.exp_module.process_exp_type_adam_two_factor(components)
		self.assertEqual(AdamTwoFactorExperiment('g_1', 'met_1'), extype)


	def test_process_exp_type_transp_reconstruction(self):
		components = ['design_activity_rec(trp1)', 'design_available(transporter1)']
		extype = self.exp_module.process_exp_type_transp_reconstruction(components)
		self.assertEqual(ReconstructionTransporterRequired('trp1', 'transporter1'), extype)


	def test_process_exp_type_enz_reconstruction(self):
		components = ['design_activity_rec(r1)', 'design_available(enz1)']
		extype = self.exp_module.process_exp_type_enz_reconstruction(components)
		self.assertEqual(ReconstructionEnzReaction('r1', 'enz1'), extype)


	def test_process_exp_type_basic_reconstruction(self):
		components = ['design_activity_rec(r1)']
		extype = self.exp_module.process_exp_type_basic_reconstruction(components)
		self.assertEqual(ReconstructionActivity('r1'), extype)


	def test_process_exp_type_detection_activity(self):
		components = ['design_activity_det(growth)']
		extype = self.exp_module.process_exp_type_detection_activity(components)
		self.assertEqual(DetectionActivity('growth'), extype)


	def test_process_exp_type_localisation_entity(self):
		components = ['design_entity_loc(met_1)', 'design_compartment(c_01)']
		extype = self.exp_module.process_exp_type_localisation_entity(components)
		self.assertEqual(LocalisationEntity('met_1', 'c_01'), extype)


	def test_process_exp_type_detection_entity(self):
		components = ['design_entity_det(met_1)']
		extype = self.exp_module.process_exp_type_detection_entity(components)
		self.assertEqual(DetectionEntity('met_1'), extype)


	def test_get_interventions(self):
		components = ['add(setup_present(met1,none,c_05))', 'remove(setup_present(met2,none,c_05))', 'add(r123)']
		interventions = self.exp_module.get_interventions(components)
		eval_info = []
		for inter in interventions:
			try:
				eval_info.append((inter.condition_or_activity.entity.ID, inter.condition_or_activity.compartment.ID))
			except:
				eval_info.append()

		self.assertIn(('met1', 'c_05'), eval_info)
		self.assertIn(('met2', 'c_05'), eval_info)

