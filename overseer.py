#! /usr/bin/env python3

import pickle
from time import gmtime
from archive import CheckPointFail, CheckPointSuccess
from revision import RevCIAddB, RevCIAddR

class Overseer:
	def __init__(self, archive, checkpoint):
		self.archive = archive
		self.checkpoint_version = checkpoint
		self.current_state = 'start'
		self.final_state = 'stop'
		self.cycles_since_last_new_model = 0
		self.cycles_since_best_model_changed = 0


	def start_development(self):
		self.do_transition('test_and_revise_models')


	def stop_development(self):
		pkl_file = open('pickled_archives/archive_%s' % gmtime(), 'wb')
		pickle.dump(self.archive, pkl_file)
		pkl_file.close()
		print('error flags?: %s' % self.error_flag)


	def do_check(self):
		if self.checkpoint_version == 'ignoring':
			# no new models for a while (counter for checks, resets if new model produced sine last check)
			# the best model didn't changed for a while (counter? )
		else: # no ignoring
			if len(self.archive.working_models) => 1: # one model left
				self.archive.record(CheckPointFail('no ignoring'))
			else:
				self.archive.record(CheckPointSuccess())


	def do_transition(self, transition_name):
		tran_dict = [tr for tr in self.available_transitions() if tr['name'] == transition_name]
		if len(tran_dict) > 1: # sanity check
			raise ValueError("do_transition: more than one transition of the same name available: %s" % tran_dict)
		tran_dict[0]['method']() # execute
		self.current_state = tran_dict[0]['dst']# update state


	def available_transitions(self):
		output = [x for x in self.transition_table if (self.current_state == x['src'])] # whole dict
		return output


	def were_new_model_produced_since_last_check(self):
		# get revision/add_model events since last check (filter out failures)
		# if new model: then True (? eeh)
		# if 


class OverseerWithModQuality(Overseer):
	def __init__(self, archive, rev_mod, exp_mod, oracle, threshold_addit_models, qual_mod):
		if (isinstance(rev_mod, RevCIAddB) or isinstance(rev_mod, RevCIAddR)):
			checkpoint = 'ignoring'
		else:
			checkpoint = 'no ignoring'
		Overseer.__init__(self, archive, checkpoint)
		self.threshold_addit_models = threshold_addit_models
		self.transition_table = [
			{'name':'start_development', 'src':'start', 'dst':'models_tested_and_revised', 'method':self.start_development},
			{'name':'get_experiment', 'src':'quality_recalculated', 'dst':'experiment_ready', 'method':exp_mod.get_experiment},
			{'name':'execute_experiment', 'src':'experiment_ready', 'dst':'has_new_result', 'method':oracle.execute_exps},# NewResults
			{'name':'record_result', 'src':'has_new_result', 'dst':'result_recorded', 'method':archive.record},# AcceptedResults
			{'name':'test_and_revise_models', 'src':'result_recorded', 'dst':'models_tested_and_revised', 'method':rev_mod.test_and_revise_all},
			{'name':'produce_additional_models', 'src':'quality_recalculated', 'dst':'produced_additional_models', 'method':rev_mod.produce_additional_models},
			{'name':'recalculate_models_quality', 'src':'models_tested_and_revised', 'dst':'quality_recalculated', 'method':qual_mod.check_and_update_qualities},
			{'name':'recalculate_models_quality', 'src':'produced_additional_models', 'dst':'quality_recalculated', 'method':qual_mod.check_and_update_qualities},
			{'name':'stop_development', 'src':'produced_additional_models', 'dst':'stop', 'method':self.stop_development},
			{'name':'stop_development', 'src':'experiment_ready', 'dst':'stop', 'method':self.stop_development}]


	def run(self, threshold_addit_models):
		while not (self.current_state == self.final_state):
			# if error: stop dev
			if self.archive.error_flag == True:
				self.do_transition('stop_development')
			# if only one transition available, do it
			elif len(self.available_transitions()) == 1:
				self.do_transition(self.available_transitions()[0]['method'])
			# if number of working models below thershold, then produce some more
			elif (self.current_state == 'quality_recalculated') and (len(self.archive.working_models) < threshold_addit_models):
				self.do_transition('produce_additional_models')
			elif (self.current_state == 'quality_recalculated') and (len(self.archive.working_models) => threshold_addit_models):
				self.do_transition('get_experiment')
			# if more than one transitions available but one of them is stop_dev
			elif len([tr for tr in self.available_transitions() if tr['name'] != 'stop_development']) == 1:
				self.do_transition([tr for tr in self.available_transitions() if tr['name'] != 'stop_development'][0])
			else:
				raise ValueError("Overseer: run: none of the specified conditions triggered: current state: %s" % self.current_state)



