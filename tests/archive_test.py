#! /usr/bin/env python3
# I, Robert Rozanski, the copyright holder of this work, release this work into the public domain. This applies worldwide. In some countries this may not be legally possible; if so: I grant anyone the right to use this work for any purpose, without any conditions, unless such conditions are required by law.

import unittest
from archive import Archive
import archive
import exp_repr
import mnm_repr

class ArchiveTest(unittest.TestCase):
	def setUp(self):
		self.archive = Archive()

	def test_record_ChosenExperiment(self):
		event = archive.ChosenExperiment('exp')
		self.archive.record(event)
		self.assertIn(event, self.archive.development_history)

	def test_record_Results(self):
		res = exp_repr.Experiment('res')
		event = archive.AcceptedResults(res)
		self.archive.record(event)
		self.assertIn(event, self.archive.development_history)
		self.assertIn(res, self.archive.known_results)

	def test_record_RefutedModels(self):
		mod = 'mod'
		self.archive.working_models.update([mod])
		event = archive.RefutedModels([mod])
		self.archive.record(event)
		self.assertIn(event, self.archive.development_history)
		self.assertNotIn(mod, self.archive.working_models)

	def test_record_RevisedModel(self):
		old = mnm_repr.Model(None, [1], [], [])
		new = mnm_repr.Model(None, [2], [], [])
		event = archive.RevisedModel(old, [new])
		self.archive.record(event)
		self.assertIn(event, self.archive.development_history)
		self.assertIn(new, self.archive.working_models)

	def test_record_AdditionalModels(self):
		mod1 = mnm_repr.Model(None, [1], [], [])
		mod2 = mnm_repr.Model(None, [2], [], [])
		event = archive.AdditionalModels([mod1,mod2])
		self.archive.record(event)
		self.assertIn(event, self.archive.development_history)
		self.assertIn(mod1, self.archive.working_models)
		self.assertIn(mod2, self.archive.working_models)

	def test_record_UpdatedModelQuality(self):
		event = archive.UpdatedModelQuality('mod', 1)
		self.archive.record(event)
		self.assertIn(event, self.archive.development_history)

	def test_record_InitialModels(self):
		mod1 = mnm_repr.Model(None, [1], [], [])
		mod2 = mnm_repr.Model(None, [2], [], [])
		event = archive.InitialModels([mod1, mod2])
		self.archive.record(event)
		self.assertIn(event, self.archive.development_history)
		self.assertIn(mod1, self.archive.working_models)
		self.assertIn(mod2, self.archive.working_models)

	def test_record_InitialResults(self):
		exp1 = exp_repr.Experiment('exp1')
		exp2 = exp_repr.Experiment('exp2')
		event = archive.InitialResults([exp1, exp2])
		self.archive.record(event)
		self.assertIn(event, self.archive.development_history)
		self.assertIn(exp1, self.archive.known_results)
		self.assertIn(exp2, self.archive.known_results)

	def test_record_TypeError(self):
		event = archive.Event
		self.assertRaises(TypeError, self.archive.record, event)

	def test_get_model_origin_event(self):
		mod1 = 'mod1'
		mod2 = 'mod2'
		exp1 = exp_repr.Experiment('exp1', ['res1'])
		exp2 = exp_repr.Experiment('exp2', ['res2'])
		adit = archive.AdditionalModels([mod1, mod2])
		self.archive.development_history.extend([adit, archive.NewResults(exp1), archive.NewResults(exp2)])
		origin_event = self.archive.get_model_origin_event(mod1)
		self.assertEqual(origin_event, adit)

	def test_get_events_after_event(self):
		mod1 = 'mod1'
		mod2 = 'mod2'
		exp1 = exp_repr.Experiment('exp1', ['res1'])
		exp2 = exp_repr.Experiment('exp2', ['res2'])
		res1 = archive.NewResults(exp1)
		res2 = archive.NewResults(exp2)
		self.archive.development_history.extend([archive.AdditionalModels([mod1, mod2]), res1, res2])
		origin_event = self.archive.get_model_origin_event(mod1)
		events = self.archive.get_events_after_event(origin_event)
		self.assertIn(res1, events)
		self.assertIn(res2, events)

	def test_get_results_after_model(self):
		mod1 = 'mod1'
		mod2 = 'mod2'
		exp1 = exp_repr.Experiment('exp1', ['res1'])
		exp2 = exp_repr.Experiment('exp2', ['res2'])
		self.archive.development_history.extend([archive.AdditionalModels([mod1, mod2]), archive.NewResults(exp1), archive.NewResults(exp2)])
		res = self.archive.get_results_after_model(mod1)
		self.assertIn('res1', res)
		self.assertIn('res2', res)
