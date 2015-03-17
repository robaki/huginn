#! /usr/bin/env python3

from sys import stdout
import pickle
from time import gmtime, time
from archive import CheckPointFail, CheckPointSuccess, RevisedModel, AdditionalModels, AcceptedResults, NewResults
from revision_module import RevCIAddB, RevCIAddR, RevCAddB, RevCAddR

class Overseer:
	def __init__(self, archive, checkpoint, stop_threshold, max_numb_cycles, max_time, suffix):
		self.archive = archive
		self.checkpoint_version = checkpoint
		self.stop_threshold = stop_threshold
		self.max_numb_cycles = max_numb_cycles
		self.max_time = max_time # number of hours
		self.current_state = 'start'
		self.final_state = 'stop'
		self.cycles_since_last_new_model = 0
		self.cycles_since_best_model_changed = 0
		self.current_best_models = None
		self.cycles_counter = 0
		self.suffix = suffix

	def time_passed_check(self):
		# number of hours since init of archive till now
		# returns True if smaller than max_time; False otherwise
		# False stops model development
		return ((time() - self.archive.start_time)/3600) < self.max_time


	def start_development(self):
		print('starting development: %s' % self.suffix)
		stdout.flush()
		self.do_transition('test_and_revise_models')


	def stop_development(self):
		current_time = gmtime()
		time_stamp = '_'.join([str(x) for x in [current_time[0], current_time[1], current_time[2], current_time[3], current_time[4], current_time[5]]])
		file_path = ('pickled_archives/archive_%s_%s' % (time_stamp, self.suffix))
		pkl_file = open(file_path, 'wb')
		pickle.dump(self.archive, pkl_file)
		pkl_file.close()
		print('error flags?: %s' % self.archive.error_flag)
		print('run out of time: %s' % (not self.time_passed_check()))
		print('run out of cycles: %s' % (self.cycles_counter >= self.max_numb_cycles))
		stdout.flush()


	def do_check(self):
		if self.checkpoint_version == 'ignoring':
			self.was_new_model_produced_since_last_check()
			self.did_the_best_model_change_since_last_check()
			if ((self.cycles_since_last_new_model >= self.stop_threshold) and (self.cycles_since_best_model_changed >= self.stop_threshold)):
				self.archive.record(CheckPointFail('ignoring'))
			else:
				self.archive.record(CheckPointSuccess())
				self.cycles_counter += 1 # development process enters another cycle
				print('starting cycle: %s' % self.cycles_counter)
				print('time elapsed: %s h' % ((time() - self.archive.start_time)/3600))
				stdout.flush()
			
		else: # no ignoring
			if len(self.archive.working_models) <= 1: # one model left
				self.archive.record(CheckPointFail('no ignoring'))
			else:
				self.archive.record(CheckPointSuccess())
				print('starting cycle: %s' % self.cycles_counter)
				print('time elapsed: %s h' % ((time() - self.archive.start_time)/3600))
				stdout.flush()
				self.cycles_counter += 1 # development process enters another cycle


	def record_result(self):
		last_event = self.archive.development_history[-1]
		if isinstance(last_event, NewResults):
			self.archive.record(AcceptedResults(last_event.experiment))
		else:
			raise TypeError("record_result: unexpected type of the last event: %s" % type(last_event))


	def do_transition(self, transition_name):
		tran_dict = [tr for tr in self.available_transitions() if tr['name'] == transition_name]
		if len(tran_dict) > 1: # sanity check
			print([x for x in tran_dict])
			raise ValueError("do_transition: more than one transition of the same name available: %s" % tran_dict)
		elif len(tran_dict) == 0: # sanity check:
			raise ValueError("do_transition: no matching transitions available: %s" % transition_name)
		else:
			tran_dict[0]['method']() # execute
			self.current_state = tran_dict[0]['dst']# update state


	def available_transitions(self):
		output = [x for x in self.transition_table if (self.current_state == x['src'])] # whole dict
		return output


	def was_new_model_produced_since_last_check(self):
		for event in self.archive.development_history[::-1]:
			if (isinstance(event, RevisedModel) or isinstance(event, AdditionalModels)):
				self.cycles_since_last_new_model = 0
				return True
			elif isinstance(event, CheckPointSuccess):
				self.cycles_since_last_new_model += 1
				return False
			else:
				pass
		return False # if nothing found


	def did_the_best_model_change_since_last_check(self):# checks set: could be best models
		dic = {mod:mod.quality for mod in self.archive.working_models} # {x: x**2 for x in (2, 4, 6)}
		max_quality = max(dic.values())
		best_models = set([mod for mod in dic if (dic[mod] == max_quality)])
		if self.current_best_models == best_models:
			self.cycles_since_best_model_changed += 1
			return False
		else:
			self.cycles_since_best_model_changed = 0
			self.current_best_models = best_models
			return True





