import unittest
import ast
import lti
import builtins
import sys
import os

from typing import *

from lti.context import Context

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
        """
        class TypeVar(name, *constraints, bound=None,
                covariant=False, contravariant=False)
        """
        #print(ast.dump(node))
        name = node.args[0].s
        # supports only builtins
        constraints = [
            getattr(builtins, arg.id) for arg in node.args[1:]]
        kwargs = dict([
            (kw.arg, kw.value.value == True)
            for kw in node.keywords])
        return TypeVar(name, *constraints, **kwargs)

    raise NotImplementedError()


class TypingReconstruction(ast.NodeTransformer):
    pass

class TypeCheck(ast.NodeVisitor):

    def __init__(self):
        self.ctx = Context()

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
            self.ctx.add_binding(node.targets[0].id, t_type)


    def visit_FunctionDef(self, node):
        #print(ast.dump(node))
        self.generic_visit(node)

        for arg in node.args.args:
            self.ctx.add_binding(arg.arg, arg.annotation)
        #self.actx[node.name] = Callable()

    def visit_Call(self, node):
        pass
        #print(ast.dump(node))