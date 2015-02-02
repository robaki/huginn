#! /usr/bin/env python3

import exporter

from archive import RefutedModels
from archive import RevisedModel
from copy import copy
import subprocess
import mnm_repr

class RevisionModule:
	def __init__(self, archive, xhail="/usr/local/xhail-0.5.1/xhail.jar", gringo="/usr/local/xhail-0.5.1/gringo", clasp="/usr/local/xhail-0.5.1/clasp"):
		self.archive = archive
		self.xhail = xhail
		self.gringo = gringo
		self.clasp = clasp


	def check_consistency(self, model):
		res_mods = self.prepare_input_results_models_consistency(model)
		max_number_activities = self.calculate_max_number_activities(model)
		mod_rules = exporter.models_rules(max_number_activities)
		pred_rules = exporter.predictions_rules()
		incons_rules = exporter.inconsistency_rules()
		inpt = [res_mods, mod_rules, pred_rules, incons_rules]
		inpt = [val for sublist in inpt for val in sublist] # flatten
		raw_output = self.write_and_execute_xhail(inpt)
		outcome = self.process_output_consistency(raw_output)	
		return outcome


	def calculate_max_number_activities(self, model):
		results = [exp.results for exp in self.archive.known_results]
		results = [val for sublist in results for val in sublist] # flatten
		interventions = [res.exp_description.interventions for res in results]
		interventions = [val for sublist in interventions for val in sublist] # flatten
		adds = set([i for i in interventions if (isinstance(i, mnm_repr.Add), isinstance(i.condition_or_activity, mnm_repr.Activity))])
		adds_act = set([i.condition_or_activity for i in adds]) - set(model.intermediate_activities) # unique additional activities
		max_number_activities = len(model.intermediate_activities) + len(adds_act)
		if max_number_activities < 4:
			return 4
		else:
			return max_number_activities


	def prepare_input_results_models_consistency(self, base_model):
		exped_elements = self.prepare_input_elements()
		exped_deriv_mods, models_results = self.prepare_input_deriv_mods_and_results(base_model)
		exped_term = exporter.export_termination_conds_consistency(base_model) # base_model() and termination conds
		exped_results = exporter.export_relevancy_results_consistency(models_results, base_model) # relevancy info, :- inconsistent()
		output = [exped_elements, exped_deriv_mods, exped_term, exped_results]
		output = [val for sublist in output for val in sublist]
		return output


	def prepare_input_results_models_revision(self, base_model):
		exped_elements = self.prepare_input_elements()
		exped_deriv_mods, models_results = self.prepare_input_deriv_mods_and_results(base_model)
		exped_term = exporter.export_termination_conds_revision(base_model) # base_model() and termination conds
		exped_results = exporter.export_relevancy_results_revision(models_results) # relevancy info, #example not inconsistent()
		output = [exped_elements, exped_deriv_mods, exped_term, exped_results]
		output = [val for sublist in output for val in sublist]
		return output


	def prepare_input_elements(self):
		exped_entities = exporter.export_entities(self.archive.mnm_entities)
		exped_compartments = exporter.export_compartments(self.archive.mnm_compartments)
		exped_activities = exporter.export_activities(self.archive.mnm_activities)
		output = [exped_entities, exped_compartments, exped_activities] # not flattened
		return [val for sublist in output for val in sublist] # flattened


	def prepare_input_deriv_mods_and_results(self, base_model):
		extracted_results = [exp.results for exp in self.archive.known_results] # not flattened
		extracted_results = [val for sublist in extracted_results for val in sublist] # flattened

		exped_results = exporter.export_results(extracted_results)
		models_results = self.make_derivative_models(base_model, extracted_results)
		exped_models = exporter.export_models(models_results) # specification and model()

		out = [exped_results, exped_models] # not flattened
		out = [val for sublist in out for val in sublist] # flattened
		return (out, models_results)


	def write_and_execute_xhail(self, inpt):
		# try: remove the workfile
		with open('./temp/workfile_xhail', 'w') as f:
			for string in inpt:
				read_data = f.write(string)
		# could suppress there warnig messages later on
		output_enc = subprocess.check_output(["java", "-jar", self.xhail, "-g", self.gringo, "-c", self.clasp, "-a", "-f", './temp/workfile_xhail'])
		output_dec = output_enc.decode('utf-8')
		return output_dec


	def process_output_consistency(self, output):
		if "Answers     : 1" in output:
			return True
		else:
			return False


	def make_derivative_models(self, base_model, extracted_results):
		unique_interventions = set([result.exp_description.interventions for result in extracted_results])
		# removes empty set; to avoid making pointless derivative model
		try:
			unique_interventions.remove(frozenset([]))
		except:
			pass
		# create derived models and keep interventions info
		models = {}
		models[frozenset([])] = base_model # adding the base model
		counter = 0
		for interv_set in unique_interventions:
			derived_model = copy(base_model)
			derived_model.apply_interventions(interv_set)
			derived_model.ID = 'deriv_%s_%s' % (base_model.ID, counter)
			models[interv_set] = derived_model
			counter += 1
		# group results acc to interventions
		grouped_results = {}
		for interv_set in models.keys():
			results_group = []
			for result in extracted_results:
				if interv_set == result.exp_description.interventions:
					results_group.append(result)
				else:
					pass
			grouped_results[interv_set] = results_group
		# model:results association (based on interventions)
		models_results = {} # model:relevant_results
		for interv_set in models.keys():
			models_results[models[interv_set]] = grouped_results[interv_set]

		return models_results


