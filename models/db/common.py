from typing import NoReturn, Optional, Any
from pydantic import Field, BaseModel, validator
from uuid import uuid4
from enum import Enum

Id = str
EmailStr = str
RaisesException = NoReturn


class BaseModelWithId(BaseModel):
    id: Optional[Id] = Field(default="", alias="_id")

    def get_id(self) -> str:
        return self.id

    @validator("id", pre=True, always=True, check_fields=False)
    def set_id(cls, value) -> str:
        """
        Workaround on dynamic default setting for UUID.
        From: https://github.com/samuelcolvin/pydantic/issues/866
        """
        return value or _generate_uuid4_str()

    def dict(self, *args, **kwargs) -> dict[str, Any]:
        """
        Override the base `dict` method in order to get the mongo ID fix
        """
        parent_dict = super().dict(*args, **kwargs)
        parent_dict["_id"] = self.get_id()
        return parent_dict


class AutoName(Enum):
    """
    Hacky but abstracted-enough solution to the dumb enum naming problem that
    python has. Basically returns enums in string form when referenced by value
    """

    # since this is a funky should-be-private method, we have to break
    # a couple of lint rules
    # pylint: disable=unused-argument, no-self-argument
    def _generate_next_value_(name, start, count, last_values):
        """
        Returns name of enum rather than assigned value.
        """
        return name


def _generate_uuid4_str() -> str:
    """
    Generates a string representation of a UUID4.
    """
    return str(uuid4())
