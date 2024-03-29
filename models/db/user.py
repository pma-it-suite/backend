from pydantic import BaseModel, Field
from typing import Optional, Any
from .metadata import Metadata
from .common import Id, BaseModelWithId, AutoName
from enum import auto


class UserTypeEnum(AutoName):
    USER = auto()
    ADMIN = auto()


class DbUser(BaseModelWithId):
    name: str
    email: str
    metadata: Optional[Metadata] = None
    user_secret_hash: str
    password_hash: str
    subscription_id: Id
    tenant_id: Id
    device_ids: list[Id]
    role_id: Id
    user_type: UserTypeEnum


class DbUserRedacted(BaseModelWithId):
    name: str
    email: str
    metadata: Optional[Metadata] = None
    subscription_id: Id
    tenant_id: Id
    role_id: Id


RawUser = dict[str, Any]
