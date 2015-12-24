import unittest
import ast
import lti

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

AST_NODES_TYPES = {
    ast.Dict: dict,
    ast.Set: set,
    ast.ListComp: list,
    ast.SetComp: set,
    ast.DictComp: dict,
    ast.Num: int,
    ast.Str: str,
    ast.Bytes: bytes,
    ast.List: list,
    ast.Tuple: tuple
}

def parse_type(node):
    pass

class Analyzer(ast.NodeVisitor):

    def __init__(self):
        self.ctx = [{}]
        self.actx = self.ctx[0]

    def visit_Assign(self, node):
        len_targets = len(node.targets)
        type_value = type(node.value)

        if type_value is ast.Call:
            parse_type(node.value)

        # simple assign
        if len_targets == 1 and type_value in AST_NODES_TYPES:
            self.actx[node.targets[0].id] = AST_NODES_TYPES[type_value]




class ConstraintsTestCase(unittest.TestCase):

    def setUp(self):
        self.visitor = Analyzer()

    def test_declarations(self):
        tree = ast.parse("""
x = 10
y = (1,2,3)
        """)
        self.visitor.visit(tree)

        assert('x' in self.visitor.actx)
        assert('y' in self.visitor.actx)

        tree = ast.parse("""
from typing import TypeVar

T = TypeVar('T')
        """)
        self.visitor.visit(tree)


if __name__ == '__main__':
    unittest.main()