#! /usr/bin/env python3

import unittest
import mnm_repr

class ElementTest(unittest.TestCase):

	def setUp(self):
		self.element = mnm_repr.Element('ID', 'name')

	def tearDown(self):
		self.element = None

	def test_attributes(self):
		self.assertEqual(self.element.ID, 'ID')
		self.assertEqual(self.element.name, 'name')


class EntityTest(unittest.TestCase):

	def tearDown(self):
		self.entity = None

	def test_with_properties(self):
		property_list = [1,2,3,4]
		self.entity = mnm_repr.Entity('ID', 'name', 0, property_list)
		self.assertEqual(self.entity.ID, 'ID')
		self.assertEqual(self.entity.name, 'name')
		self.assertEqual(self.entity.version, 0)
		self.assertEqual(self.entity.properties, property_list)
		self.assertIsNot(self.entity.properties, property_list)
		self.assertEqual(self.entity.add_cost, None)
		self.assertEqual(self.entity.remove_cost, None)
		self.assertEqual(self.entity.detection_cost, None)
		self.assertEqual(self.entity.localisation_cost, None)

	def test_no_properties(self):
		property_list = []
		self.entity = mnm_repr.Entity('ID', 'name', 0, property_list)
		self.assertEqual(self.entity.properties, property_list)
		self.assertIsNot(self.entity.properties, property_list)


class GeneTest(unittest.TestCase):

	def tearDown(self):
		self.gene = None

	def test_default_values(self):
		property_list = []
		self.gene = mnm_repr.Gene('ID')
		self.assertEqual(self.gene.ID, 'ID')
		self.assertEqual(self.gene.name, None)
		self.assertEqual(self.gene.version, None)
		self.assertEqual(self.gene.properties, property_list)
		self.assertIsNot(self.gene.properties, property_list)

	def test_non_default_values(self):
		property_list = [1,2,3]
		self.gene = mnm_repr.Gene('ID', 'name', 0, property_list)
		self.assertEqual(self.gene.ID, 'ID')
		self.assertEqual(self.gene.name, 'name')
		self.assertEqual(self.gene.version, 0)
		self.assertEqual(self.gene.properties, property_list)
		self.assertIsNot(self.gene.properties, property_list)


class MetaboliteTest(unittest.TestCase):

	def tearDown(self):
		self.metabolite = None

	def test_default_values(self):
		property_list = []
		self.metabolite = mnm_repr.Metabolite('ID')
		self.assertEqual(self.metabolite.ID, 'ID')
		self.assertEqual(self.metabolite.name, None)
		self.assertEqual(self.metabolite.version, None)
		self.assertEqual(self.metabolite.properties, property_list)
		self.assertIsNot(self.metabolite.properties, property_list)

	def test_non_default_values(self):
		property_list = [1,2,3]
		self.metabolite = mnm_repr.Metabolite('ID', 'name', 0, property_list)
		self.assertEqual(self.metabolite.ID, 'ID')
		self.assertEqual(self.metabolite.name, 'name')
		self.assertEqual(self.metabolite.version, 0)
		self.assertEqual(self.metabolite.properties, property_list)
		self.assertIsNot(self.metabolite.properties, property_list)


class ProteinTest(unittest.TestCase):

	def tearDown(self):
		self.protein = None

	def test_default_values(self):
		property_list = []
		self.protein = mnm_repr.Protein('ID')
		self.assertEqual(self.protein.ID, 'ID')
		self.assertEqual(self.protein.name, None)
		self.assertEqual(self.protein.version, None)
		self.assertEqual(self.protein.properties, property_list)
		self.assertIsNot(self.protein.properties, property_list)

	def test_non_default_values(self):
		property_list = [1,2,3]
		self.protein = mnm_repr.Protein('ID', 'name', 0, property_list)
		self.assertEqual(self.protein.ID, 'ID')
		self.assertEqual(self.protein.name, 'name')
		self.assertEqual(self.protein.version, 0)
		self.assertEqual(self.protein.properties, property_list)
		self.assertIsNot(self.protein.properties, property_list)


