#! /usr/bin/env python3

import unittest
from overseer import Overseer, OverseerWithModQuality, OverseerNoQuality

from archive import Archive
from revision_module import RevCAddB
from experiment_module import BasicExpModuleNoCosts
from oracle import Oracle
from quality_module import QualityModule


class OverseerTest(unittest.TestCase):
	def setUp(self):
		archive = Archive()
		rev_mod = RevCAddB(archive)
		exp_mod = BasicExpModuleNoCosts(archive, None)
		oracle = Oracle(archive, [], [], None, [], [], [])
		qual_mod = QualityModule(archive)
		stop_threshold = 2
		self.overseer_qual = OverseerWithModQuality(archive, rev_mod, exp_mod, oracle, 2, qual_mod, stop_threshold)
		self.overseer_no_qual = OverseerNoQuality(archive, rev_mod, exp_mod, oracle, 2, stop_threshold)


	def test_available_transitions(self):
		self.overseer_qual.current_state = 'quality_recalculated'
		self.overseer_no_qual.current_state = 'models_tested_and_revised'
		qual_av = self.overseer_qual.available_transitions()
		no_qual_av = self.overseer_no_qual.available_transitions()
		self.assertEqual(len(qual_av), 2)
		self.assertEqual(len(no_qual_av), 2)


	def test_do_transition(self):
		state_before = self.overseer_qual.current_state
		self.overseer_qual.do_transition('start_development')
		state_after = self.overseer_qual.current_state
		self.assertEqual(state_before, 'start')
		self.assertEqual(state_after, 'models_tested_and_revised')


#	def test_stop_development(self):# TESTED BUT SHOULDN'T BE PART OF THE SUIT
#		self.overseer_qual.stop_development()


	def test_do_check_ignoring(self):
		


#	def test_do_check_noignoring(self):



#	def test_record_result(self):



#	def test_was_new_model_produced_since_last_check_positive(self):



#	def test_was_new_model_produced_since_last_check_negative(self):



#	def test_did_the_best_model_change_since_last_check_positive(self):



#	def test_did_the_best_model_change_since_last_check_negative(self):




#	def test_cond_1_with_qual_positive(self):

#	def test_cond_1_with_qual_negative(self):

#	def test_cond_2_with_qual_positive(self):

#	def test_cond_2_with_qual_negative(self):

#	def test_cond_1_positive(self): # no qual

#	def test_cond_1_negative(self): # no qual

#	def test_cond_2_positive(self): # no qual

#	def test_cond_2_negative(self): # no qual

#	def test_cond_3_positive(self): # no qual

#	def test_cond_3_negative(self): # no qual

#	def test_cond_4_positive(self): # no qual

#	def test_cond_4_negative(self): # no qual


