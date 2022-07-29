from typing import List

from vyper import ast as vy_ast


def generate_name_node(node_id: int) -> vy_ast.Name:
    ret = vy_ast.Name(id=f"VYRO_VAR_{node_id}", node_id=node_id, ast_type="Name")
    return ret


def insert_statement_before(
    node: vy_ast.VyperNode, before: vy_ast.VyperNode, body: List[vy_ast.VyperNode]
):
    """
    Helper function to insert a new node before a given node in a list.

    Arguments
    ---------
    node : vy_ast.VyperNode
        Node to insert.
    before : vy_ast.VyperNode
        Node to insert before.
    body: List[vy_ast.VyperNode]
        List of a vy_ast.VyperNode that contains `before` and which `node` is to be added to.
    """
    node_idx = body.index(before)
    body.insert(node_idx, node)
