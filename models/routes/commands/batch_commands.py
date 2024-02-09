from models.db.common import Id, BaseModelWithConfig
from models.db.command import Command


class BatchCommandsRequest(BaseModelWithConfig):
    command_ids: list[Id]


class BatchCommandsResponse(BaseModelWithConfig):
    commands: list[Command]
