from models.db.common import Id, BaseModelWithConfig, BaseModelWithId
from models.db.command import Command
from typing import Optional


class GetCommandResponse(BaseModelWithConfig):
    command: Command
