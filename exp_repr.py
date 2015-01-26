#! /usr/bin/env python3

class ExperimentType:
	def __init__(self):
		self.cost = None
		self.ignoring_penalty = None

class DetectionEntity(ExperimentType):
	def __init__(self, entity_id):
		ExperimentType.__init__(self)
		self.entity_id = entity_id

class LocalisationEntity(ExperimentType):
	def __init__(self, entity_id):
		ExperimentType.__init__(self)
		self.entity_id = entity_id

class DetectionActivity(ExperimentType):
	def __init__(self, activity_id):
		ExperimentType.__init__(self)
		self.activity_id = activity_id

class AdamTwoFactorExperiment(ExperimentType):
	def __init__(self, gene_id, metabolite_id):
		ExperimentType.__init__(self)
		self.gene_id = gene_id
		self.metabolite_id = metabolite_id

class ReconstructionActivity(ExperimentType):
	def __init__(self, activity_id):
		ExperimentType.__init__(self)
		self.activity_id = activity_id

class ReconstructionEnzReaction(ExperimentType):
	def __init__(self, reaction_id, enzyme_id):
		ExperimentType.__init__(self)
		self.reaction_id = reaction_id
		self.enzyme_id = enzyme_id

class ReconstructionTransporterRequired(ExperimentType):
	def __init__(self, transport_activity_id, transporter_id):
		ExperimentType.__init__(self)
		self.transport_activity_id = transport_activity_id
		self.transporter_id = transporter_id




class ExperimentDescription:
	def __init__(self, exp_type, interventions=[]):
		self.experiment_type = exp_type
		self.interventions = frozenset(interventions)
		self.status = 'Active'

class Result:
	def __init__(self, exp_description, outcome):
		self.exp_description = exp_description
		self.outcome = outcome # True or False

class Experiment:
	def __init__(self, ID, results=[]):
		self.ID = ID
		self.results = frozenset(results)
