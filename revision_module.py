#! /usr/bin/env python3
# I, Robert Rozanski, the copyright holder of this work, release this work into the public domain. This applies worldwide. In some countries this may not be legally possible; if so: I grant anyone the right to use this work for any purpose, without any conditions, unless such conditions are required by law.

import exporter

from archive import RefutedModels, RevisedModel, RevisionFail, AdditionalModels, AdditModProdFail, RevisedIgnoredUpdate, RedundantModel
import archive
from copy import copy
import subprocess
import mnm_repr
import re
import random
from time import gmtime

class RevisionModule:
	def __init__(self, archive, xhail="/usr/local/xhail-0.5.1/xhail.jar", gringo="/usr/local/xhail-0.5.1/gringo", clasp="/usr/local/xhail-0.5.1/clasp", sfx=""):
		self.archive = archive
		self.xhail = xhail
		self.gringo = gringo
		self.clasp = clasp
		# adds suffix specific for the task (required for multiprocessing)
		self.work_file = './temp/workfile_xhail_%s' % sfx


	def test_and_revise_all(self):
		inconsistent_models = []
		for model in self.archive.working_models:
			if not self.check_consistency(model):
				inconsistent_models.append(model)
			else:
				pass

		revision_events = []
		update_events = []
		updated_ignoring_models = []
		redundant_model_created_events = []
		for model in inconsistent_models:
			#(new_mods, updated_base_model)
			out = self.revise(model)
			# in this case: there is no other consistent model
			if out == False:
				self.archive.record(RevisionFail())
				break
			else:
				if (out[0] != []): # new_mods
					# check if new model redundant:
					activities_from_current_models = [mod.intermediate_activities for mod in self.archive.working_models]
					non_redundant_new_models = []
					for new_model in out[0]:
						# is redundant (set of activities identical to some other model)
						if new_model.intermediate_activities in activities_from_current_models:
							redundant_model_created_events.append(RedundantModel(model, new_model))
						else: # is not redundant
							non_redundant_new_models.append(new_model)
					revision_events.append(RevisedModel(model, non_redundant_new_models))

				if (out[1] == True): # updated_base_model
					update_events.append(RevisedIgnoredUpdate(model))
					updated_ignoring_models.append(model)

		# record refuted
		# (revision required change in model's structure, not just in set of ignored results)
		self.archive.record(RefutedModels(list(set(inconsistent_models) - set(updated_ignoring_models))))
		# record revision/update events
		for event in revision_events + update_events + redundant_model_created_events:
			self.archive.record(event)


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
		max_number_activities = len(self.archive.mnm_activities)
		if max_number_activities < 4:
			return 4
		else:
			return max_number_activities


	def prepare_input_results_models_consistency(self, base_model):
		exped_elements = self.prepare_input_elements()
		exped_deriv_mods, models_results = self.prepare_input_deriv_mods_and_results(base_model)
		# base_model() and termination conds
		exped_term = exporter.export_termination_conds_consistency(base_model)
		# relevancy info, :- inconsistent()
		exped_results = exporter.export_relevancy_results_consistency(models_results, base_model)
		output = [exped_elements, exped_deriv_mods, exped_term, exped_results]
		output = [val for sublist in output for val in sublist]
		return output


	def prepare_input_results_models_revision(self, base_model):
		exped_elements = self.prepare_input_elements()
		exped_deriv_mods, models_results = self.prepare_input_deriv_mods_and_results(base_model)
		# base_model() and termination conds
		exped_term = exporter.export_termination_conds_revision(base_model)
		# relevancy info, #example not inconsistent()
		exped_results = exporter.export_relevancy_results_revision(models_results)
		output = [exped_elements, exped_deriv_mods, exped_term, exped_results]
		output = [val for sublist in output for val in sublist]
		return output


	def prepare_input_elements(self):
		exped_entities = exporter.export_entities(self.archive.mnm_entities)
		exped_compartments = exporter.export_compartments(self.archive.mnm_compartments)
		exped_activities = exporter.export_activities(self.archive.mnm_activities + self.archive.import_activities)
		# not flattened
		output = [exped_entities, exped_compartments, exped_activities]
		# flattened
		return [val for sublist in output for val in sublist]


	def prepare_input_deriv_mods_and_results(self, base_model):
		# not flattened
		extracted_results = [exp.results for exp in self.archive.known_results]
		# flattened
		extracted_results = [val for sublist in extracted_results for val in sublist]

		exped_results = exporter.export_results(extracted_results)
		models_results = self.make_derivative_models(base_model, extracted_results)
		# specification and model()
		exped_models = exporter.export_models(models_results)

		# not flattened
		out = [exped_results, exped_models]
		# flattened
		out = [val for sublist in out for val in sublist]
		return (out, models_results)


	def write_and_execute_xhail(self, inpt):
		# try: remove the workfile
		with open(self.work_file, 'w') as f:
			for string in inpt:
				read_data = f.write(string)
		# could suppress there warnig messages later on
		output_enc = subprocess.check_output(["java", "-jar", self.xhail, "-g", self.gringo, "-c", self.clasp, "-a", "-f", self.work_file])
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
		# adding the base model
		models[frozenset([])] = base_model
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


	def create_revised_models(self, base_model, solution):
		interv_add = [mnm_repr.Add(self.archive.get_matching_element(e_id)) for e_id in solution[0]]
		interv_rem = [mnm_repr.Remove(self.archive.get_matching_element(e_id)) for e_id in solution[1]]
		covered_res = [self.archive.get_matching_result(res_id) for res_id in solution[2]]
		ignored_res = [self.archive.get_matching_result(res_id) for res_id in solution[3]]

		new_model = copy(base_model)
		new_model.apply_interventions(interv_rem)
		new_model.apply_interventions(interv_add)
		new_model.results_covered = frozenset(covered_res)
		new_model.ignored_results = frozenset(ignored_res)

		return new_model


	def process_output_revision(self, raw_output):
		pat_answer = re.compile('Answer.*?\n\n\x1b', re.DOTALL)
		answers = pat_answer.findall(raw_output)

		pat_add = re.compile('add\(.*?\)')
		pat_remove = re.compile('remove\(.*?\)')
		pat_not_incon = re.compile('not inconsistent\(.*?\)')
		pat_ignored = re.compile('ignored\(.*?\)')
		output = []
		counter = 0
		for ans in answers:
			added = set(pat_add.findall(ans))
			# using split not strip; strip matchech chars not string: overzelous
			added = [ad.split('add(')[1] for ad in added]
			# formatting: leaving only id
			added = [ad.strip(')') for ad in added]

			removed = set(pat_remove.findall(ans))
			# using split not strip; strip matchech chars not string: overzelous
			removed = [rem.split('remove(')[1] for rem in removed]
			removed = [rem.strip(')') for rem in removed]

			covered = set(pat_not_incon.findall(ans))
			# using split not strip; strip matchech chars not string: overzelous
			covered = [cov.split('not inconsistent(')[1] for cov in covered]
			covered = [cov.strip(')') for cov in covered]
			# removing first argument
			covered = [cov.split(',')[1] for cov in covered]

			ignored = set(pat_ignored.findall(ans))
			# using split not strip; strip matchech chars not string: overzelous
			ignored = [ign.split('ignored(')[1] for ign in ignored]
			ignored = [ign.strip(')') for ign in ignored]

			counter += 1
			output.append((added, removed, covered, ignored))

		return output


	def get_current_best_model(self):
		# one of them at least
		max_quality = max([m.quality for m in self.archive.working_models])
		model = random.choice([m for m in self.archive.working_models if (m.quality == max_quality)])
		return copy(model)

	def create_random_model(self):
		# presence of two versions of the same entity will trigger revision anyway
		numberActToChoose = random.choice(list(range(len(self.archive.mnm_activities))))
		activities = random.sample(self.archive.mnm_activities, numberActToChoose)
		# will cause problems if there will be no working models left...
		new_model = copy(list(self.archive.working_models)[0])
		new_model.intermediate_activities = frozenset(activities)
		new_model.ID = 'random_base'
		return new_model


	def prepare_input_execute_and_process(self, base_model, ignoring, force_new_model):
		# pretty much revise; base_model = original one
		cmodel = copy(base_model)
		cmodel.ID = 'base'

		res_mods = self.prepare_input_results_models_revision(cmodel)

		add_act = set([x for x in self.archive.mnm_activities if (x.add_cost != None)]) - set(cmodel.intermediate_activities)
		rem_act = set([x for x in cmodel.intermediate_activities if (x.remove_cost != None)])
		modeh_add_act = exporter.export_add_activities(add_act)
		modeh_rem_act = exporter.export_remove_activities(rem_act)

		modeh_ignore = []
		if ignoring:
			results = [exp.results for exp in self.archive.known_results]
			results = [val for sublist in results for val in sublist] # flatten
			modeh_ignore = exporter.export_ignore_results(results)

		inter_rules = exporter.interventions_rules()

		difference_facts = []
		model_difference_rules = []
		if force_new_model:
			# base model (id) must not be in the working mods
			difference_facts = exporter.export_force_new_model(cmodel, self.archive.working_models)
			model_difference_rules = exporter.model_difference_rules()

		max_number_activities = len(self.archive.mnm_activities + self.archive.import_activities)
		mod_rules = exporter.models_rules(max_number_activities)
		pred_rules = exporter.predictions_rules()
		incons_rules = exporter.inconsistency_rules()

		inpt = [res_mods, modeh_add_act, modeh_rem_act, modeh_ignore, inter_rules, difference_facts, model_difference_rules, mod_rules, pred_rules, incons_rules]
		inpt = [val for sublist in inpt for val in sublist] # flatten

		raw_output = self.write_and_execute_xhail(inpt)

		processed_output = self.process_output_revision(raw_output)
		# decide what to do based on output
		# revision fail
		if processed_output == []:
			return False

		new_mod = []
		updated_base_model = False
		solutions_for_model_revision = [solution for solution in processed_output if ((solution[0] != []) or (solution[1] != []))]
		solution_for_ignoring_update = [solution for solution in processed_output if ((solution[0] == []) and (solution[1] == []))]

		# random choice used to limit # of new models to 1:
		# more than that would blow up experiment design!
		if (solutions_for_model_revision != []):
			new_mod = [random.choice([self.create_revised_models(cmodel, solution) for solution in solutions_for_model_revision])]

		# update of ignoring results
		# (pick one randomly, they're all optimal)
		elif (solution_for_ignoring_update != []):
			self.update_base_model(base_model, random.choice(solution_for_ignoring_update))
			updated_base_model = True

		else:
			raise ValueError("no solutions for revisions and ignoring: revision failed")

		return (new_mod, updated_base_model)


	def update_base_model(self, base_model, solution):
		covered_res = [self.archive.get_matching_result(res_id) for res_id in solution[2]]
		ignored_res = [self.archive.get_matching_result(res_id) for res_id in solution[3]]
		base_model.update_ignored_results(ignored_res)
		base_model.update_covered_results(covered_res)


