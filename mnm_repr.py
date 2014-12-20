#! /usr/bin/env python3

class Element:
	def __init__(self, ID, name):
		self.ID = ID
		self.name = name


class Entity(Element):
	def __init__(self, ID, name, version, properties):
		Element.__init__(self, ID, name)
		self.version = version
		self.properties = set(properties)
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
	def __init__(self, ID, name):
		Element.__init__(self, ID, name)
		self.detection_cost = None

class Growth(Activity):
	def __init__(self, conditions, ID, name=None):
		Activity.__init__(self, ID, name)
		self.required_conditions = set(conditions)

class Expression(Activity):
	def __init__(self, coding_gene, product_conditions, ID, name=None):
		Activity.__init__(self, ID, name)
		self.coding_gene = coding_gene
		self.product_conditions = set(product_conditions)

class NonEnzymaticReaction(Activity):
	def __init__(self, substrates, products, ID, name=None):
		Activity.__init__(self, ID, name)
		self.substrates = set(substrates)
		self.products = set(products)

class EnzymaticReaction(Activity):
	def __init__(self, substrates, products, ID, name=None):
		Activity.__init__(self, ID, name)
		self.substrates = set(substrates)
		self.products = set(products)

class TransporterNotRequired(Activity):
	def __init__(self, source_conditions, destination_conditions, ID, name=None):
		Activity.__init__(self, ID, name)
		self.source_conditions = set(source_conditions)
		self.destination_conditions = set(destination_conditions)

class TransporterRequired(Activity):
	def __init__(self, source_conditions, destination_conditions, transporter_location, ID, name=None):
		Activity.__init__(self, ID, name)
		self.source_conditions = set(source_conditions)
		self.destination_conditions = set(destination_conditions)
		self.transporter_location = transporter_location

class NotCatalysedComplexFormation():
	def __init__(self, substrates, products, ID, name=None):
		Activity.__init__(self, ID, name)
		self.substrates = set(substrates)
		self.products = set(products)

class CatalysedComplexFormation():
	def __init__(self, substrates, products, ID, name=None):
		Activity.__init__(self, ID, name)
		self.substrates = set(substrates)
		self.products = set(products)


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
	def __init__(self):
		pass

class Present(Condition):
	def __init__(self, entity, compartment):
		self.entity = entity
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
	def __init__(self, ID, setup_conds, intermediate_activities, termination_conds, status='Active'):
		self.ID = ID
		self.setup_conds = set(setup_conds)
		self.intermediate_activities = set(intermediate_activities)
		self.termination_conds = set(termination_conds)
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
				self.intermediate_activities.append(intervention.condition_or_activity)
			else:
				raise TypeError('intervention is neither condition nor activity: %s' % type(intervention.condition_or_activity))

		elif type(intervention) == Remove:
			if isinstance(intervention.condition_or_activity, Condition):
				self.setup_conds.remove(intervention.condition_or_activity)
			elif isinstance(intervention.condition_or_activity, Activity):
				self.intermediate_activities.remove(intervention.condition_or_activity)
			else:
				raise TypeError('intervention is neither condition nor activity: %s' % type(intervention.condition_or_activity))

		else:
			raise TypeError('type of intervention not recognised: %s' % type(intervention))