class ComplexTest(unittest.TestCase):

	def tearDown(self):
		self.complex = None

	def test_default_values(self):
		property_list = []
		self.complex = mnm_repr.Complex('ID')
		self.assertEqual(self.complex.ID, 'ID')
		self.assertEqual(self.complex.name, None)
		self.assertEqual(self.complex.version, None)
		self.assertEqual(self.complex.properties, property_list)
		self.assertIsNot(self.complex.properties, property_list)

	def test_non_default_values(self):
		property_list = [1,2,3]
		self.complex = mnm_repr.Complex('ID', 'name', 0, property_list)
		self.assertEqual(self.complex.ID, 'ID')
		self.assertEqual(self.complex.name, 'name')
		self.assertEqual(self.complex.version, 0)
		self.assertEqual(self.complex.properties, property_list)
		self.assertIsNot(self.complex.properties, property_list)


class ActivityTest(unittest.TestCase):

	def test_activity(self):
		self.activity = mnm_repr.Activity('ID', 'name')
		self.assertEqual(self.activity.ID, 'ID')
		self.assertEqual(self.activity.name, 'name')
		self.assertEqual(self.activity.detection_cost, None)


class GrowthTest(unittest.TestCase):

	def tearDown(self):
		self.growth = None

	def test_default_values(self):
		conditions = []
		self.growth = mnm_repr.Growth(conditions, 'ID')
		self.assertEqual(self.growth.required_conditions, conditions)
		self.assertIsNot(self.growth.required_conditions, conditions)
		self.assertEqual(self.growth.ID, 'ID')

class ExpressionTest(unittest.TestCase):

	def tearDown(self):
		self.expression = None

	def test_default_values(self):
		conditions = []
		self.expression = mnm_repr.Expression('gene', conditions, 'ID')
		self.assertEqual(self.expression.coding_gene, 'gene')
		self.assertIsNot(self.expression.product_conditions, conditions)
		self.assertEqual(self.expression.product_conditions, conditions)
		self.assertEqual(self.expression.ID, 'ID')


class NonEnzymaticReactionTest(unittest.TestCase):

	def tearDown(self):
		self.nonenzymaticreaction = None

	def test_default_values(self):
		substrates = []
		products = []
		self.nonenzymaticreaction = mnm_repr.NonEnzymaticReaction(substrates, products, 'ID')
		self.assertEqual(self.nonenzymaticreaction.substrates, substrates)
		self.assertIsNot(self.nonenzymaticreaction.substrates, substrates)
		self.assertEqual(self.nonenzymaticreaction.products, products)
		self.assertIsNot(self.nonenzymaticreaction.products, products)
		self.assertEqual(self.nonenzymaticreaction.ID, 'ID')


class EnzymaticReactionTest(unittest.TestCase):

	def tearDown(self):
		self.enzymaticreaction = None

	def test_default_values(self):
		substrates = []
		products = []
		self.enzymaticreaction = mnm_repr.EnzymaticReaction(substrates, products, 'ID')
		self.assertEqual(self.enzymaticreaction.substrates, substrates)
		self.assertIsNot(self.enzymaticreaction.substrates, substrates)
		self.assertEqual(self.enzymaticreaction.products, products)
		self.assertIsNot(self.enzymaticreaction.products, products)
		self.assertEqual(self.enzymaticreaction.ID, 'ID')

class TransporterNotRequiredTest(unittest.TestCase):

	def tearDown(self):
		self.transporternotrequired = None

	def test_default_values(self):
		src_conds = []
		dest_conds = []
		self.transporternotrequired = mnm_repr.TransporterNotRequired(src_conds, dest_conds, 'ID')
		self.assertEqual(self.transporternotrequired.source_conditions, src_conds)
		self.assertIsNot(self.transporternotrequired.source_conditions, src_conds)
		self.assertEqual(self.transporternotrequired.destination_conditions, dest_conds)
		self.assertIsNot(self.transporternotrequired.destination_conditions, dest_conds)
		self.assertEqual(self.transporternotrequired.ID, 'ID')

