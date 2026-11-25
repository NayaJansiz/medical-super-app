import uuid
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints

Email = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        to_lower=True,
        max_length=320,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    ),
]
FullName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
]
NewPassword = Annotated[str, StringConstraints(min_length=8, max_length=128)]


class RegisterRequest(BaseModel):
    email: Email
    password: NewPassword
    full_name: FullName
    # Public registration may only create these two roles.
    role: Literal["patient", "student"]


class LoginRequest(BaseModel):
    email: Email
    password: Annotated[str, StringConstraints(min_length=1, max_length=128)]


class RoleUpdate(BaseModel):
    role: Literal[
        "patient",
        "doctor",
        "clinic_admin",
        "pharmacist",
        "student",
        "lab_staff",
        "super_admin",
    ]


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    role: str


class StatusOut(BaseModel):
    status: str
