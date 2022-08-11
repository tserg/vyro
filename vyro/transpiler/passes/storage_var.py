from vyper import ast as vy_ast
from vyper.semantics.types.function import ContractFunction, FunctionVisibility, StateMutability

from vyro.cairo.nodes import CairoStorageRead, CairoStorageWrite
from vyro.transpiler.context import ASTContext
from vyro.transpiler.utils import (
    convert_node_type_definition,
    generate_name_node,
    get_cairo_type,
    initialise_function_implicits,
    insert_statement_before,
    set_parent,
)
from vyro.transpiler.visitor import BaseVisitor


class StorageVarVisitor(BaseVisitor):
    def visit_VariableDecl(
        self, node: vy_ast.VariableDecl, ast: vy_ast.Module, context: ASTContext
    ):
        # Store original variable name
        var_name = node.target.id

        # Update type
        vy_typ = node._metadata["type"]
        cairo_typ = get_cairo_type(vy_typ)
        node._metadata["type"] = cairo_typ

        if node.is_public is True:
            # Create temporary variable for assignment of storage read value
            temp_name_node = generate_name_node(context.reserve_id())
            temp_name_node._metadata["type"] = cairo_typ

            value_node = vy_ast.Name(
                node_id=context.reserve_id(), id=f"{var_name}_STORAGE", ast_type="Name"
            )

            # Create storage read node
            storage_read_node = CairoStorageRead(
                node_id=context.reserve_id(),
                parent=ast,
                targets=[temp_name_node],  # type: ignore
                value=value_node,
            )
            storage_read_node._children.add(value_node)
            storage_read_node._children.add(temp_name_node)

            return_value_node = vy_ast.Name(
                node_id=context.reserve_id(), id=temp_name_node.id, ast_type="Name"
            )
            return_value_node._metadata["type"] = cairo_typ

            fn_node_args = vy_ast.arguments(
                node_id=context.reserve_id(), args=[], defaults=[], ast_type="arguments"
            )

            # Create return node
            return_node = vy_ast.Return(
                node_id=context.reserve_id(), value=return_value_node, ast_type="Return"
            )
            return_node._children.add(return_value_node)

            # Create return type node
            return_type_node = vy_ast.Name(
                node_id=context.reserve_id(), id=f"{cairo_typ}", ast_type="Name"
            )

            fn_node = vy_ast.FunctionDef(
                node_id=context.reserve_id(),
                name=var_name,
                body=[storage_read_node, return_node],
                args=fn_node_args,
                returns=return_type_node,
                decorator_list=None,
                doc_string=None,
                ast_type="FunctionDef",
            )
            initialise_function_implicits(fn_node)

            fn_node._children.add(storage_read_node)
            fn_node._children.add(fn_node_args)
            fn_node._children.add(return_node)

            fn_node_typ = ContractFunction(
                name=var_name,
                arguments={},
                min_arg_count=0,
                max_arg_count=0,
                return_type=cairo_typ,
                function_visibility=FunctionVisibility.EXTERNAL,
                state_mutability=StateMutability.VIEW,
            )

            fn_node._metadata["type"] = fn_node_typ

            ast.add_to_body(fn_node)

    def visit_Assign(self, node: vy_ast.Assign, ast: vy_ast.Module, context: ASTContext):
        # Check for storage variable on LHS of assignment
        lhs = node.target
        contract_vars = lhs.get_descendants(
            vy_ast.Attribute, {"value.id": "self"}, include_self=True
        )

        cairo_typ = convert_node_type_definition(node.target)

        if contract_vars:
            # Create new variable and assign RHS
            rhs_name_node = generate_name_node(context.reserve_id())
            rhs_assignment_node = vy_ast.Assign(
                node_id=context.reserve_id(),
                targets=[rhs_name_node],
                value=node.value,
                ast_type="Assign",
            )
            rhs_assignment_node._children.add(rhs_name_node)
            rhs_assignment_node._children.add(node.value)
            set_parent(node.value, rhs_assignment_node)

            # Add storage write node to body of function

            fn_node = node.get_ancestor(vy_ast.FunctionDef)

            # Create storage write node
            contract_var = contract_vars.pop()
            value_node = vy_ast.Name(
                node_id=context.reserve_id(), id=rhs_name_node.id, ast_type="Name"
            )

            storage_write_node = CairoStorageWrite(
                node_id=context.reserve_id(),
                parent=fn_node,
                targets=[  # type: ignore
                    vy_ast.Name(
                        node_id=context.reserve_id(),
                        id=f"{contract_var.attr}_STORAGE",
                        ast_type="Name",
                    )
                ],
                value=value_node,
            )
            storage_write_node._children.add(value_node)

            # Update type
            storage_write_node._metadata["type"] = cairo_typ
            storage_write_node.value._metadata["type"] = cairo_typ
            storage_write_node.target._metadata["type"] = cairo_typ

            # Replace assign node with RHS
            ast.replace_in_tree(node, storage_write_node)
            # Add RHS node before storage write node
            insert_statement_before(rhs_assignment_node, storage_write_node, fn_node)

        # Handle storage variables on RHS of assignment
        rhs = node.value
        rhs_contract_vars = rhs.get_descendants(
            vy_ast.Attribute, {"value.id": "self"}, include_self=True
        )
        if rhs_contract_vars:
            contract_var = rhs_contract_vars.pop()
            # Store original variable name
            var_name = contract_var.attr
            # Create temporary variable for assignment of storage read value
            temp_name_node = generate_name_node(context.reserve_id())
            temp_name_node._metadata["type"] = cairo_typ

            value_node = vy_ast.Name(
                node_id=context.reserve_id(), id=f"{var_name}_STORAGE", ast_type="Name"
            )

            # Create storage read node
            storage_read_node = CairoStorageRead(
                node_id=context.reserve_id(),
                parent=ast,
                targets=[temp_name_node],  # type: ignore
                value=value_node,
                ast_type="CairoStorageRead",
            )
            storage_read_node._children.add(value_node)
            storage_read_node._children.add(temp_name_node)

            # Insert `CairoStorageRead` node before `Assign`
            fn_node = node.get_ancestor(vy_ast.FunctionDef)
            insert_statement_before(storage_read_node, node, fn_node)

            # Duplicate name node
            temp_name_node_copy = generate_name_node(context.reserve_id(), name=temp_name_node.id)
            ast.replace_in_tree(contract_var, temp_name_node_copy)

    def visit_AugAssign(self, node: vy_ast.AugAssign, ast: vy_ast.Module, context: ASTContext):
        # Check for storage variable on LHS of assignment
        lhs = node.target
        contract_vars = lhs.get_descendants(
            vy_ast.Attribute, {"value.id": "self"}, include_self=True
        )

        cairo_typ = convert_node_type_definition(node.target)

        if contract_vars:
            # Store original variable name
            var_name = node.target.attr
            # Create temporary variable for assignment of storage read value
            temp_name_node = generate_name_node(context.reserve_id())
            temp_name_node._metadata["type"] = cairo_typ

            value_node = vy_ast.Name(
                node_id=context.reserve_id(), id=f"{var_name}_STORAGE", ast_type="Name"
            )

            # Create storage read node
            storage_read_node = CairoStorageRead(
                node_id=context.reserve_id(),
                parent=ast,
                targets=[temp_name_node],  # type: ignore
                value=value_node,
                ast_type="CairoStorageRead",
            )
            storage_read_node._children.add(value_node)
            storage_read_node._children.add(temp_name_node)

            # Convert `AugAssign` operation to `BinOp`
            binop_node = vy_ast.BinOp(
                node_id=context.reserve_id(),
                op=node.op,
                left=temp_name_node,
                right=node.value,
                ast_type="BinOp",
            )
            binop_node._children.add(node.op)
            binop_node._children.add(temp_name_node)
            binop_node._children.add(node.value)
            binop_node._metadata["type"] = cairo_typ

            # Create new variable and assign RHS
            rhs_name_node = generate_name_node(context.reserve_id())
            rhs_name_node._metadata["type"] = cairo_typ

            rhs_assignment_node = vy_ast.Assign(
                node_id=context.reserve_id(),
                targets=[rhs_name_node],
                value=binop_node,
                ast_type="Assign",
            )
            rhs_assignment_node._children.add(rhs_name_node)
            rhs_assignment_node._children.add(binop_node)
            rhs_assignment_node._metadata["type"] = cairo_typ
            set_parent(binop_node, rhs_assignment_node)

            # Add storage write node to body of function

            fn_node = node.get_ancestor(vy_ast.FunctionDef)

            # Create storage write node
            contract_var = contract_vars.pop()

            value_node = vy_ast.Name(
                node_id=context.reserve_id(), id=rhs_name_node.id, ast_type="Name"
            )

            storage_write_node = CairoStorageWrite(
                node_id=context.reserve_id(),
                parent=fn_node,
                targets=[  # type: ignore
                    vy_ast.Name(
                        node_id=context.reserve_id(),
                        id=f"{contract_var.attr}_STORAGE",
                        ast_type="Name",
                    )
                ],
                value=value_node,
            )
            storage_write_node._children.add(value_node)

            # Update type
            storage_write_node._metadata["type"] = cairo_typ
            storage_write_node.value._metadata["type"] = cairo_typ
            storage_write_node.target._metadata["type"] = cairo_typ

            # Replace assign node with RHS
            ast.replace_in_tree(node, storage_write_node)
            # Add RHS node before storage write node
            insert_statement_before(rhs_assignment_node, storage_write_node, fn_node)
            insert_statement_before(storage_read_node, rhs_assignment_node, fn_node)
