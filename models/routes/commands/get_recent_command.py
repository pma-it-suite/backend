from models.db.common import BaseModelWithConfig, Id
from models.db.command import Command


class GetRecentCommandRequest(BaseModelWithConfig):
    device_id: Id


class GetRecentCommandResponse(BaseModelWithConfig):
    command: Command
