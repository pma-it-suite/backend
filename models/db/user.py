from pydantic import BaseModel
from typing import Optional, Any
from .metadata import Metadata
from .common import Id


class DbUser(BaseModel):
    _id: Optional[Id] = None
    name: Optional[str] = None
    email: Optional[str] = None
    metadata: Optional[Metadata] = None
    user_secret_hash: Optional[str] = None
    password_hash: Optional[str] = None
    subscription_id: Optional[Id] = None
    tenant_id: Optional[Id] = None
    device_ids: Optional[list[Id]] = None
    role_id: Optional[Id] = None


RawUser = dict[str, any]


class _DbUser(BaseModel):
    _id: Id
    name: str
    email: str
    metadata: Optional[Metadata] = None
    user_secret_hash: str
    password_hash: str
    subscription_id: Id
    tenant_id: Id
    device_ids: list[Id]
    role_id: Id
