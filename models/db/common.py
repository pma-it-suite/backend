from typing import NoReturn, Optional
from pydantic import Field, BaseModel

Id = str
EmailStr = str
RaisesException = NoReturn


class BaseModelWithId(BaseModel):
    id: Optional[Id] = Field(default=None, alias="_id")

    def get_id(self) -> str:
        return self.id