class OverseerWithModQuality(Overseer):
	def __init__(self, archive, rev_mod, exp_mod, oracle, threshold_addit_models, qual_mod, max_numb_cycles, max_time, suffix, stop_threshold=None):
		if (isinstance(rev_mod, RevCIAddB) or isinstance(rev_mod, RevCIAddR)):
			checkpoint = 'ignoring'
		elif (isinstance(rev_mod, RevCAddB) or isinstance(rev_mod, RevCAddR)):
			checkpoint = 'no ignoring'
		else:
			raise ValueError("overseer __init__: revision module type not recognised: %s" % type(rev_mod))
		Overseer.__init__(self, archive, checkpoint, stop_threshold, max_numb_cycles, max_time, suffix)
		self.threshold_addit_models = threshold_addit_models
		self.transition_table = [
			{'name':'start_development', 'src':'start', 'dst':'models_tested_and_revised', 'method':self.start_development},
			{'name':'get_experiment', 'src':'checkpoint', 'dst':'experiment_ready', 'method':exp_mod.get_experiment},###
			{'name':'execute_experiment', 'src':'experiment_ready', 'dst':'has_new_result', 'method':oracle.execute_exps},# NewResults
			{'name':'record_result', 'src':'has_new_result', 'dst':'result_recorded', 'method':self.record_result},# AcceptedResults
			{'name':'test_and_revise_models', 'src':'start', 'dst':'models_tested_and_revised', 'method':rev_mod.test_and_revise_all},
			{'name':'test_and_revise_models', 'src':'result_recorded', 'dst':'models_tested_and_revised', 'method':rev_mod.test_and_revise_all},
			{'name':'do_check', 'src':'quality_recalculated', 'dst':'checkpoint', 'method':self.do_check},
			{'name':'produce_additional_models', 'src':'quality_recalculated', 'dst':'produced_additional_models', 'method':rev_mod.produce_additional_models},
			{'name':'recalculate_models_quality', 'src':'models_tested_and_revised', 'dst':'quality_recalculated', 'method':qual_mod.check_and_update_qualities},
			{'name':'recalculate_models_quality', 'src':'produced_additional_models', 'dst':'quality_recalculated', 'method':qual_mod.check_and_update_qualities},
			{'name':'stop_development', 'src':'checkpoint', 'dst':'stop', 'method':self.stop_development},###
			{'name':'stop_development', 'src':'experiment_ready', 'dst':'stop', 'method':self.stop_development}]


	def run(self):
		try:
			while (self.current_state != self.final_state):
				# if error or thresholds met: stop dev
				if self.archive.error_flag == True:
					self.stop_development()
					self.current_state = 'stop'
				elif self.cycles_counter >= self.max_numb_cycles:
					self.stop_development()
					self.current_state = 'stop'
				elif not self.time_passed_check():
					self.stop_development()
					self.current_state = 'stop'
				# if only one transition available, do it
				elif len(self.available_transitions()) == 1:
					self.do_transition(self.available_transitions()[0]['name'])
				# if number of working models below threshold, then produce some more
				elif self.cond_1():
					self.do_transition('produce_additional_models')
				elif self.cond_2():
					self.do_transition('do_check')
				# if more than one transitions available but one of them is stop_dev
				elif len([tr for tr in self.available_transitions() if tr['name'] != 'stop_development']) == 1:
					self.do_transition([tr['name'] for tr in self.available_transitions() if tr['name'] != 'stop_development'][0])
				elif self.current_state == 'start':
					self.do_transition('start_development')
				else:
					raise ValueError("Overseer: run: none of the specified conditions triggered: current state: %s" % self.current_state)

		except Exception as e:
			self.stop_development()
			self.current_state = 'stop'
			print(e)
			stdout.flush()


	def cond_1(self):
		if not (self.current_state == 'quality_recalculated'):
			return False
		elif not (len(self.archive.working_models) < self.threshold_addit_models):
			return False
		elif not (self.archive.revflag == False):
			return False
		else:
			return True


	def cond_2(self):
		if (self.archive.revflag == True):
			return True
		elif not (len(self.archive.working_models) >= self.threshold_addit_models):
			return False
		elif not (self.current_state == 'quality_recalculated'):
			return False
		else:
			return True



