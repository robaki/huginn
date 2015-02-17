#! /usr/bin/env python3

import exporter

from archive import RefutedModels
from archive import RevisedModel
from archive import RevisionFail
from archive import AdditionalModels
from archive import AdditModProdFail
import archive
from copy import copy
import subprocess
import mnm_repr
import re
import random

class RevisionModule:
	def __init__(self, archive, xhail="/usr/local/xhail-0.5.1/xhail.jar", gringo="/usr/local/xhail-0.5.1/gringo", clasp="/usr/local/xhail-0.5.1/clasp"):
		self.archive = archive
		self.xhail = xhail
		self.gringo = gringo
		self.clasp = clasp


	def test_and_revise_all(self):
		inconsistent_models = []
		for model in self.archive.working_models:
			if not self.check_consistency(model):
				inconsistent_models.append(model)
			else:
				pass

		self.archive.record(RefutedModels(inconsistent_models))

		revision_results = {}
		for model in inconsistent_models:
			cmodel = copy(model)
			cmodel.ID = 'base'
			out = self.revise(cmodel)
			if out == False: # in this case: there is no consistent model
				self.archive.record(RevisionFail())
#				return False # so revision is futile; no need check other models
			else:
				self.archive.record(RevisedModel(out[1][0], out[1][1]))
#				revision_results.update(out[1])
#		return revision_results



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


	def create_models_and_register(self, base_model, processed_output):
		models = []
		for solution in processed_output.keys():
			interv_add = [mnm_repr.Add(self.archive.get_matching_element(e_id)) for e_id in processed_output[solution][0]]
			interv_rem = [mnm_repr.Remove(self.archive.get_matching_element(e_id)) for e_id in processed_output[solution][1]]
			covered_res = [self.archive.get_matching_result(res_id) for res_id in processed_output[solution][2]]
			ignored_res = [self.archive.get_matching_result(res_id) for res_id in processed_output[solution][3]]

			new_model = copy(base_model)
			new_model.apply_interventions(interv_rem)
			new_model.apply_interventions(interv_add)
			new_model.results_covered = frozenset(covered_res)
			new_model.ignored_results = frozenset(ignored_res)
			models.append(new_model)

		self.archive.record(archive.RevisedModel(base_model, models))
		return (base_model, models)


	def process_output_revision(self, raw_output):
		pat_answer = re.compile('Answer.*?\n\n\x1b', re.DOTALL)
		answers = pat_answer.findall(raw_output)

		pat_add = re.compile('add\(.*?\)')
		pat_remove = re.compile('remove\(.*?\)')
		pat_not_incon = re.compile('not inconsistent\(.*?\)')
		pat_ignored = re.compile('ignored\(.*?\)')
		output = {}
		counter = 0
		for ans in answers:
			added = set(pat_add.findall(raw_output))
			added = [ad.strip('add(') for ad in added] # formatting: leaving only id
			added = [ad.strip(')') for ad in added] # formatting: leaving only id
			removed = set(pat_remove.findall(raw_output))
			removed = [rem.strip('remove(') for rem in removed]
			removed = [rem.strip(')') for rem in removed]
			covered = set(pat_not_incon.findall(raw_output))
			covered = [cov.strip('not inconsistent(') for cov in covered]
			covered = [cov.strip(')') for cov in covered]
			covered = [cov.split(',')[1] for cov in covered] # removing first argument
			ignored = set(pat_ignored.findall(raw_output))
			ignored = [ign.split('ignored(')[1] for ign in ignored] # using split not strip; strip matchech chars not string: overzelous
			ignored = [ign.strip(')') for ign in ignored]
			counter += 1
			output[counter] = (added, removed, covered, ignored)

		return output


	def get_current_best_model(self): # one of them at least
		max_quality = max([m.quality for m in self.archive.working_models])
		return random.choice([m for m in self.archive.working_models if (m.quality == max_quality)])


	def create_random_model(self):
		numberActToChoose = random.choice(list(range(len(self.archive.mnm_activities)))) # presence of two versions of the same entity will trigger revision anyway
		activities = [random.sample(self.archive.mnm_activities), numberActToChoose]
		new_model = copy(self.archive.working_models[0]) # will cause problems if there will be no working models left...
		new_model.intermediate_activities = activities
		return new_model


	def prepare_input_execute_and_process(self, base_model, ignoring, force_new_model): # pretty much revise
		res_mods = self.prepare_input_results_models_revision(base_model)

		add_act = set([x for x in self.archive.mnm_activities if (x.add_cost != None)]) - set(base_model.intermediate_activities)
		rem_act = set([x for x in base_model.intermediate_activities if (x.remove_cost != None)])
		modeh_add_act = exporter.export_add_activities(add_act)
		modeh_rem_act = exporter.export_remove_activities(rem_act)

		modeh_ignore = []
		if ignore:
			results = [exp.results for exp in self.archive.known_results]
			results = [val for sublist in results for val in sublist] # flatten
			modeh_ignore = exporter.export_ignore_results(results)# added ignoring!!!

		interventions_rules = exporter.interventions_rules()

		difference_facts = []
		model_difference_rules = []
		if force_new_model:
			difference_facts = exporter.export_force_new_model(base_model, self.archive.working_models)# base model (id) must not be in the working mods
			model_difference_rules = exporter.model_difference_rules()

		max_number_activities = self.calculate_max_number_activities(base_model)
		mod_rules = exporter.models_rules(max_number_activities)
		pred_rules = exporter.predictions_rules()
		incons_rules = exporter.inconsistency_rules()

		inpt = [res_mods, modeh_add_act, modeh_rem_act, modeh_ignore, inter_rules, difference_facts, model_difference_rules, mod_rules, pred_rules, incons_rules]
		inpt = [val for sublist in inpt for val in sublist] # flatten

		raw_output = self.write_and_execute_xhail(inpt)
		processed_output = self.process_output_revision(raw_output)
		if processed_output == {}:
			return False
		else:
			b_mod, new_mods = self.create_models_and_register(base_model, processed_output)
			return (True, (b_mod, new_mods))



