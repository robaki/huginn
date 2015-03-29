#! /usr/bin/env python3

import exporter
import random
import subprocess

from exp_repr import DetectionEntity, LocalisationEntity, DetectionActivity, AdamTwoFactorExperiment, ReconstructionActivity, ReconstructionEnzReaction, ReconstructionTransporterRequired, ExperimentDescription

from mnm_repr import PresentEntity, Add, Remove

from archive import ExpDesignFail, ChosenExperiment

from time import gmtime

class ExperimentModule:
	# module for experiment design. Method relies on splitting sum of models' probabilities (qualities) in half.
	# If no model quality modules is used, then model quality = 1 and is constant throught development time.
	# In that case the algorithm just splits set of working models in half.
	def __init__(self, archive, cost_model, use_costs, sfx=""):
		self.archive = archive
		self.cost_model = cost_model
		self.use_costs = use_costs
		self.work_file = './temp/workfile_gringo_clasp_%s' % sfx


	def design_experiments(self):
		exp_input = self.prepare_input_for_exp_design()
		out = self.write_and_execute_gringo_clasp(exp_input)
		experiments = self.process_output(out)
		return experiments


	def write_and_execute_gringo_clasp(self, exp_input):
		# TESTING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#		current_time = gmtime()
#		time_stamp = '_'.join([str(x) for x in [current_time[0], current_time[1], current_time[2], current_time[3], current_time[4], current_time[5]]])
#		modified_workfile = '_'.join([self.work_file, time_stamp])
		# try remove the file
		with open(self.work_file, 'w') as f:
			for string in exp_input:
				read_data = f.write(string)
		# could suppress there warnig messages later on
		gringo = subprocess.Popen(['gringo', self.work_file], stdout=subprocess.PIPE)
		clasp = subprocess.Popen(['clasp', '-n', '0'], stdin=gringo.stdout, stdout=subprocess.PIPE)
		gringo.stdout.close()
		output_enc = clasp.communicate()[0]
		output_dec = output_enc.decode('utf-8')
		return output_dec


	def prepare_input_for_exp_design(self):
		exported = []
		exported.extend(exporter.hide_show_statements()) # export hide/show stuff
		exported.extend(exporter.export_compartments(self.archive.mnm_compartments))
		exported.extend(exporter.export_entities(self.archive.mnm_entities))
		exported.extend(exporter.export_activities(self.archive.mnm_activities + self.archive.import_activities))
		exported.extend(exporter.export_models_exp_design(self.archive.working_models)) # export models info
		exported.extend(exporter.models_nr_and_probabilities(self.archive.working_models)) # + probabilities and numbers
		exported.append(exporter.modeh_replacement(self.cost_model)) # export design elements (modeh eqiv)
		exported.extend(exporter.design_constraints_basic()) # export rules forcing and restricting exp design
		for exp in self.archive.known_results:
			exp_descriptions = [res.exp_description for res in exp.results]
			for des in exp_descriptions:
				exported.extend(exporter.ban_experiment(des)) # export ban experiment(s) (from old exps)
		exported.append(exporter.constant_for_calculating_score(self.calculate_constant_for_scores())) # calculate constant for scores and export it
		exported.extend(exporter.advanced_exp_design_rules()) # export scoring rules/optimisation
		if self.use_costs: # * export cost, and optimisation rule for that
			exported.extend(exporter.cost_rules(self.cost_model))
			exported.extend(exporter.cost_minimisation_rules())
		else:
			pass
		exported.extend(exporter.experiment_design_rules()) # export design rules
		exported.extend(exporter.interventions_rules())
		exported.extend(exporter.predictions_rules())
		exported.extend(exporter.models_rules(len(self.archive.mnm_activities + self.archive.import_activities))) 
		return exported


	def calculate_constant_for_scores(self):
		return int((sum([mod.quality for mod in self.archive.working_models])*10)/2)

