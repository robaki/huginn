#! /usr/bin/env python3

import unittest
from experiment_module import ExperimentModule
from mnm_repr import Gene, Metabolite, Protein, Complex, Growth, Reaction, PresentEntity, Cytosol, Add, Remove, Medium, CellMembrane, Model
import exp_repr
from archive import Archive
from exp_cost_model import CostModel

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
		self.exp_module = ExperimentModule(self.arch, self.cost_model)


	def test_calculate_constant_for_scores(self):
		self.assertEqual(self.exp_module.calculate_constant_for_scores(), 10)


	def test_design_experiments_nocost(self): # cost=False
		self.exp_module.design_experiments()


	def test_design_experiments_cost(self): # cost=True
		self.exp_module.use_costs = True
		self.exp_module.design_experiments()

#	def test_(self):
#
#	def test_(self):
#
#	def test_(self):
