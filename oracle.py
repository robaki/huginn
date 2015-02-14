#! /usr/bin/env python3

import exporter

from copy import copy

from exp_repr import DetectionEntity, LocalisationEntity, DetectionActivity, AdamTwoFactorExperiment, ReconstructionActivity, ReconstructionEnzReaction, ReconstructionTransporterRequired, Result

from mnm_repr import Catalyses, Transports

import subprocess

import re


class Oracle:
	def __init__(self, entities_ref, activities_ref, model_ref, all_ent, all_comp, all_act):
		ent_id_list = [e.ID for e in entities_ref]
		if len(ent_id_list) != len(set(ent_id_list)):
			raise ValueError("Oracle __init__: entities list contains more than one version of some entities (at least one)")
		self.entities = entities_ref
		self.activities = activities_ref
		self.model = model_ref
		self.all_ent = all_ent
		self.all_comp = all_comp
		self.all_act = all_act


	def execute_in_vitro_exps(self, expD):
		if isinstance(expD.experiment_type, ReconstructionActivity):
			act_ids = [a.ID for a in self.activities]
			if (expD.experiment_type.activity_id in act_ids):
				return Result(None, expD, True)
			else:
				return Result(None, expD, False)
			
		elif isinstance(expD.experiment_type, ReconstructionEnzReaction):
			act_ids = [a.ID for a in self.activities]
			matching_entity = [ent for ent in self.entities if ent.ID == expD.experiment_type.enzyme_id][0]
			catalysed_by_entity = [p.activity.ID for p in matching_entity.properties if isinstance(p, Catalyses)]
			if not (expD.experiment_type.reaction_id in act_ids):
				return Result(None, expD, False)
			elif not (expD.experiment_type.reaction_id in catalysed_by_entity):
				print('\n\n no ent \n\n')
				return Result(None, expD, False)
			else:
				return Result(None, expD, True)

		elif isinstance(expD.experiment_type, ReconstructionTransporterRequired):
			act_ids = [a.ID for a in self.activities]
			matching_entity = [ent for ent in self.entities if ent.ID == expD.experiment_type.transporter_id][0]
			transported_by_entity = [p.activity.ID for p in matching_entity.properties if isinstance(p, Transports)]
			if not (expD.experiment_type.transport_activity_id in act_ids):
				return Result(None, expD, False)
			elif not (expD.experiment_type.transport_activity_id in transported_by_entity):
				return Result(None, expD, False)
			else:
				return Result(None, expD, True)

		else:
			raise TypeError("execute_in_vitro_exps: experiment type not recognised: %s" % expD.experiment_type)


	def execute_in_vivo(self, expD):
		inp = self.prepare_input_in_vivo(expD)
		out = self.write_and_execute(inp)
#		print(out)


	def prepare_input_in_vivo(self, expD):
		copied_model = copy(self.model)
		copied_model.ID = 'copied_%s' % self.model.ID
		copied_model.apply_interventions(expD.interventions)
		exported_ent = exporter.export_entities(self.all_ent)
		exported_comp = exporter.export_compartments(self.all_comp)
		exported_act = exporter.export_activities(self.all_act)
		exported_model = exporter.export_models_exp_design([copied_model])
		exported_model_rules = exporter.models_rules(len(copied_model.intermediate_activities))
		exported_display = exporter.export_display_for_oracle(expD)
		inp = [exported_ent, exported_comp, exported_act, exported_model, exported_display, exported_model_rules]
		inp = [val for sublist in inp for val in sublist] # flatten
		return inp


	def write_and_execute(self, inp):
		# try: remove the file
		with open('./temp/workfile_gringo_clasp_oracle', 'w') as f:
			for string in inp:
				read_data = f.write(string)
		# could suppress there warnig messages later on
		gringo = subprocess.Popen(['gringo', './temp/workfile_gringo_clasp_oracle'], stdout=subprocess.PIPE)
		clasp = subprocess.Popen(['clasp', '-n', '0'], stdin=gringo.stdout, stdout=subprocess.PIPE)
		gringo.stdout.close()
		output_enc = clasp.communicate()[0]
		output_dec = output_enc.decode('utf-8')
		return output_dec


	def process_output(self, out, expD):
		if isinstance(expDescription.experiment_type, DetectionEntity):
			
			'synthesizable(,,,)' 'initially_present(,,,)'
		elif isinstance(expDescription.experiment_type, LocalisationEntity):
			
			'synthesizable(,,,)' 'initially_present(,,,)'
		elif isinstance(expDescription.experiment_type, DetectionActivity):
			
			'active(,)'
		elif isinstance(expDescription.experiment_type, AdamTwoFactorExperiment):
			
			'predicts(,)'
		else:
			raise TypeError("oracle process_output: experiment type not recognised: %s" % expD.experiment_type)
