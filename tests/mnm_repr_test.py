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


