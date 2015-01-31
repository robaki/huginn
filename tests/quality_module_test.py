#! /usr/bin/env python3

import unittest
from archive import Archive, Results, AdditionalModels
from mnm_repr import Model
from exp_repr import Result, Experiment
from quality_module import NumberAllCovered, NumberAllCoveredMinusIgnored, NumberNewCovered, NumberNewCoveredMinusIgnored

class QualityModuleTest(unittest.TestCase):
	def setUp(self):
		self.archive = Archive()
		res1 = Result('res1', None, None)
		res2 = Result('res2', None, None)
		res3 = Result('res3', None, None)
		res4 = Result('res4', None, None)
		exp1 = Experiment('exp1', [res1])
		exp2 = Experiment('exp2', [res2])
		exp3 = Experiment('exp3', [res3])
		exp4 = Experiment('exp4', [res4])
		r1 = Results(exp1)
		r2 = Results(exp2)
		r3 = Results(exp3)
		r4 = Results(exp4)

		self.mod1 = Model('id1', ['m1'], [], [])
		self.mod1.ignored_results = frozenset([res3])
		self.mod1.results_covered = frozenset([res1, res4])

		self.mod2 = Model('id2', ['m2'], [], [])
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

	def test_NumberAllCovered(self):
		q = NumberAllCovered(self.archive)
		q.check_and_update_qualities()
		self.assertEqual(self.mod1.quality, 2)
		self.assertEqual(self.mod2.quality, 3)

	def test_NumberAllCoveredMinusIgnored(self):
		q = NumberAllCoveredMinusIgnored(self.archive)
		q.check_and_update_qualities()
		self.assertEqual(self.mod1.quality, 1)
		self.assertEqual(self.mod2.quality, 2)

	def test_NumberNewCovered(self):
		q = NumberNewCovered(self.archive)
		q.check_and_update_qualities()
		self.assertEqual(self.mod1.quality, 1)
		self.assertEqual(self.mod2.quality, 2)

	def test_NumberNewCoveredMinusIgnored(self):
		q = NumberNewCoveredMinusIgnored(self.archive)
		q.check_and_update_qualities()
		self.assertEqual(self.mod1.quality, 1)
		self.assertEqual(self.mod2.quality, 2)

