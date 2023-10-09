from pydantic import BaseModel
from models.db.common import Id


class RegisterUserRequest(BaseModel):
    name: str
    email: str
    raw_password: str
    subscription_id: Id
    tenant_id: Id
    role_id: Id


class RegisterUserResponse(BaseModel):
    pass
