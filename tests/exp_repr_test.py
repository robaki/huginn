#! /usr/bin/env python3

import unittest
import exp_repr

class ExperimentTypeTest(unittest.TestCase):

	def init_test(self):
		self.exptype = exp_repr.ExperimentType()
		self.assertEqual(self.exptype.base_cost, None)


class ReconstructionActivityTest(unittest.TestCase):

	def init_test(self):
		self.exp = exp_repr.ReconstructionActivity('activity')
		self.assertEqual(self.exp.activity, 'activity')


class ReconstructionEnzReactionTest(unittest.TestCase):

	def init_test(self):
		self.exp = exp_repr.ReconstructionEnzReaction('reaction', 'enzyme')
		self.assertEqual(self.exp.reaction, 'reaction')
		self.assertEqual(self.exp.enzyme, 'enzyme')


class ReconstructionTransporterRequiredTest(unittest.TestCase):

	def init_test(self):
		self.exp = exp_repr.ReconstructionTransporterRequired('transport', 'transporter')
		self.assertEqual(self.exp.transport_activity, 'transport')
		self.assertEqual(self.exp.transporter, 'transporter')



class DetectionActivityTest(unittest.TestCase):

	def init_test(self):
		self.exp = exp_repr.DetectionActivity('activity')
		self.assertEqual(self.exp.activity, 'activity')


class DetectionEntityTest(unittest.TestCase):

	def init_test(self):
		self.exp = exp_repr.DetectionEntity('entity')
		self.assertEqual(self.exp.entity, 'entity')


class LocalisationEntityTest(unittest.TestCase):

	def init_test(self):
		self.exp = exp_repr.LocalisationEntity('entity')
		self.assertEqual(self.exp.entity, 'entity')


class ExperimentDescriptionTest(unittest.TestCase):

	def init_test(self):
		interv_list = [0,1,2,3]
		self.exp = exp_repr.ExperimentDescription('exp_type', interv_list)
		self.assertEqual(self.exp.experiment_type, 'exp_type')
		self.assertEqual(self.exp.status, 'Active')
		self.assertEqual(self.exp.interventions, interv_list)
		self.assertIsNot(self.exp.interventions, interv_list)


class ResultTest(unittest.TestCase):

	def init_test(self):
		self.exp = exp_repr.Result('exp_description', 'outcome')
		self.assertEqual(self.exp.exp_description, 'exp_description')
		self.assertEqual(self.exp.outcome, 'outcome')


class ExperimentTest(unittest.TestCase):

	def init_test(self):
		results = [0,1,2,3]
		self.exp = exp_repr.Experiment('ID', results)
		self.assertEqual(self.exp.ID, 'ID')
		self.assertEqual(self.exp.results, results)
		self.assertIsNot(self.exp.results, results)
