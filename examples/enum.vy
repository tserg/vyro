# @version ^0.3.5

enum Roles:
    ADMIN
    STAFF
    USER


@external
@view
def is_staff(x: Roles) -> bool:
    return x in (Roles.ADMIN | Roles.STAFF)
