from string import ascii_lowercase as alc

from vyro.cairo.types import CairoMappingDefinition, CairoTypeDefinition

INDENT = "    "


def generate_storage_var_stub(storage_var_name: str, typ: CairoTypeDefinition):
    modified_name = f"{storage_var_name}_STORAGE"
    return_var_name = f"{modified_name}_ret"

    args_str = ""
    if isinstance(typ, CairoMappingDefinition):
        args = []
        for i in range(len(typ.key_types)):
            # Note: will work until 26 keys
            var_name = alc[i]
            type_str = str(typ.key_types[i])
            args.append(f"{var_name} : {type_str}")
        args_str = ", ".join(args)
        return_typ = typ.value_type

    else:
        return_typ = typ

    return f"""
@storage_var
func {modified_name}({args_str}) -> ({return_var_name} : {return_typ}):
end
    """
