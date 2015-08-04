#! /usr/bin/env python3
# I, Robert Rozanski, the copyright holder of this work, release this work into the public domain. This applies worldwide. In some countries this may not be legally possible; if so: I grant anyone the right to use this work for any purpose, without any conditions, unless such conditions are required by law.

from time import time
from random import choice
from sys import stdout

class Archive:
	def __init__(self):
		self.development_history = []
		self.working_models = set([])
		self.known_results = [] # container for Experiment type objects not Result type
		self.chosen_experiment_descriptions = [] # list of expDs
		self.new_result = None # stored here before it's accepted
		self.error_flag = False
		self.revflag = False
		self.all_models_equivalent = False
		self.all_models_equivalent_counter = 0 # counts in row - restarts after succesfull design
		self.mnm_compartments = [] # to keep track of mnm elements; info for exp design
		self.mnm_entities = [] # to keep track of mnm elements
		self.mnm_activities = [] # to keep track of mnm elements; info for revision and exp design
		self.import_activities = []
		self.start_time = time()
		self._results_counter = 0
		self._models_counter = 0
		self.model_of_ref = None


	def record(self, event):
		event.timestamp = time() - self.start_time
		self.development_history.append(event)

		if isinstance(event, ChosenExperiment):
			self.chosen_experiment_descriptions = event.experiment_descriptions
			self.all_models_equivalent_counter = 0

		elif isinstance(event, ExpDesignFail):
			self.error_flag = True

		elif isinstance(event, NewResults):
			self.chosen_experiment_descriptions = [] # clearing 
			event.experiment.ID = self.get_new_exp_id()
			for res in event.experiment.results:
				res.ID = self.get_new_res_id()
			self.new_result = event.experiment
#			self.known_results.append(event.experiment)# doubled accepted results

		elif isinstance(event, AcceptedResults):
			self.new_result = None # clearing 
			self.known_results.append(event.experiment)

		elif isinstance(event, RefutedModels):
			self.working_models = self.working_models - set(event.refuted_models)
#			for model in event.refuted_models:
#				self.working_models.remove(model)

		elif isinstance(event, RevisedModel):
			for model in event.revised_models:
				model.ID = self.get_new_model_id()
# append
			self.working_models = self.working_models | set(event.revised_models)

		elif isinstance(event, RedundantModel):
			pass # not added, so no need to remove

		elif isinstance(event, AllModelsEmpiricallyEquivalent):
			self.all_models_equivalent_counter += 1
			self.all_models_equivalent = True
			max_quality = max([m.quality for m in event.models])
			best_models = [m for m in event.models if m.quality == max_quality]
			chosen_model = choice(best_models)
			self.working_models = set([chosen_model]) # was list, not set
			event.model_left = chosen_model
			print('all models equivalent!')
			stdout.flush()

		elif isinstance(event, RevisionFail):
			self.revflag = True
			self.error_flag = True

		elif isinstance(event, RevisedIgnoredUpdate):
			pass

		elif isinstance(event, CheckPointSuccess):
			pass

		elif isinstance(event, AdditionalModels):
			for model in event.additional_models:
				model.ID = self.get_new_model_id()
#				self.working_models.append(model)
			self.working_models = self.working_models | set(event.additional_models)

		elif isinstance(event, AdditModProdFail):
			self.revflag = True
			self.error_flag = True

		elif isinstance(event, UpdatedModelQuality):
			pass

		elif isinstance(event,  InitialModels):
			for model in event.models:
				model.ID = self.get_new_model_id()
