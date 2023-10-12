from typing import Optional
from .common import Id, BaseModelWithId, AutoName
from enum import auto


class CommandNames(AutoName):
    UPDATE = auto()


class Command(BaseModelWithId):
    status: str
    args: Optional[str]
    name: CommandNames
    issuer_id: Id