class RevCAddB(RevisionModule):
	# rev: minimise changes; additional: revise the best
	def __init__(self, archive, sfx=""):
		RevisionModule.__init__(self, archive, sfx=sfx)

	def revise(self, base_model, force_new_model=False):
		return self.prepare_input_execute_and_process(base_model, False, force_new_model)

	def produce_additional_models(self):
		model = self.get_current_best_model()
		out = self.revise(model, True)
		if out == False:
			self.archive.record(AdditModProdFail())
		else:
			self.archive.record(AdditionalModels(out[0]))

		if out[1] == True:
			raise ValueError('produce_additional_models: revised set of ignored results instead of model itself')


class RevCAddR(RevisionModule):
	# rev: minimise changes; additional: random
	def __init__(self, archive, sfx=""):
		RevisionModule.__init__(self, archive, sfx=sfx)

	def revise(self, base_model, force_new_model=False):
		return self.prepare_input_execute_and_process(base_model, False, force_new_model)

	def produce_additional_models(self):
		model = self.create_random_model()
		if not self.check_consistency(model):
			out = self.revise(model)
			if out == False:
				self.archive.record(AdditModProdFail())
			else:
				self.archive.record(AdditionalModels(out[0]))
		else:
			self.archive.record(AdditionalModels([model]))

		if out[1] == True:
			raise ValueError('produce_additional_models: revised set of ignored results instead of model itself')