class OverseerNoQuality(Overseer):
	def __init__(self, archive, rev_mod, exp_mod, oracle, threshold_addit_models, max_numb_cycles, max_time, suffix, stop_threshold=None):
		Overseer.__init__(self, archive, 'no ignoring', stop_threshold, max_numb_cycles, max_time, suffix) # w/o quality module ignoring shouldn't be used
		self.threshold_addit_models = threshold_addit_models
		self.transition_table = [
			{'name':'start_development', 'src':'start', 'dst':'models_tested_and_revised', 'method':self.start_development},
			{'name':'get_experiment', 'src':'checkpoint', 'dst':'experiment_ready', 'method':exp_mod.get_experiment},
			{'name':'execute_experiment', 'src':'experiment_ready', 'dst':'has_new_result', 'method':oracle.execute_exps},# NewResults
			{'name':'record_result', 'src':'has_new_result', 'dst':'result_recorded', 'method':self.record_result},# AcceptedResults
			{'name':'test_and_revise_models', 'src':'start', 'dst':'models_tested_and_revised', 'method':rev_mod.test_and_revise_all},
			{'name':'test_and_revise_models', 'src':'result_recorded', 'dst':'models_tested_and_revised', 'method':rev_mod.test_and_revise_all},
			{'name':'produce_additional_models', 'src':'models_tested_and_revised', 'dst':'produced_additional_models', 'method':rev_mod.produce_additional_models},
			{'name':'produce_additional_models', 'src':'produced_additional_models', 'dst':'produced_additional_models','method':rev_mod.produce_additional_models},
			{'name':'do_check', 'src':'models_tested_and_revised', 'dst':'checkpoint', 'method':self.do_check},
			{'name':'do_check', 'src':'produced_additional_models', 'dst':'checkpoint', 'method':self.do_check},
			{'name':'stop_development', 'src':'checkpoint', 'dst':'stop', 'method':self.stop_development},
			{'name':'stop_development', 'src':'experiment_ready', 'dst':'stop', 'method':self.stop_development}]


	def run(self):
		try:
			while (self.current_state != self.final_state):
				# if error or thresholds met: stop dev
				if self.archive.error_flag == True:
					self.stop_development()
					self.current_state = 'stop'
				elif self.cycles_counter >= self.max_numb_cycles:
					self.stop_development()
					self.current_state = 'stop'
				elif not self.time_passed_check():
					self.stop_development()
					self.current_state = 'stop'
				# if only one transition available, do it
				elif len(self.available_transitions()) == 1:
					self.do_transition(self.available_transitions()[0]['method'])
				# if number of working models below thershold, then produce some more
				elif self.cond_1():
					self.do_transition('produce_additional_models')
				elif self.cond_2():
					self.do_transition('produce_additional_models')
				elif self.cond_3():
					self.do_transition('do_check')
				elif self.cond_4():
					self.do_transition('do_check')
				# if more than one transitions available but one of them is stop_dev
				elif len([tr for tr in self.available_transitions() if tr['name'] != 'stop_development']) == 1:
					self.do_transition([tr for tr in self.available_transitions() if tr['name'] != 'stop_development'][0])
				else:
					raise ValueError("Overseer: run: none of the specified conditions triggered: current state: %s" % self.current_state)

		except Exception:
			self.stop_development()
			self.current_state = 'stop'
			raise Exception # raise exception here? or somehow print it and move on with the next test case...!



	def cond_1(self):
		if not (self.current_state == 'models_tested_and_revised'):
			return False
		elif not (len(self.archive.working_models) < self.threshold_addit_models):
			return False
		elif not (self.archive.revflag == False):
			return False
		else:
			return True


	def cond_2(self):
		if not (self.current_state == 'produced_additional_models'):
			return False
		elif not (len(self.archive.working_models) < self.threshold_addit_models):
			return False
		elif not (self.archive.revflag == False):
			return False
		else:
			return True


	def cond_3(self):
		if (self.archive.revflag == True):
			return True
		elif not (len(self.archive.working_models) >= self.threshold_addit_models):
			return False
		elif not (self.current_state == 'models_tested_and_revised'):
			return False
		else:
			return True


	def cond_4(self):
		if (self.archive.revflag == True):
			return True
		elif not (len(self.archive.working_models) >= self.threshold_addit_models):
			return False
		elif not (self.current_state == 'produced_additional_models'):
			return False
		else:
			return True
