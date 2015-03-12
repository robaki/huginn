#! /usr/bin/env python3

from exp_repr import DetectionEntity, AdamTwoFactorExperiment, ReconstructionActivity, ReconstructionEnzReaction, ReconstructionTransporterRequired
from exp_repr import LocalisationEntity
from exp_repr import DetectionActivity

from mnm_repr import CellMembrane, CellMembraneOuterSide, CellMembraneInnerSide, Cytosol, Mitochondrium, MitochMatrix, MitochOuterMembrane, MitochOuterMembraneOuterSide, MitochOuterMembraneInnerSide, MitochInnerMembrane, MitochInnerMembraneOuterSide, MitochInnerMembraneInnerSide, GolgiMembrane, GolgiMembraneOuterSide, GolgiMembraneInnerSide, GolgiApparatus, Nucleus, NuclearMembrane, NuclearMembraneOuterSide, NuclearMembraneInnerSide, EndoplasmicReticulum, ERMembrane, ERMembraneOuterSide, ERMembraneInnerSide, Vacuole, VacuolarMembrane, VacuolarMembraneMediumSide, VacuolarMembraneCytosolSide, VacuolarMembraneInnerSide, PeroxisomalMembrane, PeroxisomalMembraneInnerSide, PeroxisomalMembraneOuterSide, Peroxisome, Medium

import mnm_repr


class CostModel:
	def __init__(self, entities, compartments, activities, setup_conds, import_activities=[]):
		self.generate_all_possible(entities, compartments, activities, setup_conds, import_activities)


	def generate_all_possible(self, entities, compartments, activities, setup_conds, import_activities):
		# exp types:
		self.types = {DetectionEntity:None, AdamTwoFactorExperiment:None,
			ReconstructionActivity:None, ReconstructionEnzReaction:None,
			ReconstructionTransporterRequired:None, LocalisationEntity:None,
			DetectionActivity:None}
		# compartments for checking localisation:
		self.design_compartment = {'c_02':None, 'c_03':None, 'c_04':None, 'c_05':None,
			'c_06':None, 'c_07':None, 'c_08':None, 'c_09':None, 'c_10':None, 'c_11':None,
			'c_12':None, 'c_13':None, 'c_14':None, 'c_15':None, 'c_16':None, 'c_17':None,
			'c_18':None, 'c_19':None, 'c_20':None, 'c_21':None, 'c_22':None, 'c_23':None,
			'c_24':None, 'c_25':None, 'c_26':None, 'c_27':None, 'c_28':None, 'c_29':None,
			'c_30':None, 'c_31':None, 'c_32':None, 'c_33':None, 'c_34':None}
		# rest of elements: 
		self.design_deletable = {}
		self.design_available = {}
		self.design_activity_rec = {}
		self.design_activity_det = {}
		self.design_entity_loc = {}
		self.design_entity_det = {}
		self.intervention_add = {}
		self.intervention_remove = {}
		#
		for act in import_activities:
			self.intervention_add[mnm_repr.Add(act)] = 0
		#
		for st in setup_conds:
			if (isinstance(st.entity, mnm_repr.Gene) or isinstance(st.compartment, Medium)): # all genes can be removed; metabs can only be removed from medium
				self.intervention_remove[mnm_repr.Remove(st)] = None
			if isinstance(st.entity, mnm_repr.Gene):
				self.design_deletable[st.entity] = None
		#
		for ent in entities:
			if isinstance(ent, mnm_repr.Gene):
				continue
			else: # Met, Prot, Cplx
				self.design_available[ent] = None
				self.design_entity_det[ent] = None
			if isinstance(ent, mnm_repr.Metabolite):
				self.intervention_add[mnm_repr.Add(mnm_repr.PresentEntity(ent, Medium()))] = None
			else: # Prot, Cplx
				self.design_entity_loc[ent] = None
		#
		for act in activities:
			if act in import_activities:# don't test these additional import reactions: they're only to help with experiments
				continue
			elif isinstance(act, mnm_repr.Growth):
				self.design_activity_det[act] = None
			else:
				self.design_activity_rec[act] = None