class TransporterRequiredTest(unittest.TestCase):

	def tearDown(self):
		self.transporterrequired = None

	def test_default_values(self):
		src_conds = []
		dest_conds = []
		self.transporterrequired = mnm_repr.TransporterRequired(src_conds, dest_conds, 'location', 'ID')
		self.assertEqual(self.transporterrequired.source_conditions, src_conds)
		self.assertIsNot(self.transporterrequired.source_conditions, src_conds)
		self.assertEqual(self.transporterrequired.destination_conditions, dest_conds)
		self.assertIsNot(self.transporterrequired.destination_conditions, dest_conds)
		self.assertEqual(self.transporterrequired.transporter_location, 'location')
		self.assertEqual(self.transporterrequired.ID, 'ID')



class PresentTest(unittest.TestCase):

	def test_default_values(self):
		self.present = mnm_repr.Present('entiy', 'compartment')
		self.assertEqual(self.present.entity, 'entiy')
		self.assertEqual(self.present.compartment, 'compartment')


class InterventionTest(unittest.TestCase):

	def test_default_values(self):
		self.intervention = mnm_repr.Intervention('cond_or_act')
		self.assertEqual(self.intervention.condition_or_activity, 'cond_or_act')


class AddTest(unittest.TestCase):

	def test_default_values(self):
		self.add = mnm_repr.Add('cond_or_act')
		self.assertEqual(self.add.condition_or_activity, 'cond_or_act')


class RemoveTest(unittest.TestCase):

	def test_default_values(self):
		self.remove = mnm_repr.Remove('cond_or_act')
		self.assertEqual(self.remove.condition_or_activity, 'cond_or_act')


