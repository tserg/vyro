from vyper import ast as vy_ast


def generate_name_node(node_id: int) -> vy_ast.Name:
    return vy_ast.Name(
        id=f"VYRO_VAR_{node_id}",
        node_id=node_id,
    )