#	def apply_basic_costs_<distribution>_<to_what>(self):


	def remove_None_valued_elements(self):
		for key in list(self.types.keys()):
			if self.types[key] == None:
				del self.types[key]
			else:
				pass
		for key in list(self.design_compartment.keys()):
			if self.design_compartment[key] == None:
				del self.design_compartment[key]
			else:
				pass
		for key in list(self.design_deletable.keys()):
			if self.design_deletable[key] == None:
				del self.design_deletable[key]
			else:
				pass
		for key in list(self.design_available.keys()):
			if self.design_available[key] == None:
				del self.design_available[key]
			else:
				pass
		for key in list(self.design_activity_det.keys()):
			if self.design_activity_det[key] == None:
				del self.design_activity_det[key]
			else:
				pass
		for key in list(self.design_entity_loc.keys()):
			if self.design_entity_loc[key] == None:
				del self.design_entity_loc[key]
			else:
				pass
		for key in list(self.design_entity_det.keys()):
			if self.design_entity_det[key] == None:
				del self.design_entity_det[key]
			else:
				pass
		for key in list(self.intervention_add.keys()):
			if self.intervention_add[key] == None:
				del self.intervention_add[key]
			else:
				pass
		for key in list(self.intervention_remove.keys()):
			if self.intervention_remove[key] == None:
				del self.intervention_remove[key]
			else:
				pass
		for key in list(self.design_activity_rec.keys()):
			if self.design_activity_rec[key] == None:
				del self.design_activity_rec[key]
			else:
				pass


	def calculate_derived_costs(self, activities):
		# calculating costs for complexes
		for ent in self.design_available: # loops through entities
			if isinstance(ent, mnm_repr.Complex): # costs for complexes are derived from costs for their components
				cplx_form = [a for a in activities if a.check_if_is_product(ent)] # find correcponding complex form. reactions
				# costs for complexes can only be calculated if there is exactly 1 formation reaction
				if len(cplx_form) == 1: 
					components = cplx_form[0].return_substrates()
					# if all components have 'available' costs, then calculate cost for 'available' complex
					costs_available = [self.design_available[comp] for comp in components]
					if not (None in costs_available):
						self.design_available[ent] = sum(costs_available)
					else:
						pass
					# the same for 'detection' costs
					costs_det = [self.design_entity_det[comp] for comp in components]
					if not (None in costs_det):
						self.design_entity_det[ent] = sum(costs_available)
					else:
						pass
					# the same for 'localisation' costs
					costs_loc = [self.design_entity_loc[comp] for comp in components]
					if not (None in costs_loc):
						self.design_entity_loc[ent] = sum(costs_available)
					else:
						pass
				else:
					pass
			else:
				pass

		# calculating costs for activities: enzymes and transporters not included here; accounted for in design rules.
		for act in self.design_activity_rec.keys():
			if isinstance(act, mnm_repr.Growth) or isinstance(act, mnm_repr.Expression):
				continue
			else:
				substrates_available_costs = [self.design_available[ent] for ent in act.return_substrates()]
				products_detection_costs = [self.design_entity_det[ent] for ent in act.return_products()]
				if (None in substrates_available_costs):
					continue
				elif (None in products_detection_costs):
					continue
				else:
					self.design_activity_rec[act] = sum(substrates_available_costs) + sum(products_detection_costs)



	def set_all_basic_costs_to_1(self): # for testing
		for key in self.types.keys():
			self.types[key] = 1
		for key in self.design_compartment.keys():
			self.design_compartment[key] = 1
		for key in self.design_deletable.keys():
			self.design_deletable[key] = 1
		for key in self.design_available.keys():
			if isinstance(key, mnm_repr.Complex):
				continue
			else:
				self.design_available[key] = 1
		for key in self.design_activity_det.keys():
			self.design_activity_det[key] = 1
		for key in self.design_entity_loc.keys():
			if isinstance(key, mnm_repr.Complex):
				continue
			else:
				self.design_entity_loc[key] = 1
		for key in self.design_entity_det.keys():
			if isinstance(key, mnm_repr.Complex):
				continue
			else:
				self.design_entity_det[key] = 1
		for key in self.intervention_add.keys():
			if self.intervention_add[key] != 0:# additional import activities should have 0... maybe :d
				self.intervention_add[key] = 1
		for key in self.intervention_remove.keys():
			self.intervention_remove[key] = 1

