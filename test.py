import unittest
import sys
import os
import ast

sys.path.insert(0,
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "typehinting", "prototyping"
    ))


from lti.typechecker import TypeCheck

"""
* Type inference of declarations

    Example:
        x = 11
        # x: int

        def foo(x: int): x*x
        # foo: int -> int

* Type inference for generic arguments

    Example:

        T = TypeVar('T')

        def head(l: List[T]) -> T:
            return l[0]

        head([1,2,3])
        # T: int

* Type inference of expressions

    Example:

        "a b c".split(" ")
        # str

"""


class InferTestCase(unittest.TestCase):

    def setUp(self):
        self.visitor = TypeCheck()

    def test_declarations(self):
        tree = ast.parse("""
x = 10
y = (1,2,3)
        """)
        self.visitor.visit(tree)

        #assert('x' in self.visitor.actx)
        #assert('y' in self.visitor.actx)

        tree = ast.parse("""
from typing import TypeVar

T = TypeVar('T')

A = TypeVar('A', str, bytes, covariant=True)

        """)
        self.visitor.visit(tree)
        #print(self.visitor.actx)

    def test_arguments(self):
        tree = ast.parse("""
T = TypeVar('T')

def foo(a: T, b, c = 105):
    y = x
    z = y
    return x*x

foo(10, "string")
        """)
        self.visitor.visit(tree)


if __name__ == '__main__':
    unittest.main()