class RevC(RevisionModule): # minimise changes
	def __init__(self, archive):
		RevisionModule.__init__(self, archive)

#	def test_and_revise_all(self):
#		inconsistent_models = []
#		for model in self.archive.working_models:
#			if not self.check_consistency(model):
#				inconsistent_models.append(model)
#			else:
#				pass
#
#		for model in inconsistent_models:
#			self.revise(model)



	def revise(self, base_model):
		res_mods = self.prepare_input_results_models_revision(base_model)

		modeh_add_act = exporter.export_add_activities(set(self.archive.mnm_activities) - set(base_model.intermediate_activities))
		modeh_rem_act = exporter.export_remove_activities(base_model.intermediate_activities)
		interventions_rules = exporter.interventions_rules()

		difference_facts = exporter.export_force_new_model(base_model, set(self.archive.working_models) - set([base_model]))
		model_difference_rules = exporter.model_difference_rules()

		max_number_activities = self.calculate_max_number_activities(base_model)
		mod_rules = exporter.models_rules(max_number_activities)
		pred_rules = exporter.predictions_rules()
		incons_rules = exporter.inconsistency_rules()

		inpt = [res_mods, modeh_add_act, modeh_rem_act, interventions_rules, difference_facts, model_difference_rules, mod_rules, pred_rules, incons_rules]
		inpt = [val for sublist in inpt for val in sublist] # flatten

		raw_output = self.write_and_execute_xhail(inpt)
		outcome = self.process_output_revision(raw_output)

#		print('\n\n\n')
#		print(raw_output)
#		print('\n\n\n')
	
#		return outcome

	def process_output_revision(self, raw_output):
		# not inconsistent(%%%,%%%)
		# remove(%%%)
		# add(%%%)

class RevCI(RevisionModule): # minimise changes and ignored
	def __init__(self, archive, quality_module):
		RevisionModule.__init__(self, archive)
		self.quality_module = quality_module

#	def test_and_revise_all(self):
#		inconsistent_models = []
#		for model in self.archive.working_models:
#			if not self.check_consistency(model):
#				inconsistent_models.append(model)
#			else:
#				pass
#
#		for model in inconsistent_models:
#			self.revise(model)
#
#		for model in self.archive.working_models:
#			self.update_quality(model)


#	def check_consistency(self, model):
		# prepare input consistency
		# return: T/F

#	def revise(self, model):

#	def update_quality(self):



class RevCwI(RevisionModule): # revision minimise changes weighted and ignored
	def __init__(self, archive, quality_module):
		RevisionModule.__init__(self, archive)
		self.quality_module = quality_module

#	def test_and_revise_all(self):
#		inconsistent_models = []
#		for model in self.archive.working_models:
#			if not self.check_consistency(model):
#				inconsistent_models.append(model)
#			else:
#				pass
#
#		for model in inconsistent_models:
#			self.revise(model)
#
#		for model in self.archive.working_models:
#			self.update_quality(model)
#
#	def check_consistency(self, model):
#		# prepare input consistency
#		# return: T/F
#
#	def revise(self, model):
#
#	def update_quality(self):



class RevCIw(RevisionModule): # revision minimise changes and ignored weighted
	def __init__(self, archive, quality_module):
		RevisionModule.__init__(self, archive)
		self.quality_module = quality_module

#	def test_and_revise_all(self):
#		inconsistent_models = []
#		for model in self.archive.working_models:
#			if not self.check_consistency(model):
#				inconsistent_models.append(model)
#			else:
#				pass
#
#		for model in inconsistent_models:
#			self.revise(model)
#
#		for model in self.archive.working_models:
#			self.update_quality(model)
#
#	def check_consistency(self, model):
#		# prepare input consistency
#		# return: T/F
#
#	def revise(self, model):
#
#	def update_quality(self):



class RevCwIw(RevisionModule): # revision minimise changes weighted and ignored weighted
	def __init__(self, archive, quality_module):
		RevisionModule.__init__(self, archive)
		self.quality_module = quality_module

#	def test_and_revise_all(self):
#		inconsistent_models = []
#		for model in self.archive.working_models:
#			if not self.check_consistency(model):
#				inconsistent_models.append(model)
#			else:
#				pass
#
#		for model in inconsistent_models:
#			self.revise(model)
#
#		for model in self.archive.working_models:
#			self.update_quality(model)
#
#	def check_consistency(self, model):
#		# prepare input consistency
#		# return: T/F
#
#	def revise(self, model):
#
#	def update_quality(self):


