import unittest
import ast
import lti

class ConstraintsTestCase(unittest.TestCase):

    def test_declarations(self):
        tree = ast.parse("x = 10")
        lti.generate_constraints(tree)
