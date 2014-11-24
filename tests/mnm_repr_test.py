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

#Present

#Intervention

#Add

#Remove

#Model
