#! /usr/bin/env python3

import exporter

from archive import RefutedModels
from archive import RevisedModel

class RevisionModule:
	def __init__(self, archive):
		self.archive = archive

	def check_consistency(self, model):
		res_mods = self.prepare_input_results_models(model)
		mod_rules = models_rules()
		pred_rules = predictions_rules()
		incons_rules = inconsistency_rules()
		all_info = [res_mods, mod_rules, pred_rules, incons_rules]
		inpt = []
		[inpt.extend(x) for x in all_info]
		raw_output = write_and_execute_xhail(inpt)
#		outcome = process_output_consistency(raw_output)	
#		return outcome


	def prepare_input_results_models(self, base_model):
		exped_entities = exporter.export_entities(self.archive.mnm_entities)
		exped_compartments = exporter.export_compartments(self.archive.mnm_compartments)
		exped_activities = exporter.export_activities(self.archive.mnm_activities)
		extracted_results = []
		for exp in self.archive.known_results:
			extracted_results.extend(exp.results)
		exped_results = exporter.export_results(extracted_results)
		models_results = self.make_derivative_models(base_model, extracted_results)
		exped_models = exporter.export_models(models_results) # specification and model()
		exped_term = exporter.export_termination_conds(base_model) # base_model() and termination conds
		exped_results = exporter.export_relevancy_results(models_results, base_model) # relevancy info, #example not inconsistent()
		all_info = [exped_entities, exped_compartments, exped_activities, exped_results, exped_models, exped_term, exped_results]
		output = []
		[output.extend(x) for x in all_info] # flattening all_info; strings put into output
		return output


#	def process_output_consistency(self, output):
#		# is there a model or not


	def write_and_execute_xhail(self, inpt):
		with open('/tmp/workfile', 'w') as f:
			for string in inpt:
				read_data = f.write(string)


	def make_derivative_models(self, base_model, extracted_results):
		unique_interventions = set([result.exp_description.interventions for result in extracted_results])
		unique_interventions.add(frozenset([]))
		# group results acc to interventions
		grouped_results = {}
		for interv_set in unique_interventions:
			results_group = []
			for result in extracted_results:
				if interv_set == result.exp_description.interventions:
					results_group.append(result)
				else:
					pass
			grouped_results[interv_set] = results_group
		# create derived models and keep interventions info
		models = {}
		counter = 0
		for interv_set in unique_interventions:
			derived_model = copy(base_model).apply_interventions(interv_set)
			derived_model.ID = 'deriv_%s_%s' % (base_model.ID, counter)
			models[interv_set] = derived_model
			counter += 1
		# model:results association (based on interventions)
		models_results = {} # model:relevant_results
		for interv_set in unique_interventions:
			models_results[models[interv_set]] = [grouped_results[interv_set]]

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


		# prepare input, execute, 
		# return: T/F

#	def revise(self, model):



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


