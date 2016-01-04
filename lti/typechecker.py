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

class InferRValue(ast.NodeVisitor):

    def visit_Dict(self, node):
        return dict

    def visit_Set(self, node):
        return set

    def visit_ListComp(self, node):
        return list

    def visit_SetComp(self, node):
        return set

    def visit_DictComp(self, node):
        return dict

    def visit_Num(self, node):
        return int

    def visit_Str(self, node):
        return str

    def visit_Bytes(self, node):
        return list

    def visit_List(self, node):
        return str

    def visit_Tuple(self, node):
        return tuple

    def visit_Name(self, node):
        print(ast.dump(node))
        binding = self.ctx.lookup(node.id)
        if binding is None:
            raise TypeError("Variable %s is not bound" % node.id)

    def visit_Call(self, node):
        if node.func.id != 'TypeVar':
            raise NotImplementedError(node)

        """
        class TypeVar(name, *constraints, bound=None,
                covariant=False, contravariant=False)
        """
        name = node.args[0].s
        # supports only builtins
        constraints = [
            getattr(builtins, arg.id) for arg in node.args[1:]]

        kwargs = dict([(kw.arg, kw.value) for kw in node.keywords])
        if "bound" in kwargs:
            raise NotImplementedError("Bounded quantification is not supported")

        for key in ["covariant", "contravariant"]:
            value = kwargs.get("key", False)
            if value and issubclass(value, ast.NameConstant):
                value = value.value
            kwargs[key] = value

        return TypeVar(name, *constraints, **kwargs)


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

        kwargs = dict([(kw.arg, kw.value) for kw in node.keywords])
        if "bound" in kwargs:
            raise NotImplementedError("Bounded quantification is not supported")

        for key in ["covariant", "contravariant"]:
            value = kwargs.get("key", False)
            if value and issubclass(value, ast.NameConstant):
                value = value.value
            kwargs[key] = value

        return TypeVar(name, *constraints, **kwargs)

    raise NotImplementedError()


class TypeCheck(ast.NodeVisitor):

    def __init__(self):
        self.ctx = Context()
        self.infer_rvalue_type = InferRValue()
        self.infer_rvalue_type.ctx = self.ctx

    def visit_Assign(self, node):
        rvalue_type = self.infer_rvalue_type.visit(node.value)

        len_targets = len(node.targets)

        #print(ast.dump(node))
        type_value = type(node.value)

        print("TYPE", node.targets[0].id, self.infer_rvalue_type.visit(node.value))

        t_type = None
        if type_value is ast.Call:

            t_type = parse_type(node.value)
        elif type_value is ast.Name:
            #
            #print(node.value.id)
            pass
        elif type_value in AST_NODES_TYPES:
            t_type = AST_NODES_TYPES[type_value]

        # simple assign
        if len_targets == 1:
            self.ctx.add_binding(node.targets[0].id, t_type)

        print(self.ctx)

    def visit_FunctionDef(self, node):
        #print(ast.dump(node))
        self.generic_visit(node)

        for arg in node.args.args:
            self.ctx.add_binding(arg.arg, arg.annotation)
        #self.actx[node.name] = Callable()

    def visit_Call(self, node):
        pass
        #print(ast.dump(node))