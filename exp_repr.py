#! /usr/bin/env python3

class ExperimentType:
	def __init__(self):
		pass

class DetectionEntity(ExperimentType):
	def __init__(self, entity_id):
		ExperimentType.__init__(self)
		self.entity_id = entity_id
		self.cost = None

class LocalisationEntity(ExperimentType):
	def __init__(self, entity_id):
		ExperimentType.__init__(self)
		self.entity_id = entity_id
		self.cost = None

class DetectionActivity(ExperimentType):
	def __init__(self, activity_id):
		ExperimentType.__init__(self)
		self.activity_id = activity_id
		self.cost = None

class AdamTwoFactorExperiment(ExperimentType):
	def __init__(self, gene_id, metabolite_id):
		ExperimentType.__init__(self)
		self.gene_id = gene_id
		self.metabolite_id = metabolite_id
		self.cost = None

class ReconstructionActivity(ExperimentType):
	def __init__(self, activity_id):
		ExperimentType.__init__(self)
		self.activity_id = activity_id
		self.cost = None

class ReconstructionEnzReaction(ExperimentType):
	def __init__(self, reaction_id, enzyme_id):
		ExperimentType.__init__(self)
		self.reaction_id = reaction_id
		self.enzyme_id = enzyme_id
		self.cost = None

class ReconstructionTransporterRequired(ExperimentType):
	def __init__(self, transport_activity_id, transporter_id):
		ExperimentType.__init__(self)
		self.transport_activity_id = transport_activity_id
		self.transporter_id = transporter_id
		self.cost = None



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
