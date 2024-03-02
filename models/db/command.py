from typing import Optional
from .common import Id, BaseModelWithId, AutoName
from enum import auto


class CommandNames(AutoName):
    UPDATE = auto()
    TEST = auto()


class CommandStatus(AutoName):
    # command has started running
    RUNNING = auto()

    # command is waiting for some resource
    BLOCKED = auto()

    # command has exited successfully
    TERMINATED = auto()

    # command has exited with an error
    FAILED = auto()

    # command is ready but not running
    READY = auto()

    # command is waiting to be sent to the device's ready queue
    PENDING = auto()

    SENT = auto()

    RECEIVED = auto()


class Command(BaseModelWithId):
    status: CommandStatus
    args: Optional[str | None] = None
    name: CommandNames
    issuer_id: Id
    device_id: Id
