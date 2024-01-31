from pydantic import BaseModel
from models.db.common import Id


class LoginUserRequest(BaseModel):
    user_id: Id
    password: str


class LoginUserResponse(BaseModel):
    jwt: str
