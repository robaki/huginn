#! /usr/bin/env python3
# I, Robert Rozanski, the copyright holder of this work, release this work into the public domain. This applies worldwide. In some countries this may not be legally possible; if so: I grant anyone the right to use this work for any purpose, without any conditions, unless such conditions are required by law.

class Element:
	def __init__(self, ID, name):
		self.ID = ID
		self.name = name


class Entity(Element):
	def __init__(self, ID, name, version, properties):
		Element.__init__(self, ID, name)
		self.version = version
		self.properties = frozenset(properties)
		self.add_cost = 1
		self.remove_cost = 1
		self.detection_cost = 1
		self.localisation_cost = 1

	def __hash__(self):
		return hash((self.ID, self.version))

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))


class Gene(Entity):
	def __init__(self, ID, name=None, version='none', properties=[]):
		Entity.__init__(self, ID, name, version, properties)

class Metabolite(Entity):
	def __init__(self, ID, name=None, version='none', properties=[]):
		Entity.__init__(self, ID, name, version, properties)

class Protein(Entity):
	def __init__(self, ID, name=None, version='none', properties=[]):
		Entity.__init__(self, ID, name, version, properties)

class Complex(Entity):
	def __init__(self, ID, name=None, version='none', properties=[]):
		Entity.__init__(self, ID, name, version, properties)


class Activity(Element):
	def __init__(self, ID, name, required_conditions, changes):
		Element.__init__(self, ID, name)
		self.required_conditions = frozenset(required_conditions)
		self.changes = frozenset(changes)
		# should be turned True or False during creation
		# exporter should raise exception if left with None
		self.reversibility = None
		self.detection_cost = 1
		self.base_reconstruction_cost = 1
		self.add_cost = 1
		self.remove_cost = 1

	def check_if_is_product(self, ent):
		return ent in [con.entity for con in self.changes if isinstance(con, PresentEntity)]

	def return_substrates(self):
		return [con.entity for con in self.required_conditions if isinstance(con, PresentEntity)]

	def return_products(self):
		return [con.entity for con in self.changes if isinstance(con, PresentEntity)]

	def __hash__(self):
		return hash((self.required_conditions, self.changes))

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))

class Growth(Activity):
	def __init__(self, ID, required_conditions, name=None):
		Activity.__init__(self, ID, name, required_conditions, [])

class Expression(Activity):
	def __init__(self, ID, required_conditions, changes, name=None):
		Activity.__init__(self, ID, name, required_conditions, changes)

class Reaction(Activity):
	def __init__(self, ID, required_conditions, changes, name=None):
		Activity.__init__(self, ID, name, required_conditions, changes)

class Transport(Activity):
	def __init__(self, ID, required_conditions, changes, name=None):
		Activity.__init__(self, ID, name, required_conditions, changes)

class ComplexFormation(Activity):
	def __init__(self, ID, required_conditions, changes, name=None):
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

	def __hash__(self):
		return hash((self.entity, self.compartment))

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))

class PresentCatalyst(Condition):
	def __init__(self, compartment):
		self.compartment = compartment

	def __hash__(self):
		return hash(self.compartment)

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))

class PresentTransporter(Condition):
	def __init__(self, compartment):
		self.compartment = compartment

	def __hash__(self):
		return hash(self.compartment)

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))



class Compartment:
	def __init__(self):
		self.ID = None

	def __hash__(self):
		return hash(self.ID)

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))


class Medium(Compartment):
	def __init__(self):
		self.ID = "c_01"

class CellMembrane(Compartment):
	def __init__(self):
		self.ID = "c_02"

class CellMembraneOuterSide(Compartment):
	def __init__(self):
		self.ID = "c_03"

class CellMembraneInnerSide(Compartment):
	def __init__(self):
		self.ID = "c_04"

class Cytosol(Compartment):
	def __init__(self):
		self.ID = "c_05"

class Mitochondrium(Compartment):
	def __init__(self):
		self.ID = "c_06"

class MitochMatrix(Compartment):
	def __init__(self):
		self.ID = "c_07"

class MitochOuterMembrane(Compartment):
	def __init__(self):
		self.ID = "c_08"

class MitochOuterMembraneOuterSide(Compartment):
	def __init__(self):
		self.ID = "c_09"

