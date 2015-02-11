#! /usr/bin/env python3

import exporter
import random
import subprocess

class ExperimentModule:
	# module for experiment design. Method relies on splitting sum of models' probabilities (qualities) in half.
	# If no model quality modules is used, then model quality = 1 and is constant throught development time.
	# In that case the algorithm just splits set of working models in half.
	def __init__(self, archive, cost_model, use_costs=False):
		self.archive = archive
		self.cost_model = cost_model
		self.use_costs = use_costs


	def get_experiment(self):
		exps = self.design_experiment()
		return random.choice(exps)


	def design_experiments(self):
		exp_input = self.prepare_input_for_exp_design()
		out = self.write_and_execute_gringo_clasp(exp_input)

#		experiments = self.process_output(out)
#		return experiments


	def process_output(self, output):
		# extract each model/answer
		# produce experiment based on an answer
		pass



	def write_and_execute_gringo_clasp(self, exp_input):
		# try remove the file
		with open('./temp/workfile_gringo_clasp', 'w') as f:
			for string in exp_input:
				read_data = f.write(string)
		# could suppress there warnig messages later on
		gringo = subprocess.Popen(['gringo', './temp/workfile_gringo_clasp'], stdout=subprocess.PIPE)
		clasp = subprocess.Popen(['clasp', '-n', '0'], stdin=gringo.stdout, stdout=subprocess.PIPE)
		gringo.stdout.close()
		output_enc = clasp.communicate()[0]
		output_dec = output_enc.decode('utf-8')
		return output_dec


	def prepare_input_for_exp_design(self):
		exported = []
		exported.extend(exporter.hide_show_statements()) # export hide/show stuff
		exported.extend(exporter.export_compartments(self.archive.mnm_compartments))
		exported.extend(exporter.export_entities(self.archive.mnm_entities))
		exported.extend(exporter.export_activities(self.archive.mnm_activities))
		exported.extend(exporter.export_models_exp_design(self.archive.working_models)) # export models info
		exported.extend(exporter.models_nr_and_probabilities(self.archive.working_models)) # + probabilities and numbers
		exported.append(exporter.modeh_replacement(self.cost_model)) # export design elements (modeh eqiv)
		exported.extend(exporter.design_constraints_basic()) # export rules forcing and restricting exp design
		for exp in self.archive.known_results:
			exp_descriptions = [res.exp_description for res in exp.results]
			for des in exp_descriptions:
				exported.extend(exporter.ban_experiment(des)) # export ban experiment(s) (from old exps)
		exported.append(exporter.constant_for_calculating_score(self.calculate_constant_for_scores())) # calculate constant for scores and export it
		exported.extend(exporter.advanced_exp_design_rules()) # export scoring rules/optimisation
		if self.use_costs: # * export cost, and optimisation rule for that
			exported.extend(exporter.cost_rules(self.cost_model))
			exported.extend(exporter.cost_minimisation_rules())
		else:
			pass
		exported.extend(exporter.experiment_design_rules()) # export design rules
		exported.extend(exporter.interventions_rules())
		exported.extend(exporter.predictions_rules())
		activities = [len(mod.intermediate_activities) for mod in self.archive.working_models]
		exported.extend(exporter.models_rules(max(activities))) # export modelling and prediction rules ASSUMES NO ACTIVITIES WILL BE ADDed
		return exported


	def calculate_constant_for_scores(self):
		return int((sum([mod.quality for mod in self.archive.working_models])*10)/2)
