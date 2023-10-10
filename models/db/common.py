from typing import NoReturn, Optional, Any
from pydantic import Field, BaseModel, validator
from uuid import uuid4

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


def _generate_uuid4_str() -> str:
    """
    Generates a string representation of a UUID4.
    """
    return str(uuid4())
