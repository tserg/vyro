from string import ascii_lowercase as alc
from typing import List

from vyper import ast as vy_ast
from vyper.semantics.types.function import StateMutability

from vyro.cairo.implicits import IMPLICITS
from vyro.cairo.types import CairoMappingDefinition
from vyro.cairo.utils import INDENT, generate_storage_var_stub
from vyro.exceptions import TranspilerPanic, UnsupportedNode


class CairoWriter:
    def __init__(self) -> None:
        self.header: str = "%lang starknet\n"
        self.imports: List[str] = []
        self.constants: List[str] = []
        self.events: List[str] = []
        self.storage_vars: List[str] = []
        self.storage_vars_getters: List[str] = []
        self.functions: List[str] = []

    def cairo(self) -> str:

        imports = ""
        if self.imports:
            imports = "\n".join(self.imports)

        constants = ""
        if self.constants:
            constants = "\n".join(self.constants)

        events = ""
        if self.events:
            events = "\n".join(self.events)

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
            [
                self.header,
                imports,
                constants,
                events,
                storage_vars,
                storage_vars_getters,
                functions,
            ]
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
        typ = node._metadata.get("type")
        return f"{node.arg} : {typ}"

    def write_arguments(self, node):
        if len(node.args) == 0:
            return None

        args = []
        for a in node.args:
            args.append(self.write(a))

        return ", ".join(args)

    def write_keyword(self, node):
        value_str = self.write(node.value)
        return f"{node.arg}={value_str}"

    def write_Add(self, node):
        pass

    def write_And(self, node):
        pass

    def write_AnnAssign(self, node):
        typ = node._metadata.get("type")
        target_str = self.write(node.target)
        value_str = self.write(node.value)
        return f"tempvar {target_str} : {typ} = {value_str}"

    def write_Assert(self, node):
        self.write(node.test)

    def write_Assign(self, node):
        target_str = self.write(node.target)
        target_typ = node.target._metadata.get("type")
        value_str = self.write(node.value)
        ret = f"let {target_str} : {target_typ} = {value_str}"
        return ret

    def write_Attribute(self, node):
        value_str = self.write(node.value)
        return f"{value_str}.{node.attr}"

    def write_AugAssign(self, node):
        self.write(node.op)
        self.write(node.target)
        self.write(node.value)

    def write_BinOp(self, node):
        left_str = self.write(node.left)
        op_str = str(node.op._pretty)
        right_str = self.write(node.right)
        return f"{left_str} {op_str} {right_str}"

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

    def write_Bytes(self, node):
        pass

    def write_CairoStorageRead(self, node):
        target_str = self.write(node.target)
        target_typ = node.target._metadata.get("type")
        value_str = self.write(node.value)

        arg_str = ""
        args = []
        for a in node.args:
            args.append(self.write(a))
            arg_str = ", ".join(args)

        return f"let ({target_str} : {target_typ}) = {value_str}.read({arg_str})"

    def write_CairoStorageWrite(self, node):
        target_str = self.write(node.target)

        arg_str = ""
        args = []
        for a in node.value:
            args.append(self.write(a))
            arg_str = ", ".join(args)

        return f"{target_str}.write({arg_str})"

    def write_Call(self, node):
        func_str = self.write(node.func)

        args = []
        for a in node.args:
            arg_str = self.write(a)
            args.append(arg_str)

        kwargs = []
        for k in node.keywords:
            kwarg_str = self.write(k)
            kwargs.append(kwarg_str)

        args_str = ", ".join(args)
        kwargs_str = ", ".join(kwargs)

        return f"{func_str}({args_str}{kwargs_str})"

    def write_Compare(self, node):
        self.write(node.left)
        self.write(node.op)
        self.write(node.right)

    def write_Continue(self, node):
        pass

    def write_Decimal(self, node):
        pass

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
        ret = ["@event"]

        args_str = ""
        args = []
        for i in range(len(node.body)):
            n = node.body[i]
            arg_name = alc[i]
            arg_typ = n._metadata.get("type")
            args.append(f"{arg_name} : {arg_typ}")

        if len(args) > 0:
            args_str = ", ".join(args)

        event_def = f"func {node.name}({args_str}):"
        ret.append(event_def)
        ret.append("end")
        self.events.append("\n".join(ret))

    def write_Expr(self, node):
        return self.write(node.value)

    def write_For(self, node):
        self.write(node.iter)
        self.write(node.target)
        self.write(node.body)

    def write_FunctionDef(self, node):
        ret = []

        fn_typ = node._metadata.get("type")

        # Add view or external decorator
        if fn_typ.is_external:
            if fn_typ.is_constructor:
                ret.append("@constructor")
            elif fn_typ.mutability == StateMutability.VIEW:
                ret.append("@view")
            else:
                ret.append("@external")

        args_str = self.write(node.args) or ""

        implicits_stub = []
        implicits = node._metadata.get("implicits")
        for i in implicits:
            i_type_str = IMPLICITS[i]
            if i_type_str is None:
                i_str = i
            else:
                i_str = f"{i}: {i_type_str}"
            implicits_stub.append(i_str)
        implicits_str = ", ".join(implicits_stub)

        return_decl_str = ""
        if node.returns:
            return_typ = fn_typ.return_type
            if isinstance(return_typ, CairoMappingDefinition):
                return_typ = return_typ.value_type
            return_decl_str = f" -> ({node.name}_ret : {return_typ})"

        fn_def_str = (
            f"func {node.name}{{{implicits_str}}}({args_str}){return_decl_str}:"
        )

        ret.append(fn_def_str)
        # Add body
        for n in node.body:
            stmt_str = self.write(n)
            if not stmt_str:
                raise TranspilerPanic("Unable to write statement in function body")
            ret.append(INDENT + stmt_str)

        # Inject return if no return value
        if not node.returns:
            return_stmt_str = "return ()"
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
        # We cannot rely on `write_Call` because of `emit` in Cairo
        call_node = node.value

        # Event name is in `func` attribute of `vy_ast.Call`
        event_name = self.write(call_node.func)

        args = []
        for a in call_node.args:
            arg_str = self.write(a)
            args.append(arg_str)

        args_str = ", ".join(args)

        return f"{event_name}.emit({args_str})"

    def write_Lt(self, node):
        pass

    def write_LtE(self, node):
        pass

    def write_Mod(self, node):
        pass

    def write_Module(self, node):
        # Add import directives
        imports = node._metadata.get("import_directives")
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
        value_str = self.write(node.value)
        return f"return ({value_str})"

    def write_Str(self, node):
        value_str = f"'{node.value}'"
        return value_str

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
        op_str = self.write(node.op)
        value_str = self.write(node.operand)
        return f"{op_str}{value_str}"

    def write_USub(self, node):
        return "-"

    def write_VariableDecl(self, node):
        typ = node._metadata.get("type")
        name = node.target.id
        if node.is_constant:
            value_str = self.write(node.value)
            constant_decl_str = f"const {name} = {value_str}"
            self.constants.append(constant_decl_str)

        storage_var_stub = generate_storage_var_stub(name, typ)
        self.storage_vars.append(storage_var_stub)


def write(ast: vy_ast.Module):
    writer = CairoWriter()
    writer.write(ast)
    output = writer.cairo()
    return output