class RevCAddB(RevisionModule): # rev: minimise changes; additional: revise the best
	def __init__(self, archive):
		RevisionModule.__init__(self, archive)

	def revise(self, base_model, force_new_model=False):
		return self.prepare_input_execute_and_process(False, base_model, force_new_model)

	def produce_additional_models(self):
		model = self.get_current_best_model()
		out = self.revise(model, True)
		if out == False:
			self.archive.record(AdditModProdFail())
		else:
			self.archive.record(AdditionalModels(out[1][1]))


class RevCAddR(RevisionModule): # rev: minimise changes; additional: random
	def __init__(self, archive):
		RevisionModule.__init__(self, archive)

	def revise(self, base_model, force_new_model=False):
		return self.prepare_input_execute_and_process(False, base_model, force_new_model)

	def produce_additional_models(self):
		model = self.create_random_model()
		if not self.check_consistency(model):
			out = self.revise(model)
			if out == False:
				self.archive.record(AdditModProdFail())
			else:
				self.archive.record(AdditionalModels(out[1][1]))
		else:
			self.archive.record(AdditionalModels([model]))


class RevCIAddB(RevisionModule): # rev: minimise changes and ignored; additional: revise the best
	def __init__(self, archive):
		RevisionModule.__init__(self, archive)

	def revise(self, base_model, force_new_model=False):
		return self.prepare_input_execute_and_process(True, base_model, force_new_model)

	def produce_additional_models(self):
		model = self.get_current_best_model()
		out = self.revise(model, True)
		if out == False:
			self.archive.record(AdditModProdFail())
		else:
			self.archive.record(AdditionalModels(out[1][1]))


class RevCIAddR(RevisionModule): # rev: minimise changes and ignored; additional: random
	def __init__(self, archive):
		RevisionModule.__init__(self, archive)

	def revise(self, base_model, force_new_model=False):
		return self.prepare_input_execute_and_process(True, base_model, force_new_model)

	def produce_additional_models(self):
		model = self.create_random_model()
		if not self.check_consistency(model):
			out = self.revise(model)
			if out == False:
				self.archive.record(AdditModProdFail())
			else:
				self.archive.record(AdditionalModels(out[1][1]))
		else:
			self.archive.record(AdditionalModels([model]))
