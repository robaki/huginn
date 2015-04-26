#! /usr/bin/env python3
# I, Robert Rozanski, the copyright holder of this work, release this work into the public domain. This applies worldwide. In some countries this may not be legally possible; if so: I grant anyone the right to use this work for any purpose, without any conditions, unless such conditions are required by law.

import unittest
from overseer import Overseer, OverseerWithModQuality, OverseerNoQuality

from mnm_repr import Model
from archive import Archive, CheckPointFail, NewResults, AcceptedResults, AdditionalModels, CheckPointSuccess
from revision_module import RevCAddB, RevCIAddR
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


	def test_do_check_ignoring_negative(self):
		mod = Model('m_0', [], [], [])
		archive = Archive()
		archive.working_models.append(mod)
		rev_mod = RevCIAddR(archive)
		exp_mod = BasicExpModuleNoCosts(archive, None)
		oracle = Oracle(archive, [], [], None, [], [], [])
		qual_mod = QualityModule(archive)
		overseer = OverseerWithModQuality(archive, rev_mod, exp_mod, oracle, 2, qual_mod, 2)
		overseer.cycles_since_last_new_model = 5
		overseer.cycles_since_best_model_changed = 5
		overseer.current_best_models = set([mod])
		before = list(overseer.archive.development_history)
		overseer.do_check()
		after = overseer.archive.development_history[-1]
		self.assertEqual(before, [])
		self.assertIsInstance(after, CheckPointFail)


	def test_do_check_noignoring_negative(self):
		before = list(self.overseer_qual.archive.development_history)
		self.overseer_qual.do_check()
		after = self.overseer_qual.archive.development_history[-1]
		self.assertEqual(before, [])
		self.assertIsInstance(after, CheckPointFail)


	def test_record_result_positive(self):
		self.overseer_qual.archive.development_history.append(NewResults([]))
		self.overseer_qual.record_result()
		after = self.overseer_qual.archive.development_history[-1]
		self.assertIsInstance(after, AcceptedResults)


	def test_record_result_error(self):
		self.overseer_qual.archive.development_history.append(1)
		self.assertRaises(TypeError, self.overseer_qual.record_result)


	def test_was_new_model_produced_since_last_check_positive(self):
		self.overseer_qual.archive.development_history.append(CheckPointSuccess())
		self.overseer_qual.archive.development_history.append(AdditionalModels([]))
		out = self.overseer_qual.was_new_model_produced_since_last_check()
		self.assertEqual(out, True)

	def test_was_new_model_produced_since_last_check_negative_one(self):
		self.overseer_qual.archive.development_history.append(CheckPointSuccess())
		out = self.overseer_qual.was_new_model_produced_since_last_check()
		self.assertEqual(out, False)

	def test_was_new_model_produced_since_last_check_negative_two(self):
		out = self.overseer_qual.was_new_model_produced_since_last_check()
		self.assertEqual(out, False)

	def test_did_the_best_model_change_since_last_check_positive(self):
		mod = Model('m_0', [], [], [])
		self.overseer_qual.archive.working_models.append(mod)
		out = self.overseer_qual.did_the_best_model_change_since_last_check()
		self.assertEqual(out, True)

	def test_did_the_best_model_change_since_last_check_negative(self):
		mod = Model('m_0', [], [], [])
		self.overseer_qual.archive.working_models.append(mod)
		self.overseer_qual.current_best_models = set([mod])
		out = self.overseer_qual.did_the_best_model_change_since_last_check()
		self.assertEqual(out, False)



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


