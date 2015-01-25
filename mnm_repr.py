#! /usr/bin/env python3

class Element:
	def __init__(self, ID, name):
		self.ID = ID
		self.name = name


class Entity(Element):
	def __init__(self, ID, name, version, properties):
		Element.__init__(self, ID, name)
		self.version = version
		self.properties = frozenset(properties)
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
	def __init__(self, ID, name, required_conditions, changes):
		Element.__init__(self, ID, name)
		self.required_conditions = frozenset(required_conditions)
		self.changes = frozenset(changes)
		self.detection_cost = None
		self.base_reconstruction_cost = None
		self.add_cost = None
		self.remove_cost = None

class Growth(Activity):
	def __init__(self, conditions, ID, name=None):
		Activity.__init__(self, ID, name, required_conditions, changes)

class Expression(Activity):
	def __init__(self, coding_gene, product_conditions, ID, name=None):
		Activity.__init__(self, ID, name, required_conditions, changes)

class Reaction(Activity):
	def __init__(self, substrates, products, ID, name=None):
		Activity.__init__(self, ID, name, required_conditions, changes)

class Transport(Activity):
	def __init__(self, source_conditions, destination_conditions, ID, name=None):
		Activity.__init__(self, ID, name, required_conditions, changes)

class ComplexFormation(Activity):
	def __init__(self, substrates, products, ID, name=None):
		Activity.__init__(self, ID, name, required_conditions, changes)


class Property:
	def __init__(self):
		pass

class Catalyses(Property):
	def __init__(self, activity):
		Property.__init__(self)
		self.activity = activity

class Transports(Property):
	def __init__(self, activity):
		Property.__init__(self)
		self.activity = activity


class Condition:
	def __init__(self):
		pass

class PresentEntity(Condition):
	def __init__(self, entity, compartment):
		self.entity = entity
		self.compartment = compartment

class PresentCatalyst(Condition):
	def __init__(self, compartment):
		self.compartment = compartment

class PresentTransporter(Condition):
	def __init__(self, compartment):
		self.compartment = compartment


class Compartment:
	def __init__(self):
		pass

class Medium(Compartment):
	def __init__(self):
		pass

class CellMembrane(Compartment):
	def __init__(self):
		pass

class CellMembraneOuterSide(Compartment):
	def __init__(self):
		pass

class CellMembraneInnerSide(Compartment):
	def __init__(self):
		pass

class Cytosol(Compartment):
	def __init__(self):
		pass

class Mitochondrium(Compartment):
	def __init__(self):
		pass

class MitochMatrix(Compartment):
	def __init__(self):
		pass

class MitochOuterMembrane(Compartment):
	def __init__(self):
		pass

class MitochOuterMembraneOuterSide(Compartment):
	def __init__(self):
		pass

class MitochOuterMembraneInnerSide(Compartment):
	def __init__(self):
		pass

class MitochInnerMembrane(Compartment):
	def __init__(self):
		pass

class MitochInnerMembraneOuterSide(Compartment):
	def __init__(self):
		pass

class MitochInnerMembraneInnerSide(Compartment):
	def __init__(self):
		pass

class GolgiMembrane(Compartment):
	def __init__(self):
		pass

class GolgiMembraneOuterSide(Compartment):
	def __init__(self):
		pass

class GolgiMembraneInnerSide(Compartment):
	def __init__(self):
		pass

class GolgiApparatus(Compartment):
	def __init__(self):
		pass

class Nucleus(Compartment):
	def __init__(self):
		pass

class NuclearMembrane(Compartment):
	def __init__(self):
		pass

class NuclearMembraneOuterSide(Compartment):
	def __init__(self):
		pass

class NuclearMembraneInnerSide(Compartment):
	def __init__(self):
		pass

class EndoplasmicReticulum(Compartment):
	def __init__(self):
		pass

class ERMembrane(Compartment):
	def __init__(self):
		pass

class ERMembraneOuterSide(Compartment):
	def __init__(self):
		pass

class ERMembraneInnerSide(Compartment):
	def __init__(self):
		pass

class Vacuole(Compartment):
	def __init__(self):
		pass

class VacuolarMembrane(Compartment):
	def __init__(self):
		pass

class VacuolarMembraneMediumSide(Compartment):
	def __init__(self):
		pass

class VacuolarMembraneCytosolSide(Compartment):
	def __init__(self):
		pass

class VacuolarMembraneInnerSide(Compartment):
	def __init__(self):
		pass

class PeroxisomalMembrane(Compartment):
	def __init__(self):
		pass

class PeroxisomalMembraneInnerSide(Compartment):
	def __init__(self):
		pass

class PeroxisomalMembraneOuterSide(Compartment):
	def __init__(self):
		pass

class Peroxisome(Compartment):
	def __init__(self):
		pass



class Intervention:
	def __init__(self, condition_or_activity):
		self.condition_or_activity = condition_or_activity

class Add(Intervention):
	def __init__(self, condition_or_activity):
		Intervention.__init__(self, condition_or_activity)

class Remove(Intervention):
	def __init__(self, condition_or_activity):
		Intervention.__init__(self, condition_or_activity)



class Model:
	def __init__(self, ID, setup_conditions, intermediate_activities, termination_conditions, status='Active'):
		self.ID = ID
		self.setup_conditions = frozenset(setup_conditions)
		self.intermediate_activities = frozenset(intermediate_activities)
		self.termination_conditions = frozenset(termination_conditions)
		self.status = status
		self.quality = None

	def apply_interventions(self, interventions):
		for intervention in interventions:
			self.apply_intervention(intervention)

	def apply_intervention(self, intervention):
		if type(intervention) == Add:
			if isinstance(intervention.condition_or_activity, Condition):
				new_set = set(self.setup_conditions)
				new_set.add(intervention.condition_or_activity)
				self.setup_conditions = frozenset(new_set)
			elif isinstance(intervention.condition_or_activity, Activity):
				new_set = set(self.intermediate_activities)
				new_set.add(intervention.condition_or_activity)
				self.intermediate_activities = frozenset(new_set)
			else:
				raise TypeError('intervention is neither condition nor activity: %s' % type(intervention.condition_or_activity))

		elif type(intervention) == Remove:
			if isinstance(intervention.condition_or_activity, Condition):
				new_set = set(self.setup_conditions)
				new_set.remove(intervention.condition_or_activity)
				self.setup_conditions = frozenset(new_set)
			elif isinstance(intervention.condition_or_activity, Activity):
				new_set = set(self.intermediate_activities)
				new_set.remove(intervention.condition_or_activity)
				self.intermediate_activities = frozenset(new_set)
			else:
				raise TypeError('intervention is neither condition nor activity: %s' % type(intervention.condition_or_activity))

		else:
			raise TypeError('type of intervention not recognised: %s' % type(intervention))
