#! /usr/bin/env python3

import unittest
from tests import mnm_repr_test




suite1 = unittest.TestLoader().loadTestsFromTestCase(mnm_repr_test.ElementTest)
unittest.TextTestRunner(verbosity=2).run(suite1)
