#! /usr/bin/env python3

import exporter

from copy import copy

from exp_repr import DetectionEntity, LocalisationEntity, DetectionActivity, AdamTwoFactorExperiment, ReconstructionActivity, ReconstructionEnzReaction, ReconstructionTransporterRequired, Result, Experiment

from mnm_repr import Catalyses, Transports

import subprocess

import re

from archive import NewResults


class Oracle:
	def __init__(self, archive, entities_ref, activities_ref, model_ref, all_ent, all_comp, all_act, sfx=""):
		ent_id_list = [e.ID for e in entities_ref]
		if len(ent_id_list) != len(set(ent_id_list)):
			print([(e.ID, e.version, type(e)) for e in entities_ref])
			raise ValueError("Oracle __init__: entities list contains more than one version of some entities (at least one)")
		self.archive = archive
		self.entities = entities_ref
		self.activities = activities_ref
		self.model = model_ref
		self.all_ent = all_ent
		self.all_comp = all_comp
		self.all_act = all_act
		self.work_file = './temp/workfile_gringo_clasp_oracle_%s' % sfx


	def execute_exps(self):
		ress = []
		for expD in self.archive.chosen_experiment_descriptions:
			ress.append(self.execute_exp(expD))
		self.archive.record(NewResults(Experiment(None, ress)))


	def execute_exp(self, expD):
		tp = expD.experiment_type
		if isinstance(tp, DetectionEntity) or isinstance(tp, LocalisationEntity) or isinstance(tp, DetectionActivity) or isinstance(tp, AdamTwoFactorExperiment):
			return self.execute_in_vivo(expD)
		else:
			return self.execute_in_vitro_exp(expD)


	def execute_in_vitro_exp(self, expD):
		if isinstance(expD.experiment_type, ReconstructionActivity):
			act_ids = [a.ID for a in self.activities]
			if (expD.experiment_type.activity_id in act_ids):
				return Result(None, expD, 'true')
			else:
				return Result(None, expD, 'false')
			
		elif isinstance(expD.experiment_type, ReconstructionEnzReaction):
			act_ids = [a.ID for a in self.activities]
			matching_entity = [ent for ent in self.entities if ent.ID == expD.experiment_type.enzyme_id][0]
			catalysed_by_entity = [p.activity.ID for p in matching_entity.properties if isinstance(p, Catalyses)]
			if not (expD.experiment_type.reaction_id in act_ids):
				return Result(None, expD, 'false')
			elif not (expD.experiment_type.reaction_id in catalysed_by_entity):
#				print('\n\n no ent \n\n')
				return Result(None, expD, 'false')
			else:
				return Result(None, expD, 'true')

		elif isinstance(expD.experiment_type, ReconstructionTransporterRequired):
			act_ids = [a.ID for a in self.activities]
			matching_entity = [ent for ent in self.entities if ent.ID == expD.experiment_type.transporter_id][0]
			transported_by_entity = [p.activity.ID for p in matching_entity.properties if isinstance(p, Transports)]
			if not (expD.experiment_type.transport_activity_id in act_ids):
				return Result(None, expD, 'false')
			elif not (expD.experiment_type.transport_activity_id in transported_by_entity):
				return Result(None, expD, 'false')
			else:
				return Result(None, expD, 'true')

		else:
			raise TypeError("execute_in_vitro_exp: experiment type not recognised: %s" % expD.experiment_type)


	def execute_in_vivo(self, expD):
		inp = self.prepare_input_in_vivo(expD)
		out = self.write_and_execute(inp)
		res = self.process_output(out, expD)
		return res


	def prepare_input_in_vivo(self, expD):
		copied_model = copy(self.model)
		copied_model.ID = 'copied_%s' % self.model.ID
		copied_model.apply_interventions(expD.interventions)
		exported_ent = exporter.export_entities(self.all_ent)
		exported_comp = exporter.export_compartments(self.all_comp)
		exported_act = exporter.export_activities(self.all_act + self.archive.import_activities)
		exported_model = exporter.export_models_exp_design([copied_model])
		exported_model_rules = exporter.models_rules(len(copied_model.intermediate_activities))
		exported_display = exporter.export_display_for_oracle(expD)
		inp = [exported_ent, exported_comp, exported_act, exported_model, exported_display, exported_model_rules]
		inp = [val for sublist in inp for val in sublist] # flatten
		return inp


	def write_and_execute(self, inp):
		# try: remove the file
		with open(self.work_file, 'w') as f:
			for string in inp:
				read_data = f.write(string)
		# could suppress there warnig messages later on
		gringo = subprocess.Popen(['gringo', self.work_file], stdout=subprocess.PIPE)
		clasp = subprocess.Popen(['clasp', '-n', '0'], stdin=gringo.stdout, stdout=subprocess.PIPE)
		gringo.stdout.close()
		output_enc = clasp.communicate()[0]
		output_dec = output_enc.decode('utf-8')
		return output_dec


	def process_output(self, out, expD):
		answer = out.split('\n')
		try:
			answer.remove('')
		except:
			pass
		answer = answer[answer.index([st for st in answer if st.startswith('Answer: ')][0])+1] # gets the string after 'Answer: ' string

		if isinstance(expD.experiment_type, DetectionEntity):
			if (re.search('synthesizable\(%s,' % expD.experiment_type.entity_id, answer) != None):
				return Result(None, expD, 'true')
			elif (re.search('initially_present\(%s,' % expD.experiment_type.entity_id, answer) != None):
				return Result(None, expD, 'true')
			else:
				return Result(None, expD, 'false')

		elif isinstance(expD.experiment_type, LocalisationEntity):
			if (re.search('synthesizable\(%s,.*?,%s,' % (expD.experiment_type.entity_id, expD.experiment_type.compartment_id), answer) != None):
				return Result(None, expD, 'true')
			elif (re.search('initially_present\(%s,.*?,%s,' % (expD.experiment_type.entity_id, expD.experiment_type.compartment_id), answer) != None):
				return Result(None, expD, 'true')
			else:
				return Result(None, expD, 'false')

		elif isinstance(expD.experiment_type, DetectionActivity):
			if (re.search('active\(%s,' % expD.experiment_type.activity_id, answer) != None):
				return Result(None, expD, 'true')
			else:
				return Result(None, expD, 'false')

		elif isinstance(expD.experiment_type, AdamTwoFactorExperiment):
			tpl = (expD.experiment_type.gene_id, expD.experiment_type.metabolite_id)
			if (re.search('predicts\(.*?,experiment\(adam_two_factor_exp,%s,%s\),true' % tpl, answer) != None):
				return Result(None, expD, 'true')
			else:
				return Result(None, expD, 'false')

		else:
			raise TypeError("oracle process_output: experiment type not recognised: %s" % expD.experiment_type)
