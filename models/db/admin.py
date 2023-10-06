from pydantic import BaseModel
from typing import Optional, List
from .metadata import Metadata
from .common import Id

class Admin(BaseModel):
    _id: Optional[Id]
    name: Optional[str]
    email: Optional[str]
    user_secret_hash: Optional[str]
    password_hash: Optional[str]
    subscription_id: Optional[Id]
    tenant_id: Optional[Id]
    device_ids: Optional[List[Id]]
    role_id: Optional[Id]
    metadata: Optional[Metadata]

class _Admin(BaseModel):
    _id: Id
    name: str
    email: str
    user_secret_hash: str
    password_hash: str
    subscription_id: Id
    tenant_id: Id
    device_ids: List[Id]
    role_id: Id
    metadata: Optional[Metadata]
