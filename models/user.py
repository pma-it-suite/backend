from pydantic import BaseModel
from typing import Optional, Any
from .metadata import Metadata
from .common import Id


class Users(BaseModel):
    _id: Id
    name: str
    email: str
    metadata: Optional[Metadata]
    user_secret_hash: str
    password_hash: str
    subscription_id: Id
    tenant_id: Id
    device_ids: list[Id]
    role_id: Id
