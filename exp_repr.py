#! /usr/bin/env python3

class ExperimentType:
	def __init__(self):
		self.base_cost = None


class InVitro(ExperimentType):
	def __init__(self):
		ExperimentType.__init__(self)

class InVivo(ExperimentType):
	def __init__(self):
		ExperimentType.__init__(self)


class ReconstructionActivity(InVitro):
	def __init__(self, activity):
		InVitro.__init__(self)
		self.activity = activity

class ReconstructionEnzReaction(InVitro):
	def __init__(self, reaction, enzyme):
		InVitro.__init__(self)
		self.reaction = reaction
		self.enzyme = enzyme

class ReconstructionTransporterRequired(InVitro):
	def __init__(self, transport_activity, transporter):
		InVitro.__init__(self)
		self.transport_activity = transport_activity
		self.transporter = transporter


class DetectionActivity(InVivo):
	def __init__(self, activity):
		InVivo.__init__(self)
		self.activity = activity

class DetectionEntity(InVivo):
	def __init__(self, entity):
		InVivo.__init__(self)
		self.entity = entity

class LocalisationEntity(InVivo):
	def __init__(self, entity):
		InVivo.__init__(self)
		self.entity = entity



class ExperimentDescription:
	def __init__(self, exp_type, interventions=[]):
		self.experiment_type = exp_type
		self.interventions = set(interventions)
		self.status = 'Active'

class Result:
	def __init__(self, exp_description, outcome):
		self.exp_description = exp_description
		self.outcome = outcome

class Experiment:
	def __init__(self, ID, results=[]):
		self.ID = ID
		self.results = set(results)
