#! /usr/bin/env python3

class Element:
	def __init__(self, ID, name):
		self.ID = ID
		self.name = name


class Entity(Element):
	def __init__(self, ID, name, version, properties):
		Element.__init__(self, ID, name)
		self.version = version
		self.properties = [x for x in properties]
		self.add_cost = None
		self.remove_cost = None
		self.detection_cost = None
		self.localisation_cost = None

class Gene(Entity):
	def __init__(self, ID, name=None, version=None, properties=[]):
		Entity.__init__(self, ID, name, version, properties)

class Metabolite(Entity):
	def __init__(self, ID, name=None, version=None, properties=[]):
		Entity.__init__(self, ID, name, version, properties)

class Protein(Entity):
	def __init__(self, ID, name=None, version=None, properties=[]):
		Entity.__init__(self, ID, name, version, properties)

class Complex(Entity):
	def __init__(self, ID, name=None, version=None, properties=[]):
		Entity.__init__(self, ID, name, version, properties)


class Activity(Element):
	def __init__(self):
		self.detection_cost = None

class Growth(Activity):
	def __init__(self, conditions):
		Activity.__init__(self)
		self.required_conditions = conditions

class Expression(Activity):
	def __init__(self, coding_gene, product_conditions):
		Activity.__init__(self)
		self.coding_gene = coding_gene
		self.product_conditions = product_conditions

class NonEnzymaticReaction(Activity):
	def __init__(self, substrates, products):
		Activity.__init__(self)
		self.substrates = substrates
		self.products = products

class EnzymaticReaction(Activity):
	def __init__(self, substrates, products):
		Activity.__init__(self)
		self.substrates = substrates
		self.products = products

class TransporterNotRequired(Activity):
	def __init__(self, source_conditions, destination_conditions):
		Activity.__init__(self)
		self.source_conditions = source_conditions
		self.destination_conditions = destination_conditions

class TransporterRequired(Activity):
	def __init__(self, source_conditions, destination_conditions, transporter_location):
		Activity.__init__(self)
		self.source_conditions = source_conditions
		self.destination_conditions = destination_conditions
		self.transporter_location = transporter_location


class Property:
	def __init__(self, activity):
		self.activity = activity

class Catalyses(Property):
	def __init__(self, activity):
		Property.__init__(self, activity)

class Transports(Property):
	def __init__(self, activity):
		Property.__init__(self, activity)


class Condition:

class Present(Condition):
	def __init__(self, entity, compartment):
		self.entity = entity
		self.compartment = compartment


class Compartment:

class Medium(Compartment):

class MediumCytosolMembrane(Compartment):

class Mitochondrium(Compartment):

class MitochMatrix(Compartment):

class MitochOuterMembrane(Compartment):

class MitochInnerMembrane(Compartment):


class Intervention():
	def __init__(self, condition_or_activity):
		self.condition_or_activity = condition_or_activity

class Add(Intervention):
	def __init__(self, condition_or_activity):
		Intervention__init__(self, condition_or_activity)

class Remove(Intervention):
	def __init__(self, condition_or_activity):
		Intervention__init__(self, condition_or_activity)


class Model:
	def __init__(self, ID, setup_conds, intermediate_activities, termination_conds, status='Active'):
		self.ID = ID
		self.setup_conds = setup_conds
		self.intermediate_activities = intermediate_activities
		self.termination_conds = termination_conds
		self.status = status
		self.quality = None

	def apply_interventions(self, interventions):
		for intervention in interventions:
			self.apply_intervention(intervention)

	def apply_intervention(self, intervention):
		if type(intervention) == Add:
			if isinstance(intervention.condition_or_activity, Condition):
				self.setup_conds.append(intervention.condition_or_activity)
			elif isinstance(intervention.condition_or_activity, Activity):
				self.termination_conds.append(intervention.condition_or_activity)
			else:
				raise TypeError('intervention is neither condition nor activity: %s' % type(intervention.condition_or_activity))

		elif type(intervention) == Remove:
			if isinstance(intervention.condition_or_activity, Condition):
				self.setup_conds.remove(intervention.condition_or_activity)
			elif isinstance(intervention.condition_or_activity, Activity):
				self.termination_conds.remove(intervention.condition_or_activity)
			else:
				raise TypeError('intervention is neither condition nor activity: %s' % type(intervention.condition_or_activity))

		else:
			raise TypeError('type of intervention not recognised: %s' % type(intervention))
