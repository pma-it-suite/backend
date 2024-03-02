from typing import Optional
from .common import Id, BaseModelWithId, AutoName
from enum import auto


class CommandNames(AutoName):
    Update = auto()
    Test = auto()


class CommandStatus(AutoName):
    # command has started running
    Running = auto()

    # command is waiting for some resource
    Blocked = auto()

    # command has exited successfully
    Terminated = auto()

    # command has exited with an error
    Failed = auto()

    # command is ready but not running
    Ready = auto()

    # command is waiting to be sent to the device's ready queue
    Pending = auto()

    Sent = auto()

    Received = auto()


class Command(BaseModelWithId):
    status: CommandStatus
    args: Optional[str | None] = None
    name: CommandNames
    issuer_id: Id
    device_id: Id
