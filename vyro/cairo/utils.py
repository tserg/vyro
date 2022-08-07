INDENT = "    "


def generate_storage_var_stub(storage_var_name, return_typ):
    modified_name = f"{storage_var_name}_STORAGE"
    return_var_name = f"{modified_name}_ret"

    return f"""
@storage_var
func {modified_name}() -> ({return_var_name} : {return_typ}):
end
    """