class OverseerNoQuality(Overseer):
	def __init__(self, archive, rev_mod, exp_mod, oracle, threshold_addit_models):
		Overseer.__init__(self, archive, 'no ignoring') # w/o quality module ignoring shouldn't be used (no way to differentiate between models quality really)
		self.threshold_addit_models = threshold_addit_models
		self.transition_table = [
			{'name':'start_development', 'src':'start', 'dst':'models_tested_and_revised', 'method':self.start_development},
			{'name':'get_experiment', 'src':'models_tested_and_revised', 'dst':'experiment_ready', 'method':exp_mod.get_experiment},
			{'name':'get_experiment', 'src':'produced_additional_models', 'dst':'experiment_ready', 'method':exp_mod.get_experiment},
			{'name':'execute_experiment', 'src':'experiment_ready', 'dst':'has_new_result', 'method':oracle.execute_exps},# NewResults
			{'name':'record_result', 'src':'has_new_result', 'dst':'result_recorded', 'method':archive.record},# AcceptedResults
			{'name':'test_and_revise_models', 'src':'result_recorded', 'dst':'models_tested_and_revised', 'method':rev_mod.test_and_revise_all},
			{'name':'produce_additional_models', 'src':'models_tested_and_revised', 'dst':'produced_additional_models', 'method':rev_mod.produce_additional_models},
			{'name':'produce_additional_models', 'src':'produced_additional_models', 'dst':'produced_additional_models','method':rev_mod.produce_additional_models},
			{'name':'stop_development', 'src':'produced_additional_models', 'dst':'stop', 'method':self.stop_development},
			{'name':'stop_development', 'src':'experiment_ready', 'dst':'stop', 'method':self.stop_development}]

'do_check' 'checkpoint'


	def run(self, threshold_addit_models):
		while not (self.current_state == self.final_state):
			# if error: stop dev
			if self.archive.error_flag == True:
				self.do_transition('stop_development')
			# if only one transition available, do it
			elif len(self.available_transitions()) == 1:
				self.do_transition(self.available_transitions()[0]['method'])
			# if number of working models below thershold, then produce some more
			elif (self.current_state == 'models_tested_and_revised') and (len(self.archive.working_models) < threshold_addit_models):
				self.do_transition('produce_additional_models')
			elif (self.current_state == 'produced_additional_models') and (len(self.archive.working_models) < threshold_addit_models):
				self.do_transition('produce_additional_models')
			elif (self.current_state == 'models_tested_and_revised') and (len(self.archive.working_models) => threshold_addit_models):
				self.do_transition('get_experiment')
			elif (self.current_state == 'produced_additional_models') and (len(self.archive.working_models) => threshold_addit_models):
				self.do_transition('get_experiment')
			# if more than one transitions available but one of them is stop_dev
			elif len([tr for tr in self.available_transitions() if tr['name'] != 'stop_development']) == 1:
				self.do_transition([tr for tr in self.available_transitions() if tr['name'] != 'stop_development'][0])
			else:
				raise ValueError("Overseer: run: none of the specified conditions triggered: current state: %s" % self.current_state)


