from vyro.exceptions import UnsupportedNode


class BaseVisitor:
    """
    Base class for Vyper AST tree visitor.
    """

    def visit(self, node, ast, context, *args):
        node_type = type(node).__name__
        visitor_fn = getattr(self, f"visit_{node_type}", None)
        if visitor_fn is None:
            raise UnsupportedNode(f"{node_type} node is not yet supported in visitor", node)
        visitor_fn(node, ast, context, *args)

    def visit_arg(self, node, ast, context):
        pass

    def visit_arguments(self, node, ast, context):
        for a in node.args:
            self.visit(a, ast, context)

    def visit_keyword(self, node, ast, context):
        self.visit(node.value, ast, context)

    def visit_Add(self, node, ast, context):
        pass

    def visit_And(self, node, ast, context):
        pass

    def visit_AnnAssign(self, node, ast, context):
        self.visit(node.target, ast, context)
        if node.value:
            self.visit(node.value, ast, context)

    def visit_Assert(self, node, ast, context):
        self.visit(node.test, ast, context)

    def visit_Assign(self, node, ast, context):
        self.visit(node.target, ast, context)
        self.visit(node.value, ast, context)

    def visit_Attribute(self, node, ast, context):
        self.visit(node.value, ast, context)

    def visit_AugAssign(self, node, ast, context):
        self.visit(node.op, ast, context)
        self.visit(node.target, ast, context)
        self.visit(node.value, ast, context)

    def visit_BinOp(self, node, ast, context):
        self.visit(node.left, ast, context)
        self.visit(node.op, ast, context)
        self.visit(node.right, ast, context)

    def visit_BitAnd(self, node, ast, context):
        pass

    def visit_BitOr(self, node, ast, context):
        pass

    def visit_BitXor(self, node, ast, context):
        pass

    def visit_BoolOp(self, node, ast, context):
        self.visit(node.op, ast, context)
        for i in node.values:
            self.visit(i, ast, context)

    def visit_Break(self, node, ast, context):
        pass

    def visit_Bytes(self, node, ast, context):
        pass

    def visit_CairoAssert(self, node, ast, context):
        pass

    def visit_CairoIfTest(self, node, ast, context):
        pass

    def visit_CairoStorageRead(self, node, ast, context):
        pass

    def visit_CairoStorageWrite(self, node, ast, context):
        pass

    def visit_Call(self, node, ast, context):
        self.visit(node.func, ast, context)

        for a in node.args:
            self.visit(a, ast, context)

        for k in node.keywords:
            self.visit(k, ast, context)

    def visit_Compare(self, node, ast, context):
        self.visit(node.left, ast, context)
        self.visit(node.right, ast, context)

    def visit_Continue(self, node, ast, context):
        pass

    def visit_Decimal(self, node, ast, context):
        pass

    def visit_Dict(self, node, ast, context):
        for k in node.keys:
            self.visit(k, ast, context)

        for v in node.values:
            self.visit(v, ast, context)

    def visit_Div(self, node, ast, context):
        pass

    def visit_DocStr(self, node, ast, context):
        self.visit(node.value, ast, context)

    def visit_EnumDef(self, node, ast, context):
        self.visit(node.name, ast, context)
        self.visit(node.body, ast, context)

    def visit_Eq(self, node, ast, context):
        pass

    def visit_EventDef(self, node, ast, context):
        pass

    def visit_Expr(self, node, ast, context):
        self.visit(node.value, ast, context)

    def visit_For(self, node, ast, context):
        self.visit(node.iter, ast, context)
        self.visit(node.target, ast, context)
        self.visit(node.body, ast, context)

    def visit_FunctionDef(self, node, ast, context):
        self.visit(node.args, ast, context)

        for i in node.body:
            self.visit(i, ast, context)

        if node.returns:
            self.visit(node.returns, ast, context)

    def visit_Gt(self, node, ast, context):
        pass

    def visit_GtE(self, node, ast, context):
        pass

    def visit_Hex(self, node, ast, context):
        pass

    def visit_If(self, node, ast, context):
        self.visit(node.test, ast, context)

        for i in node.body:
            self.visit(i, ast, context)

        for i in node.orelse:
            self.visit(i, ast, context)

    def visit_Import(self, node, ast, context):
        self.visit(node.name, ast, context)

    def visit_ImportFrom(self, node, ast, context):
        pass

    def visit_In(self, node, ast, context):
        pass

    def visit_Index(self, node, ast, context):
        self.visit(node.value, ast, context)

    def visit_Int(self, node, ast, context):
        pass

    def visit_InterfaceDef(self, node, ast, context):
        self.visit(node.name, ast, context)
        self.visit(node.body, ast, context)

    def visit_Invert(self, node, ast, context):
        pass

    def visit_List(self, node, ast, context):
        for e in node.elements:
            self.visit(e, ast, context)

    def visit_Log(self, node, ast, context):
        for i in node.value.args:
            self.visit(i, ast, context)

    def visit_Lt(self, node, ast, context):
        pass

    def visit_LtE(self, node, ast, context):
        pass

    def visit_Mod(self, node, ast, context):
        pass

    def visit_Module(self, node, ast, context):
        for i in node.body:
            self.visit(i, ast, context)

    def visit_Mult(self, node, ast, context):
        pass

    def visit_Name(self, node, ast, context):
        pass

    def visit_NameConstant(self, node, ast, context):
        pass

    def visit_Not(self, node, ast, context):
        pass

    def visit_NotEq(self, node, ast, context):
        pass

    def visit_NotIn(self, node, ast, context):
        pass

    def visit_Or(self, node, ast, context):
        pass

    def visit_Pass(self, node, ast, context):
        pass

    def visit_Pow(self, node, ast, context):
        pass

    def visit_Raise(self, node, ast, context):
        pass

    def visit_Return(self, node, ast, context):
        self.visit(node.value, ast, context)

    def visit_Str(self, node, ast, context):
        pass

    def visit_StructDef(self, node, ast, context):
        self.visit(node.name, ast, context)
        self.visit(node.body, ast, context)

    def visit_Sub(self, node, ast, context):
        pass

    def visit_Subscript(self, node, ast, context):
        self.visit(node.slice, ast, context)
        self.visit(node.value, ast, context)

    def visit_Tuple(self, node, ast, context):
        for e in node.elements:
            self.visit(e, ast, context)

    def visit_UnaryOp(self, node, ast, context):
        self.visit(node.op, ast, context)
        self.visit(node.operand, ast, context)

    def visit_USub(self, node, ast, context):
        pass

    def visit_VariableDecl(self, node, ast, context):
        self.visit(node.target, ast, context)
        if node.value:
            self.visit(node.value, ast, context)
