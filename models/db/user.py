from pydantic import BaseModel
from typing import Optional, Any
from .metadata import Metadata
from .common import Id


class Users(BaseModel):
    _id: Optional[Id]
    name: Optional[str]
    email: Optional[str]
    metadata: Optional[Metadata]
    user_secret_hash: Optional[str]
    password_hash: Optional[str]
    subscription_id: Optional[Id]
    tenant_id: Optional[Id]
    device_ids: Optional[list[Id]]
    role_id: Optional[Id]


class _Users(BaseModel):
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
