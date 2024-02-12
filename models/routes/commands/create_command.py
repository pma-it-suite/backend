from typing import Optional
from models.db.common import BaseModelWithConfig, Id
from models.db.command import Command, CommandNames


class CreateCommandRequest(BaseModelWithConfig):
    device_id: Id
    name: CommandNames
    args: Optional[str|None] = None
    issuer_id: Id


class CreateCommandResponse(BaseModelWithConfig):
    command_id: Id
