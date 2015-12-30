import unittest
import ast
import lti
import builtins
import sys
import os

sys.path.insert(0,
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "typehinting", "prototyping"
    ))

from typing import *

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
    func_type = type(node.func)

    if func_type is not ast.Name:
        raise NotImplementedError()

    if node.func.id == 'TypeVar':
        name = node.args[0].s
        # supports only builtins
        constraints = [
            getattr(builtins, arg.id) for arg in node.args[1:]]
        kwargs = dict([
            (kw.arg, kw.value.id == 'True')
            for kw in node.keywords])
        return TypeVar(name, *constraints, **kwargs)

    raise NotImplementedError()

class Analyzer(ast.NodeVisitor):

    def __init__(self):
        self.ctx = [{}]
        self.actx = self.ctx[0]

    def visit_Assign(self, node):
        #print(node.targets[0].id)
        len_targets = len(node.targets)
        type_value = type(node.value)

        t_type = None
        if type_value is ast.Call:
            t_type = parse_type(node.value)
        elif type_value is ast.Name:
            #
            print(node.value.id)
        elif type_value in AST_NODES_TYPES:
            t_type = AST_NODES_TYPES[type_value]

        # simple assign
        if len_targets == 1:
            self.actx[node.targets[0].id] = t_type


    def visit_FunctionDef(self, node):
        print(ast.dump(node))
        self.generic_visit(node)

        for arg in node.args.args:
            self.actx[arg.arg] = arg.annotation
        #self.actx[node.name] = Callable()

    def visit_Call(self, node):
        print(ast.dump(node))

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
        print(self.visitor.actx)


if __name__ == '__main__':
    unittest.main()