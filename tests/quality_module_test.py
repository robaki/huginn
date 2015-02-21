#! /usr/bin/env python3

import unittest
from archive import Archive, NewResults, AdditionalModels
from mnm_repr import Model
from exp_repr import Result, Experiment, ExperimentDescription, DetectionEntity
from quality_module import AllCovered, AllCoveredMinusIgnored, NewCovered, NewCoveredMinusIgnored

class QualityModuleTest(unittest.TestCase):
	def setUp(self):
		self.archive = Archive()
		exd = ExperimentDescription(DetectionEntity(None))
		res1 = Result('res_0', exd, None)
		res2 = Result('res_1', exd, None)
		res3 = Result('res_2', exd, None)
		res4 = Result('res_3', exd, None)
		exp1 = Experiment('exp_0', [res1])
		exp2 = Experiment('exp_1', [res2])
		exp3 = Experiment('exp_2', [res3])
		exp4 = Experiment('exp_3', [res4])
		r1 = NewResults(exp1)
		r2 = NewResults(exp2)
		r3 = NewResults(exp3)
		r4 = NewResults(exp4)

		self.mod1 = Model('m_0', [1], [], [])
		self.mod1.ignored_results = frozenset([res3])
		self.mod1.results_covered = frozenset([res1, res4])

		self.mod2 = Model('m_1', [2], [], [])
		self.mod2.ignored_results = frozenset([res3])
		self.mod2.results_covered = frozenset([res1, res2, res4])

		m = AdditionalModels([self.mod1, self.mod2])

		self.archive.record(r1)
		self.archive.record(m)
		self.archive.record(r2)
		self.archive.record(r3)
		self.archive.record(r4)

	def tearDown(self):
		self.archive = None
		self.mod1 = None
		self.mod2 = None

	def test_AllCovered(self):
		q = AllCovered(self.archive)
		q.check_and_update_qualities()
		self.assertEqual(self.mod1.quality, 2)
		self.assertEqual(self.mod2.quality, 3)

	def test_AllCoveredMinusIgnored(self):
		q = AllCoveredMinusIgnored(self.archive)
		q.check_and_update_qualities()
		self.assertEqual(self.mod1.quality, 1)
		self.assertEqual(self.mod2.quality, 2)

	def test_NewCovered(self):
		q = NewCovered(self.archive)
		q.check_and_update_qualities()
		self.assertEqual(self.mod1.quality, 1)
		self.assertEqual(self.mod2.quality, 2)

	def test_NewCoveredMinusIgnored(self):
		q = NewCoveredMinusIgnored(self.archive)
		q.check_and_update_qualities()
		self.assertEqual(self.mod1.quality, 1)
		self.assertEqual(self.mod2.quality, 2)

