#! /usr/bin/env python3

import unittest
from oracle import Oracle
from exp_repr import DetectionEntity, LocalisationEntity, DetectionActivity, AdamTwoFactorExperiment, ReconstructionActivity, ReconstructionEnzReaction, ReconstructionTransporterRequired, ExperimentDescription, Result
from mnm_repr import Gene, Metabolite, Protein, Complex, Growth, Reaction, PresentEntity, Cytosol, Add, Remove, Medium, CellMembrane, Model, PresentCatalyst, PresentTransporter, Catalyses, Transports

class OracleTest(unittest.TestCase):
	def setUp(self):
		self.g1 = Gene('g1')
		self.p1 = Protein('p1')
		self.met1 = Metabolite('met1')
		self.met2 = Metabolite('met2')
		self.cplx1 = Complex('cplx1')
		self.cytosol = Cytosol()

		self.cond1 = PresentEntity(self.met1, self.cytosol)
		self.cond2 = PresentEntity(self.met2, self.cytosol)
		self.cond3 = PresentEntity(self.p1, self.cytosol)
		self.cond4 = PresentEntity(self.cplx1, self.cytosol)

		self.growth = Growth('growth', [self.cond2])
		self.r1 = Reaction('r1', [self.cond1], [self.cond2])
		self.r2 = Reaction('r2', [self.cond3], [self.cond4])

		self.entities = [self.g1, self.p1, self.met1, self.met2, self.cplx1]
		self.compartments = [self.cytosol]
		self.activities = [self.growth, self.r1, self.r2]
		self.setup_conds = [self.cond1, self.cond3]

		self.mod1 = Model('m0', self.setup_conds, [self.growth, self.r1], [])
		self.mod2 = Model('m1', self.setup_conds, [self.growth, self.r2], [])

		self.oracle = Oracle([], [], self.mod1, self.entities, self.compartments, self.activities)


	def tearDown(self):
		self.oracle = None


	def test_in_vitro_basic(self):
		met1 = Metabolite('met1')
		met2 = Metabolite('met2')
		cytosol = Cytosol()
		cond1 = PresentEntity(met1, cytosol)
		cond2 = PresentEntity(met2, cytosol)
		r1 = Reaction('r1', [cond1], [cond2])
		self.oracle = Oracle([], [r1], None, [], [], [])
		expD = ExperimentDescription(ReconstructionActivity('r1'), [])
		out = self.oracle.execute_in_vitro_exps(expD)
		self.assertEqual(out.outcome, True)


	def test_in_vitro_enz(self):
		met1 = Metabolite('met1')
		met2 = Metabolite('met2')
		cytosol = Cytosol()
		cond1 = PresentEntity(met1, cytosol)
		cond2 = PresentEntity(met2, cytosol)
		cond_enz = PresentCatalyst(cytosol)
		r1 = Reaction('r1', [cond1, cond_enz], [cond2])
		enz = Protein('p1', properties=[Catalyses(r1)])
		self.oracle = Oracle([enz], [r1], None, [], [], [])
		expD = ExperimentDescription(ReconstructionEnzReaction('r1', 'p1'), [])
		out = self.oracle.execute_in_vitro_exps(expD)
		self.assertEqual(out.outcome, True)


	def test_in_vitro_transp(self):
		met1 = Metabolite('met1')
		met2 = Metabolite('met2')
		cytosol = Cytosol()
		cond1 = PresentEntity(met1, cytosol)
		cond2 = PresentEntity(met2, cytosol)
		cond_trp = PresentTransporter(cytosol)
		r1 = Reaction('r1', [cond1, cond_trp], [cond2])
		transp = Protein('p1', properties=[Transports(r1)])
		self.oracle = Oracle([transp], [r1], None, [], [], [])
		expD = ExperimentDescription(ReconstructionTransporterRequired('r1', 'p1'), [])
		out = self.oracle.execute_in_vitro_exps(expD)
		self.assertEqual(out.outcome, True)


	def test_in_vivo(self):
		expD = ExperimentDescription(DetectionActivity('r1'), [])
		res = self.oracle.execute_in_vivo(expD)
		self.assertEqual(res.outcome, True)


	def test_process_output_ent_detection_1(self):
		expD = ExperimentDescription(DetectionEntity('met1'), [])
		out = 'Answer: 1\nsynthesizable(met1,ver,c_05,m0)'
		res = self.oracle.process_output(out, expD)
		self.assertEqual(res.outcome, True)


	def test_process_output_localisation_ent_1(self):
		expD = ExperimentDescription(LocalisationEntity('met1', 'c_05'), [])
		out = 'Answer: 1\nsynthesizable(met1,ver,c_05,m0)'
		res = self.oracle.process_output(out, expD)
		self.assertEqual(res.outcome, True)


	def test_process_output_ent_detection_2(self):
		expD = ExperimentDescription(DetectionEntity('met1'), [])
		out = 'Answer: 1\ninitially_present(met1,ver,c_05,m0)'
		res = self.oracle.process_output(out, expD)
		self.assertEqual(res.outcome, True)


	def test_process_output_localisation_ent_2(self):
		expD = ExperimentDescription(LocalisationEntity('met1', 'c_05'), [])
		out = 'Answer: 1\ninitially_present(met1,ver,c_05,m0)'
		res = self.oracle.process_output(out, expD)
		self.assertEqual(res.outcome, True)


	def test_process_output_act_detection(self):
		expD = ExperimentDescription(DetectionActivity('r1'), [])
		out = 'Answer: 1\nactive(r1,m0)'
		res = self.oracle.process_output(out, expD)
		self.assertEqual(res.outcome, True)


	def test_process_output_adam_two_factor(self):
		expD = ExperimentDescription(AdamTwoFactorExperiment('g1', 'met1'), [])
		out = 'Answer: 1\npredicts(m0,experiment(adam_two_factor_exp,g1,met1),true'
		res = self.oracle.process_output(out, expD)
		self.assertEqual(res.outcome, True)
