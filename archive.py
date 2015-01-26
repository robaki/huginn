#! /usr/bin/env python3

from time import time

class Archive:
	def __init__(self):
		self.development_history = []
		self.working_models = []
		self.known_results = []
		self.mnm_compartments = [] # to keep track of mnm elements; info for exp design
		self.mnm_entities = [] # to keep track of mnm elements
		self.mnm_activities = [] # to keep track of mnm elements; info for revision and exp design
		self.allowed_exp_types = [] # info for exp design
		self.start_time = time()


	def record(self, event):
		event.timestamp = time() - self.start_time
		self.development_history.append(event)

		if isinstance(event, ChosenExperiment):
			pass

		elif isinstance(event, Results):
			self.known_results.append(event.experiment)

		elif isinstance(event, RefutedModels):
			for model in event.refuted_models:
				self.working_models.remove(model)

		elif isinstance(event, RevisedModel):
			for model in event.revised_models:
				self.working_models.append(model)

		elif isinstance(event, AdditionalModels):
			for model in event.additional_models:
				self.working_models.append(model)

		elif isinstance(event, ChangedModelQuality):
			pass

		else:
			raise(TypeError, "Archive: event's type unknown: %s" % type(event))


	def get_model_origin_event(self, model): # number of new results covered
		for event in self.archive:
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
		results_sets = [event.experiment.results for event in events_after if isinstance(event, Results)]
		results = []
		for res_set in results_sets:
			results.extend(list(res_set))
		return results


class Event:
	def __init__(self):
		self.timestamp = None

class InitialModels(Event):
	def __init__(self, models):
		Event.__init__(self)
		self.models = models
		self.timestamp = 0

class InitialResults(Event):
	def __init__(self, exp):
		Event.__init__(self)
		self.experiment = exp
		self.timestamp = 0

class ChosenExperiment(Event): # experiment description
	def __init__(self, exp):
		Event.__init__(self)
		self.experiment_description = exp

class Results(Event): # full experiment with results
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
