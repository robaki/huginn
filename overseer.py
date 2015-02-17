#! /usr/bin/env python3

class Overseer:
	def __init__(self, rev_mod, qual_mod, exp_mod, oracle, archive):
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

		self.current_state = 'start'
		self.final_state = 'stop'



	def start_development(self):
		pass


	def stop_development(self):
		pass
