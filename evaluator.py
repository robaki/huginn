#! /usr/bin/env python3

#from test_configurations import template_1
from exp_cost_model import CostModel
import pickle
from archive import Archive, InitialModels
from experiment_module import BasicExpModuleNoCosts
from experiment_module import BasicExpModuleWithCosts
from oracle import Oracle
from overseer import OverseerWithModQuality
from overseer import OverseerNoQuality
from quality_module import AllCovered
from quality_module import AllCoveredMinusIgnored
from quality_module import NewCovered
from quality_module import NewCoveredMinusIgnored
from revision_module import RevCAddB
from revision_module import RevCAddR
from revision_module import RevCIAddB# template: the best
from revision_module import RevCIAddR# template: random


#		self.test_case['initial_results']

class Evaluator:
	def __init__(self):
		self.test_case = None
		self.cost_model = None
		self.configuration_spec = None


	def quick_test(self):
		# test case
		pkl_file = open('test_cases/case_7', 'rb')
		self.test_case = pickle.load(pkl_file)
		pkl_file.close()

		archive_ = Archive()
		archive_.mnm_compartments = self.test_case['all_compartments']
		archive_.model_of_ref = self.test_case['model_of_ref']

		for ent in self.test_case['all_entities']:
			ent.ID = archive_.get_new_ent_id()
			archive_.mnm_entities.append(ent)
		for act in self.test_case['all_activities']:
			act.ID = archive_.get_new_act_id()
			archive_.mnm_activities.append(act)
		for act in self.test_case['add_import_activities']:
			act.ID = archive_.get_new_act_id()
			archive_.import_activities.append(act)
		
		archive_.record(InitialModels(self.test_case['initial_models']))

		quality_m = NewCoveredMinusIgnored(archive_)
		revision_m = RevCIAddR(archive_)

		self.cost_model = CostModel(self.test_case['all_entities'],
			self.test_case['all_compartments'], self.test_case['all_activities'],
			self.test_case['model_of_ref'].setup_conditions,
			self.test_case['add_import_activities'])
		self.cost_model.set_all_basic_costs_to_1()
		self.cost_model.calculate_derived_costs(self.test_case['all_activities'])
		self.cost_model.remove_None_valued_elements()

		exp_m = BasicExpModuleNoCosts(archive_, self.cost_model)
		oracle_ = Oracle(archive_, self.test_case['entities_ref'],
			self.test_case['activities_ref'], self.test_case['model_of_ref'],
			self.test_case['all_entities'], self.test_case['all_compartments'],
			self.test_case['all_activities'])

		overseer = OverseerWithModQuality(archive_, revision_m, exp_m, oracle_, 2, quality_m, 8)
		overseer.run()




evaluator = Evaluator()
evaluator.quick_test()