class RevCIAddB(RevisionModule):
	# rev: minimise changes and ignored; additional: revise the best
	def __init__(self, archive, sfx=""):
		RevisionModule.__init__(self, archive, sfx=sfx)

	def revise(self, base_model, force_new_model=False):
		return self.prepare_input_execute_and_process(base_model, True, force_new_model)

	def produce_additional_models(self):
		model = self.get_current_best_model()
		out = self.revise(model, True)
		if out == False:
			self.archive.record(AdditModProdFail())
			return
		else:
			self.archive.record(AdditionalModels(out[0]))
			return

		if out[1] == True:
			raise ValueError('produce_additional_models: revised set of ignored results instead of model itself')


class RevCIAddR(RevisionModule):
	# rev: minimise changes and ignored; additional: random
	def __init__(self, archive, sfx=""):
		RevisionModule.__init__(self, archive, sfx=sfx)

	def revise(self, base_model, force_new_model=False):
		return self.prepare_input_execute_and_process(base_model, True, force_new_model)

	def produce_additional_models(self):
		model = self.create_random_model()
		if not self.check_consistency(model):
			out = self.revise(model, True)
			if out == False:
				self.archive.record(AdditModProdFail())
				return
			else:
				self.archive.record(AdditionalModels(out[0]))
				return
		else:
			self.archive.record(AdditionalModels([model]))
			return

		if out[1] == True:
			raise ValueError('produce_additional_models: revised set of ignored results instead of model itself')
