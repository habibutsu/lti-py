import unittest
import sys
import os
import ast

sys.path.insert(0,
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "typehinting", "prototyping"
    ))

sys.path.insert(0,
    os.path.join(
        os.getcwd(),
        "typehinting", "prototyping"
    ))



#from lti.typechecker import type_check
from lti.typechecker import TypeChecker, ErrorException
import typing

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
        self.type_checker = TypeChecker()

    def test_unbound(self):
        tree = ast.parse("""x = y""")
        with self.assertRaises(ErrorException):
            self.type_checker.visit(tree)

    def test_declarations(self):
        tree = ast.parse("""
x = 10
y = (1,2,3)
        """)
        self.type_checker.visit(tree)
        self.assertIs(self.type_checker.ctx.lookup("x"), int)
        self.assertIs(self.type_checker.ctx.lookup("y"), tuple)

    def test_recover_typevar(self):
        tree = ast.parse("""
from typing import TypeVar

T = TypeVar('T')
U = TypeVar('U', str, bytes, covariant=True)
        """)
        self.type_checker.visit(tree)

        self.assertIsInstance(
            self.type_checker.ctx.lookup("T"), typing.TypeVar)
        self.assertIsInstance(
            self.type_checker.ctx.lookup("U"), typing.TypeVar)

    def test_arguments(self):
        tree = ast.parse("""
U = TypeVar('T', contravariant=True)
T = TypeVar('U', int, float)

def foo1(a: TypeVar('T'), b):
    pass

def foo2(a: T, b, c = 105) -> U:
    x = a
    y = b
    return x

foo1(10, "string")
        """)
        #self.visitor.visit(tree)


if __name__ == '__main__':
    unittest.main()