#				self.working_models.append(model)
			self.working_models = self.working_models | set(event.models)

		elif isinstance(event,  InitialResults):
			for exp in event.experiments:
				exp.ID = self.get_new_exp_id()
				for exp in event.experiments:
					for res in exp.results:
						res.ID = self.get_new_res_id()
			self.known_results.extend(event.experiments)

		elif isinstance(event,  CheckPointFail):
			self.error_flag = True

		else:
			raise(TypeError, "Archive: event's type unknown: %s" % type(event))


	def get_model_origin_event(self, model): # number of new results covered
		for event in self.development_history:
			if not (isinstance(event, InitialModels) or isinstance(event, RevisedModel) or isinstance(event, AdditionalModels)):
				continue

			elif (isinstance(event, InitialModels) and (model in event.models)):
				return event

			elif (isinstance(event, RevisedModel) and (model in event.revised_models)):
				return event

			elif (isinstance(event, AdditionalModels) and (model in event.additional_models)):
				return event

			else:
				pass

		# if not found
		raise ValueError("get_model_origin_event: matching event not found; model: %s" % model.ID)


	def get_events_after_event(self, event):
		index = self.development_history.index(event)
		return self.development_history[index+1:]


	def get_results_after_model(self, model):
		event = self.get_model_origin_event(model)
		events_after = self.get_events_after_event(event)
		results_sets = [event.experiment.results for event in events_after if isinstance(event, NewResults)]# doesn't include initial results
		results = []
		for res_set in results_sets:
			results.extend(list(res_set))
		return results


	def get_matching_element(self, element_id, element_version=None):
		for element in self.mnm_activities:
			if element.ID == element_id:
				return element
			else:
				pass
		for element in self.mnm_entities:
			if ((element.ID == element_id) and (element.version == element_version)):
				return element
			else:
				pass
		for element in self.mnm_compartments:
			if element.ID == element_id:
				return element
			else:
				pass
		for element in self.import_activities:
			if element.ID == element_id:
				return element
			else:
				pass
		raise ValueError("get_matching_element: matching element not found: ID: %s" % element_id)


	def get_matching_result(self, res_id):
		for exp in self.known_results:
			for res in exp.results:
				if res.ID == res_id:
					return res
				else:
					pass
		raise ValueError("get_matching_result: matching element not found: ID: %s" % res_id)


	def get_new_model_id(self):
		ID = 'm_%s' % self._models_counter
		self._models_counter += 1
		return ID

	def get_new_exp_id(self):
		return 'exp_%s' % len(self.known_results)

	def get_new_res_id(self):
		ID = 'res_%s' % self._results_counter
		self._results_counter += 1
		return ID

	def get_new_ent_id(self):
		return 'ent_%s' % len(self.mnm_entities)

	def get_new_act_id(self):
		return 'act_%s' % len(self.mnm_activities + self.import_activities)


class Event:
	def __init__(self):
		self.timestamp = None

class InitialModels(Event): # record them after initial results!
	def __init__(self, models):
		Event.__init__(self)
		self.models = models


class InitialResults(Event): # record them first! # full experiments!
	def __init__(self, exps):
		Event.__init__(self)
		self.experiments = exps

class ChosenExperiment(Event): # experiment descriptions
	def __init__(self, expDs):
		Event.__init__(self)
		self.experiment_descriptions = expDs

class NewResults(Event): # full experiment with results
	def __init__(self, exp):
		Event.__init__(self)
		self.experiment = exp

class AcceptedResults(Event):
	def __init__(self, exp):
		Event.__init__(self)
		self.experiment = exp

class RefutedModels(Event):
	def __init__(self, models):
		Event.__init__(self)
		self.refuted_models = frozenset(models)

class RevisedModel(Event):
	def __init__(self, old_model, revised_models):
		Event.__init__(self)
		self.old_model = old_model
		self.revised_models = frozenset(revised_models)

class UpdatedModelQuality(Event):
	def __init__(self, model, new_quality):
		Event.__init__(self)
		self.model = model
		self.new_quality = new_quality

class AdditionalModels(Event):
	def __init__(self, models):
		Event.__init__(self)
		self.additional_models = frozenset(models)

class RevisionFail(Event):
	def __init__(self):
		pass

class AdditModProdFail(Event):
	def __init__(self):
		pass

class ExpDesignFail(Event):
	def __init__(self):
		pass

class CheckPointFail(Event):
	def __init__(self, criterion):
		self.criterion = criterion

class CheckPointSuccess(Event):
	def __init__(self):
		pass

class RevisedIgnoredUpdate(Event):
	def __init__(self, model):
		self.model = model

class RedundantModel(Event):
	def __init__(self, base_model, model):
		self.base_model = base_model
		self.model = model

class AllModelsEmpiricallyEquivalent(Event):
	def __init__(self, models):
		self.models = list(models)
		self.model_left = None