class MitochOuterMembraneInnerSide(Compartment):
	def __init__(self):
		self.ID = "c_10"

class MitochInnerMembrane(Compartment):
	def __init__(self):
		self.ID = "c_11"

class MitochInnerMembraneOuterSide(Compartment):
	def __init__(self):
		self.ID = "c_12"

class MitochInnerMembraneInnerSide(Compartment):
	def __init__(self):
		self.ID = "c_13"

class GolgiMembrane(Compartment):
	def __init__(self):
		self.ID = "c_14"

class GolgiMembraneOuterSide(Compartment):
	def __init__(self):
		self.ID = "c_15"

class GolgiMembraneInnerSide(Compartment):
	def __init__(self):
		self.ID = "c_16"

class GolgiApparatus(Compartment):
	def __init__(self):
		self.ID = "c_17"

class Nucleus(Compartment):
	def __init__(self):
		self.ID = "c_18"

class NuclearMembrane(Compartment):
	def __init__(self):
		self.ID = "c_19"

class NuclearMembraneOuterSide(Compartment):
	def __init__(self):
		self.ID = "c_20"

class NuclearMembraneInnerSide(Compartment):
	def __init__(self):
		self.ID = "c_21"

class EndoplasmicReticulum(Compartment):
	def __init__(self):
		self.ID = "c_22"

class ERMembrane(Compartment):
	def __init__(self):
		self.ID = "c_23"

class ERMembraneOuterSide(Compartment):
	def __init__(self):
		self.ID = "c_24"

class ERMembraneInnerSide(Compartment):
	def __init__(self):
		self.ID = "c_25"

class Vacuole(Compartment):
	def __init__(self):
		self.ID = "c_26"

class VacuolarMembrane(Compartment):
	def __init__(self):
		self.ID = "c_27"

class VacuolarMembraneMediumSide(Compartment):
	def __init__(self):
		self.ID = "c_28"

class VacuolarMembraneCytosolSide(Compartment):
	def __init__(self):
		self.ID = "c_29"

class VacuolarMembraneInnerSide(Compartment):
	def __init__(self):
		self.ID = "c_30"

class PeroxisomalMembrane(Compartment):
	def __init__(self):
		self.ID = "c_31"

class PeroxisomalMembraneInnerSide(Compartment):
	def __init__(self):
		self.ID = "c_32"

class PeroxisomalMembraneOuterSide(Compartment):
	def __init__(self):
		self.ID = "c_33"

class Peroxisome(Compartment):
	def __init__(self):
		self.ID = "c_34"

class LipidParticle(Compartment):
	def __init__(self):
		self.ID = "c_35"



class Intervention:
	def __init__(self, condition_or_activity):
		self.condition_or_activity = condition_or_activity


	def __hash__(self):
		return hash(self.condition_or_activity)

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))


class Add(Intervention):
	def __init__(self, condition_or_activity):
		Intervention.__init__(self, condition_or_activity)

	def __hash__(self):
		return hash(self.condition_or_activity)

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))


class Remove(Intervention):
	def __init__(self, condition_or_activity):
		Intervention.__init__(self, condition_or_activity)

	def __hash__(self):
		return hash(self.condition_or_activity)

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))



class Model:
	def __init__(self, ID, setup_conditions, intermediate_activities, termination_conditions, status='Active'):
		self.ID = ID
		self.setup_conditions = frozenset(setup_conditions)
		self.intermediate_activities = frozenset(intermediate_activities)
		self.termination_conditions = frozenset(termination_conditions)
		self.status = status
		self.score = None
		self.quality = 1
		self.results_covered = frozenset([])
		self.ignored_results = frozenset([])


	def __copy__(self):
		setup = frozenset(list(self.setup_conditions))
		activ = frozenset(list(self.intermediate_activities))
		termi = frozenset(list(self.termination_conditions))
		new_model = Model(None, setup, activ, termi)
		return new_model

	def __hash__(self):
		return hash((self.setup_conditions, self.intermediate_activities, self.termination_conditions))

	def __eq__(self, other):
		return ((hash(self) == hash(other)) and (type(self) == type(other)))

	def update_ignored_results(self, ignored_results):
		self.ignored_results = frozenset(ignored_results)

	def update_covered_results(self, results_covered):
		self.results_covered = frozenset(results_covered)

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
