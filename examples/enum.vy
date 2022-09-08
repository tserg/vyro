# @version ^0.3.5

enum Roles:
    ADMIN
    STAFF
    USER

r: Roles

@external
@view
def is_staff(x: Roles) -> bool:
    return x in (Roles.ADMIN | Roles.STAFF)


@external
@view
def is_user(x: Roles) -> bool:
    return x == Roles.USER


@external
def set_r(x: Roles):
    self.r = x


@external
@view
def r_is_staff() -> bool:
    return self.r in (Roles.ADMIN | Roles.STAFF)