class ModelTest(unittest.TestCase):

	def test_setup_empty(self):
		setup_conds = []
		interm_activs = []
		term_conds = []
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.assertEqual(self.model.ID, 'ID')
		self.assertEqual(self.model.setup_conds, setup_conds)
		self.assertIsNot(self.model.setup_conds, setup_conds)
		self.assertEqual(self.model.intermediate_activities, interm_activs)
		self.assertIsNot(self.model.intermediate_activities, interm_activs)
		self.assertEqual(self.model.termination_conds, term_conds)
		self.assertIsNot(self.model.termination_conds, term_conds)

	def test_setup_with_lists(self):
		con1 = mnm_repr.Present('ent1','comp1')
		con2 = mnm_repr.Present('ent2','comp2')
		con3 = mnm_repr.Present('ent3','comp3')
		con4 = mnm_repr.Present('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1')
		act2 = mnm_repr.Activity('ID2', 'name2')
		setup_conds = [con1, con2]
		interm_activs = [act1, act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.assertEqual(self.model.ID, 'ID')
		self.assertEqual(self.model.setup_conds, setup_conds)
		self.assertIsNot(self.model.setup_conds, setup_conds)
		self.assertEqual(self.model.intermediate_activities, interm_activs)
		self.assertIsNot(self.model.intermediate_activities, interm_activs)
		self.assertEqual(self.model.termination_conds, term_conds)
		self.assertIsNot(self.model.termination_conds, term_conds)


	def test_apply_intervention_add_condition(self):
		con1 = mnm_repr.Present('ent1','comp1')
		con2 = mnm_repr.Present('ent2','comp2')
		con3 = mnm_repr.Present('ent3','comp3')
		con4 = mnm_repr.Present('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1')
		act2 = mnm_repr.Activity('ID2', 'name2')
		intervention = mnm_repr.Add(con1)
		setup_conds = [con2]
		interm_activs = [act1, act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.model.apply_intervention(intervention)
		self.assertEqual(self.model.setup_conds, [con2, con1])


	def test_apply_intervention_remove_condition(self):
		con1 = mnm_repr.Present('ent1','comp1')
		con2 = mnm_repr.Present('ent2','comp2')
		con3 = mnm_repr.Present('ent3','comp3')
		con4 = mnm_repr.Present('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1')
		act2 = mnm_repr.Activity('ID2', 'name2')
		intervention = mnm_repr.Remove(con1)
		setup_conds = [con1, con2]
		interm_activs = [act1, act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.model.apply_intervention(intervention)
		self.assertEqual(self.model.setup_conds, [con2])


	def test_apply_intervention_add_activity(self):
		con1 = mnm_repr.Present('ent1','comp1')
		con2 = mnm_repr.Present('ent2','comp2')
		con3 = mnm_repr.Present('ent3','comp3')
		con4 = mnm_repr.Present('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1')
		act2 = mnm_repr.Activity('ID2', 'name2')
		intervention = mnm_repr.Add(act1)
		setup_conds = [con1, con2]
		interm_activs = [act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.model.apply_intervention(intervention)
		self.assertEqual(self.model.intermediate_activities, [act2, act1])


	def test_apply_intervention_remove_activity(self):
		con1 = mnm_repr.Present('ent1','comp1')
		con2 = mnm_repr.Present('ent2','comp2')
		con3 = mnm_repr.Present('ent3','comp3')
		con4 = mnm_repr.Present('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1')
		act2 = mnm_repr.Activity('ID2', 'name2')
		intervention = mnm_repr.Remove(act1)
		setup_conds = [con1, con2]
		interm_activs = [act1, act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.model.apply_intervention(intervention)
		self.assertEqual(self.model.intermediate_activities, [act2])


	def test_apply_multiple_interventions(self):
		con1 = mnm_repr.Present('ent1','comp1')
		con2 = mnm_repr.Present('ent2','comp2')
		con3 = mnm_repr.Present('ent3','comp3')
		con4 = mnm_repr.Present('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1')
		act2 = mnm_repr.Activity('ID2', 'name2')
		intervention1 = mnm_repr.Add(con1)
		intervention2 = mnm_repr.Remove(con1)
		intervention3 = mnm_repr.Add(act1)
		intervention4 = mnm_repr.Remove(act1)
		setup_conds = [con2]
		interm_activs = [act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.model.apply_interventions([intervention1, intervention2, intervention3, intervention4])
		self.assertEqual(self.model.setup_conds, [con2])
		self.assertEqual(self.model.intermediate_activities, [act2])


	def test_apply_intervention_raise_not_intervention(self):
		con1 = mnm_repr.Present('ent1','comp1')
		con2 = mnm_repr.Present('ent2','comp2')
		con3 = mnm_repr.Present('ent3','comp3')
		con4 = mnm_repr.Present('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1')
		act2 = mnm_repr.Activity('ID2', 'name2')
		intervention = 'fake intervention'
		setup_conds = [con1, con2]
		interm_activs = [act1, act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.assertRaises(TypeError, self.model.apply_intervention, intervention)


	def test_apply_intervention_raise_not_intervention(self):
		con1 = mnm_repr.Present('ent1','comp1')
		con2 = mnm_repr.Present('ent2','comp2')
		con3 = mnm_repr.Present('ent3','comp3')
		con4 = mnm_repr.Present('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1')
		act2 = mnm_repr.Activity('ID2', 'name2')
		intervention = 'fake intervention'
		setup_conds = [con1, con2]
		interm_activs = [act1, act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.assertRaises(TypeError, self.model.apply_intervention, intervention)


	def test_apply_intervention_raise_neither_cond_nor_activity(self):
		con1 = mnm_repr.Present('ent1','comp1')
		con2 = mnm_repr.Present('ent2','comp2')
		con3 = mnm_repr.Present('ent3','comp3')
		con4 = mnm_repr.Present('ent4','comp4')
		act1 = mnm_repr.Activity('ID1', 'name1')
		act2 = mnm_repr.Activity('ID2', 'name2')
		intervention = mnm_repr.Intervention('nothing')
		setup_conds = [con1, con2]
		interm_activs = [act1, act2]
		term_conds = [con3, con4]
		self.model = mnm_repr.Model('ID', setup_conds, interm_activs, term_conds)
		self.assertRaises(TypeError, self.model.apply_intervention, intervention)
