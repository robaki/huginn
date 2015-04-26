#! /usr/bin/env python3
# I, Robert Rozanski, the copyright holder of this work, release this work into the public domain. This applies worldwide. In some countries this may not be legally possible; if so: I grant anyone the right to use this work for any purpose, without any conditions, unless such conditions are required by law.

class ExperimentType:
	def __init__(self):
		self.ignoring_penalty = 1
		self.covering_reward = 1
		self.cost = 1

class DetectionEntity(ExperimentType):
	def __init__(self, entity_id):
		ExperimentType.__init__(self)
		self.entity_id = entity_id

	def __hash__(self):
		return hash(self.entity_id)

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))

class LocalisationEntity(ExperimentType):
	def __init__(self, entity_id, comp_id):
		ExperimentType.__init__(self)
		self.entity_id = entity_id
		self.compartment_id = comp_id

	def __hash__(self):
		return hash((self.entity_id, self.compartment_id))

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))

class DetectionActivity(ExperimentType):
	def __init__(self, activity_id):
		ExperimentType.__init__(self)
		self.activity_id = activity_id

	def __hash__(self):
		return hash(self.activity_id)

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))

class AdamTwoFactorExperiment(ExperimentType):
	def __init__(self, gene_id, metabolite_id):
		ExperimentType.__init__(self)
		self.gene_id = gene_id
		self.metabolite_id = metabolite_id

	def __hash__(self):
		return hash((self.gene_id, self.metabolite_id))

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))

class ReconstructionActivity(ExperimentType):
	def __init__(self, activity_id):
		ExperimentType.__init__(self)
		self.activity_id = activity_id

	def __hash__(self):
		return hash(self.activity_id)

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))

class ReconstructionEnzReaction(ExperimentType):
	def __init__(self, reaction_id, enzyme_id):
		ExperimentType.__init__(self)
		self.reaction_id = reaction_id
		self.enzyme_id = enzyme_id

	def __hash__(self):
		return hash((self.reaction_id, self.enzyme_id))

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))

class ReconstructionTransporterRequired(ExperimentType):
	def __init__(self, transport_activity_id, transporter_id):
		ExperimentType.__init__(self)
		self.transport_activity_id = transport_activity_id
		self.transporter_id = transporter_id

	def __hash__(self):
		return hash((self.transport_activity_id, self.transporter_id))

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))




class ExperimentDescription:
	def __init__(self, exp_type, interventions=[]):
		self.experiment_type = exp_type
		self.interventions = frozenset(interventions)

	def __hash__(self):
		return hash((self.experiment_type, self.interventions))

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))

class Result:
	def __init__(self, ID, exp_description, outcome):
		self.ID = ID
		self.exp_description = exp_description
		self.outcome = outcome # True or False

	def __hash__(self):
		return hash((self.ID, self.exp_description, self.outcome))

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))

class Experiment:
	def __init__(self, ID, results=[]):
		self.ID = ID
		self.results = frozenset(results)

	def __hash__(self):
		return hash((self.ID, self.results))

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))