#
#
#

	def process_output(self, out):
		experiments = []
		# check if program was satisfiable
		if 'UNSATISFIABLE' in out:
			return False
		# find optimum info:
		strings = out.split('\n')
		strings.remove('')
		# find answers:
		answers = self.get_answers(strings)
		if answers == False:
			return False
		# process answers:
		for ans in answers:
			components = ans.split(' ')
			exp_type = self.get_expType(components)
			# decide what to do next based on the type
			if exp_type == 'design_type(adam_two_factor_exp)':
				expT = self.process_exp_type_adam_two_factor(components)
			elif exp_type == 'design_type(transp_reconstruction_exp)':
				expT = self.process_exp_type_transp_reconstruction(components)
			elif exp_type == 'design_type(enz_reconstruction_exp)':
				expT = self.process_exp_type_enz_reconstruction(components)
			elif exp_type == 'design_type(basic_reconstruction_exp)':
				expT = self.process_exp_type_basic_reconstruction(components)
			elif exp_type == 'design_type(detection_activity_exp)':
				expT = self.process_exp_type_detection_activity(components)
			elif exp_type == 'design_type(localisation_entity_exp)':
				expT = self.process_exp_type_localisation_entity(components)
			elif exp_type == 'design_type(detection_entity_exp)':
				expT = self.process_exp_type_detection_entity(components)
			else:
				raise ValueError('process_output: design_type(...) not recognised: %s' % exp_type)

			interventions = self.get_interventions(components)
			# if not all components of an answer were used: sth went wrong in design phase or processing
			if len(components) > 0:
				raise ValueError("process_output: not all components used: %s" % components)
			experiments.append(ExperimentDescription(expT, interventions))
		return experiments


	def get_answers(self, strings):
		answers = []
		try: # can fail if the solver fails (not enough RAM; bad memory allocation...)
			optimum = [st.split('Optimization : ')[1] for st in strings if st.startswith('Optimization : ')][0]
		except IndexError as err:
			print('experiment_module: solver failed.')
			print('output as strings: %s' % strings)
			return False
			
		for st in strings:
			if not st.startswith('Answer: '):
				continue
			optimization = strings[strings.index(st) + 2].split('Optimization: ')[1] # get two after 'answer'
			if optimization == optimum:
				answers.append(strings[strings.index(st) + 1]) # get one after 'answer'
			else:
				pass
		return answers


	def get_expType(self, components):
		exp_type = [st for st in components if st.startswith('design_type(')]
		if len(exp_type) > 1:
			raise ValueError('process_output: more than one design_type statement')
		# remove 'used' info
		components.remove(exp_type[0])
		#
		return exp_type[0]


	def process_exp_type_adam_two_factor(self, components):
		gene = [st for st in components if st.startswith('design_deletable(')]
		if len(gene) > 1:
			raise ValueError('process_output: more than one element of the same kind statement %s' % gene)
		gene_id = gene[0].split('design_deletable(')[1].split(')')[0]
		metab = [st for st in components if st.startswith('design_available(')]
		if len(metab) > 1:
			raise ValueError('process_output: more than one element of the same kind statement %s' % metab)
		metab_id = metab[0].split('design_available(')[1].split(')')[0]
		components.remove(gene[0])
		components.remove(metab[0])
		return AdamTwoFactorExperiment(gene_id, metab_id)


	def process_exp_type_transp_reconstruction(self, components):
		act = [st for st in components if st.startswith('design_activity_rec(')]
		if len(act) > 1:
			raise ValueError('process_output: more than one element of the same kind statement %s' % act)
		act_id = act[0].split('design_activity_rec(')[1].split(')')[0]
		ent = [st for st in components if st.startswith('design_available(')]
		if len(ent) > 1:
			raise ValueError('process_output: more than one element of the same kind statement %s' % ent)
		ent_id = ent[0].split('design_available(')[1].split(')')[0]
		components.remove(act[0])
		components.remove(ent[0])
		return ReconstructionTransporterRequired(act_id, ent_id)


	def process_exp_type_enz_reconstruction(self, components):
		act = [st for st in components if st.startswith('design_activity_rec(')]
		if len(act) > 1:
			raise ValueError('process_output: more than one element of the same kind statement %s' % act)
		act_id = act[0].split('design_activity_rec(')[1].split(')')[0]
		ent = [st for st in components if st.startswith('design_available(')]
		if len(ent) > 1:
			raise ValueError('process_output: more than one element of the same kind statement %s' % ent)
		ent_id =  ent[0].split('design_available(')[1].split(')')[0]
		components.remove(act[0])
		components.remove(ent[0])
		return ReconstructionEnzReaction(act_id, ent_id)


	def process_exp_type_basic_reconstruction(self, components):
		act = [st for st in components if st.startswith('design_activity_rec(')]
		if len(act) > 1:
			raise ValueError('process_output: more than one element of the same kind statement %s' % act)
		act_id = act[0].split('design_activity_rec(')[1].split(')')[0]
		components.remove(act[0])
		return ReconstructionActivity(act_id)


	def process_exp_type_detection_activity(self, components):
		act = [st for st in components if st.startswith('design_activity_det(')]
		if len(act) > 1:
			raise ValueError('process_output: more than one element of the same kind statement %s' % act)
		act_id = act[0].split('design_activity_det(')[1].split(')')[0]
		components.remove(act[0])
		return DetectionActivity(act_id)


	def process_exp_type_localisation_entity(self, components):
		ent = [st for st in components if st.startswith('design_entity_loc(')]
		if len(ent) > 1:
			raise ValueError('process_output: more than one element of the same kind statement %s' % ent)
		ent_id = ent[0].split('design_entity_loc(')[1].split(')')[0]
		comp = [st for st in components if st.startswith('design_compartment(')]
		if len(comp) > 1:
			raise ValueError('process_output: more than one element of the same kind statement %s' % comp)
		comp_id = comp[0].split('design_compartment(')[1].split(')')[0]
		components.remove(ent[0])
		components.remove(comp[0])
		return LocalisationEntity(ent_id, comp_id )


	def process_exp_type_detection_entity(self, components):
		ent = [st for st in components if st.startswith('design_entity_det(')]
		if len(ent) > 1:
			raise ValueError('process_output: more than one element of the same kind statement %s' % ent)
		ent_id = ent[0].split('design_entity_det(')[1].split(')')[0]
		components.remove(ent[0])
		return DetectionEntity(ent_id)


	def get_interventions(self, components):
		interventions = []
		add_setup = [st for st in components if st.startswith('add(setup_')]
		add_activ = list(set([st for st in components if st.startswith('add')]) - set(add_setup))
		remove = [st for st in components if st.startswith('remove(')]
		for st in add_setup:
			splitted = st.split('add(setup_present(')[1].split(')')[0].split(',')
			entity = self.archive.get_matching_element(splitted[0], splitted[1])
			compartment = self.archive.get_matching_element(splitted[2])
			interventions.append(Add(PresentEntity(entity, compartment)))
		for st in add_activ:
			splitted = st.split('add(')[1].split(')')[0]
			activity = self.archive.get_matching_element(splitted)
			interventions.append(Add(activity))
		for st in remove:
			splitted = st.split('remove(setup_present(')[1].split(')')[0].split(',')
			entity = self.archive.get_matching_element(splitted[0], splitted[1])
			compartment = self.archive.get_matching_element(splitted[2])
			interventions.append(Remove(PresentEntity(entity, compartment)))

		# removing used stuff from components
		[components.remove(st) for st in add_setup]
		[components.remove(st) for st in add_activ]
		[components.remove(st) for st in remove]
		return interventions




class BasicExpModuleNoCosts(ExperimentModule):
	def __init__(self, archive, cost_model, sfx=""):
		ExperimentModule.__init__(self, archive, cost_model, use_costs=False, sfx=sfx)

	def get_experiment(self):
		exps = self.design_experiments()
		if exps == False:
			self.archive.record(ExpDesignFail())
		else:
			self.archive.record(ChosenExperiment([random.choice(exps)]))


class BasicExpModuleWithCosts(ExperimentModule):
	def __init__(self, archive, cost_model, sfx=""):
		ExperimentModule.__init__(self, archive, cost_model, use_costs=True, sfx=sfx)

	def get_experiment(self):
		exps = self.design_experiments()
		if exps == False:
			self.archive.record(ExpDesignFail())
		else:
			self.archive.record(ChosenExperiment([random.choice(exps)]))


