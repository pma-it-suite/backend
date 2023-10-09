from pydantic import BaseModel
from models.db.common import Id


class LoginUserRequest(BaseModel):
    user_id: Id
    password_hash: str


class LoginUserResponse(BaseModel):
    pass
