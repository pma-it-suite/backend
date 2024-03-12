from typing import Optional
from pydantic import BaseModel
from models.db.common import Id, BaseModelWithConfig
from models.db.user import UserTypeEnum


class RegisterUserRequest(BaseModelWithConfig):
    name: str
    email: str
    raw_password: str
    subscription_id: Id
    tenant_id: Id
    role_id: Id
    user_type: UserTypeEnum
    raw_user_secret: Optional[str] = None


class RegisterUserResponse(BaseModel):
    user_id: Id
    jwt: str
    user_secret: str
