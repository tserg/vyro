from typing import List

from vyper import ast as vy_ast
from vyper.semantics.types.function import FunctionVisibility, StateMutability

from vyro.cairo.stubs import BUILTINS_STUB, generate_storage_var_stub
from vyro.cairo.utils import INDENT
from vyro.exceptions import TranspilerPanic, UnsupportedNode


class CairoWriter:
    def __init__(self) -> None:
        self.header: str = "%lang starknet\n"
        self.imports: List[str] = []
        self.events: List[str] = []
        self.storage_vars: List[str] = []
        self.storage_vars_getters: List[str] = []
        self.functions: List[str] = []

    def cairo(self) -> str:

        imports = ""
        if self.imports:
            imports = "\n".join(self.imports)

        storage_vars = ""
        if self.storage_vars:
            storage_vars = "\n\n".join(self.storage_vars)

        storage_vars_getters = ""
        if self.storage_vars_getters:
            storage_vars_getters = "\n\n".join(self.storage_vars_getters)

        functions = ""
        if self.functions:
            functions = "\n\n".join(self.functions)

        cairo = "\n".join(
            [self.header, imports, storage_vars, storage_vars_getters, functions]
        )
        return cairo

    def write(self, node, *args):
        node_type = type(node).__name__
        write_fn = getattr(self, f"write_{node_type}", None)
        if write_fn is None:
            raise UnsupportedNode(
                f"{node_type} node is not yet supported in writer", node
            )
        return write_fn(node, *args)

    def write_arg(self, node):
        self.write(node.arg)
        self.write(node.annotation)

    def write_arguments(self, node):
        if len(node.args) == 0:
            return None

        for a in node.args:
            pass
        for d in node.defaults:
            pass

    def write_keyword(self, node):
        self.write(node.arg)
        self.write(node.value)

    def write_Add(self, node):
        pass

    def write_And(self, node):
        pass

    def write_AnnAssign(self, node):
        self.write(node.target)
        # self.write(node.annotation)
        if node.value:
            self.write(node.value)

    def write_Assert(self, node):
        self.write(node.test)

    def write_Assign(self, node):
        target_str = self.write(node.target)
        value_str = self.write(node.value)
        ret = f"let {target_str} = {value_str}"
        return ret

    def write_Attribute(self, node):
        value_str = self.write(node.value)
        return f"{value_str}.{node.attr}"

    def write_AugAssign(self, node):
        self.write(node.op)
        self.write(node.target)
        self.write(node.value)

    def write_BinOp(self, node):
        self.write(node.left)
        self.write(node.op)
        self.write(node.right)

    def write_BitAnd(self, node):
        pass

    def write_BitOr(self, node):
        pass

    def write_BitXor(self, node):
        pass

    def write_BoolOp(self, node):
        self.write(node.op)
        self.write(node.values)

    def write_Break(self, node):
        pass

    def write_CairoStorageRead(self, node):
        target_str = self.write(node.target)
        return f"let ({target_str}) = {node.value}.read()"

    def write_CairoStorageWrite(self, node):
        value_str = self.write(node.value)
        return f"{node.target}.write({value_str})"

    def write_Call(self, node):
        self.write(node.func)
        for a in node.args:
            self.write(a)
        for k in node.keywords:
            self.write(k)

    def write_Compare(self, node):
        self.write(node.left)
        self.write(node.op)
        self.write(node.right)

    def write_Continue(self, node):
        pass

    def write_Decimal(self, node):
        return str(node.value)

    def write_Dict(self, node):
        for k in node.keys:
            self.write(k)

        for v in node.values:
            self.write(v)

    def write_Div(self, node):
        pass

    def write_DocStr(self, node):
        self.write(node.value)

    def write_EnumDef(self, node):
        self.write(node.name)
        self.write(node.body)

    def write_Eq(self, node):
        pass

    def write_EventDef(self, node):
        pass

    def write_Expr(self, node):
        self.write(node.value)

    def write_For(self, node):
        self.write(node.iter)
        self.write(node.target)
        self.write(node.body)

    def write_FunctionDef(self, node):
        ret = []

        typ = node._metadata["type"]

        # Add view or external decorator
        if typ.visibility == FunctionVisibility.EXTERNAL:
            if typ.mutability == StateMutability.VIEW:
                ret.append("@view")
            else:
                ret.append("@external")

        args_str = self.write(node.args) or ""

        return_decl_str = ""
        if node.returns:
            # TODO Set return types
            # return_values = self.write(node.returns)
            return_typ = node.returns._metadata["type"]
            return_decl_str = f" -> ({node.name}_ret : {return_typ})"

        fn_def_str = f"func {node.name}{BUILTINS_STUB}({args_str}){return_decl_str}:"

        ret.append(fn_def_str)
        # Add body
        for n in node.body:
            stmt_str = self.write(n)
            if not stmt_str:
                raise TranspilerPanic("Unable to write statement in function body")
            ret.append(INDENT + stmt_str)

        return_val_str = ""
        if node.returns:
            return_val_str = self.write(node.returns)

        return_stmt_str = f"return ({return_val_str})"
        ret.append(INDENT + return_stmt_str)

        # Add closing block
        ret.append("end")

        fn_str = "\n".join(ret)
        self.functions.append(fn_str)

    def write_Gt(self, node):
        pass

    def write_GtE(self, node):
        pass

    def write_Hex(self, node):
        return str(node.value)

    def write_If(self, node):
        self.write(node.test)
        self.write(node.body)
        self.write(node.orelse)

    def write_Import(self, node):
        self.write(node.name)

    def write_ImportFrom(self, node):
        pass

    def write_In(self, node):
        pass

    def write_Index(self, node):
        self.write(node.value)

    def write_InterfaceDef(self, node):
        self.write(node.name)
        self.write(node.body)

    def write_Int(self, node):
        return str(node.value)

    def write_Invert(self, node):
        pass

    def write_List(self, node):
        for e in node.elements:
            self.write(e)

    def write_Log(self, node):
        pass

    def write_Lt(self, node):
        pass

    def write_LtE(self, node):
        pass

    def write_Mod(self, node):
        pass

    def write_Module(self, node):
        # Add import directives
        imports = node._metadata["import_directives"]
        for k, v in imports.items():
            imported = ", ".join(v)
            self.imports.append(f"from {k} import {imported}\n")

        for i in node.body:
            self.write(i)

    def write_Mult(self, node):
        pass

    def write_Name(self, node):
        return str(node.id)

    def write_NameConstant(self, node):
        return str(node.value)

    def write_Not(self, node):
        pass

    def write_NotEq(self, node):
        pass

    def write_NotIn(self, node):
        pass

    def write_Or(self, node):
        pass

    def write_Pass(self, node):
        pass

    def write_Pow(self, node):
        pass

    def write_Raise(self, node):
        pass

    def write_Return(self, node):
        self.write(node.value)

    def write_StructDef(self, node):
        self.write(node.name)
        self.write(node.body)

    def write_Sub(self, node):
        pass

    def write_Subscript(self, node):
        self.write(node.slice)
        self.write(node.value)

    def write_Tuple(self, node):
        for e in node.elements:
            self.write(e)

    def write_UnaryOp(self, node):
        self.write(node.op)
        self.write(node.operand)

    def write_USub(self, node):
        pass

    def write_VariableDecl(self, node):

        typ = node._metadata["type"]
        if not typ.is_constant and not typ.is_immutable:
            name = node.target.id
            storage_var_stub = generate_storage_var_stub(name, typ)
            self.storage_vars.append(storage_var_stub)


def write(ast: vy_ast.Module):
    writer = CairoWriter()
    writer.write(ast)
    output = writer.cairo()
    return output
