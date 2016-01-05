import unittest
import ast
import lti
import builtins
import sys
import os

from typing import *

from lti.context import Context


class ErrorException(Exception):
    
    def __init__(self, msg, node):
        self.msg = msg
        self.node = node


class RestoreType(ast.NodeVisitor):

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
        binding = self.ctx.lookup(node.id)
        if binding is None:
            raise ErrorException("Variable '%s' is unbound" % node.id, node)
        return binding

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
            value = kwargs.get(key, False)
            if value and type(value) is ast.NameConstant:
                value = value.value
            kwargs[key] = value

        return TypeVar(name, *constraints, **kwargs)


class TypeChecker(ast.NodeVisitor):

    def __init__(self):
        self.ctx = Context()
        self.restore_type = RestoreType()
        self.restore_type.ctx = self.ctx

    def visit_Assign(self, node):
        rvalue_type = self.restore_type.visit(node.value)

        len_targets = len(node.targets)
        if len_targets == 1:
            self.ctx.add_binding(node.targets[0].id, rvalue_type)
        else:
            raise NotImplementedError("Unpack not implemented")

    def visit_FunctionDef(self, node):
        with self.ctx.scope():

            len_defaults = len(node.args.defaults)
            len_args = len(node.args.args)

            args_types = []
            for (pos, arg) in enumerate(node.args.args):
                def_pos = pos - (len_args - len_defaults)
                if def_pos >= 0:
                    def_value = node.args.defaults[def_pos]
                    arg_type = self.restore_type.visit(def_value)
                elif arg.annotation is not None:
                    arg_type = self.restore_type.visit(arg.annotation)
                else:
                    # no annotation
                    arg_type = self.ctx.pick_fresh_name(arg.arg)

                self.ctx.add_binding(arg.arg, arg_type)
                args_types.append(arg_type)

            if node.returns is not None:
                return_type = self.restore_type.visit(node.returns)
                self.ctx.add_binding("return", return_type)
            
            for expr in node.body:
                self.visit(expr)

            return_type = self.ctx.lookup("return")

        self.ctx.add_binding(node.name, Callable[args_types, return_type])

    def visit_Return(self, node):
        if type(node.value) is not ast.Name:
            raise NotImplementedError("Supports only variable")
        
        binding = self.ctx.lookup(node.value.id)
        if binding is None:
            raise ErrorException(
                "Variable '%s' is unbound" % node.value.id,
                node.value.lineno, node.value.col_offset)

        return_type = self.ctx.lookup("return")
        if return_type is None:
            self.ctx.add_binding("return", binding)
        elif not issubclass(binding, return_type):
            raise ErrorException(
                "Type of variable '%s' should be is subclass of return type" % node.value.id,
                node)

    def visit_Call(self, node):
        pass


def type_check(source):
    type_checker = TypeChecker()
    tree = ast.parse(source)
    try:
        type_checker.visit(tree)
    except ErrorException as e:
        ctx_lineno = e.node.lineno - 4
        ctx_lineno = ctx_lineno if ctx_lineno > 0 else 0
        context = source.split("\n")[ctx_lineno: e.node.lineno]
        print("")
        print("\n".join(context))
        indent = " " * (e.node.col_offset)
        print("%s^" % indent)
        print("Error: %s" % e.msg)
