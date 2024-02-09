from config.db import get_commands_collection
from models.db.common import Id, RaisesException
from models.db.command import Command
from utils.errors import DefaultDataNotFoundException

commands_collection = get_commands_collection()


def get_command_from_db(command_id: Id) -> dict | None:
    command = commands_collection.find_one({'_id': command_id})
    return command


def get_command_from_db_or_404(command_id: Id) -> Command | RaisesException:
    command = get_command_from_db(command_id)
    if not command:
        raise DefaultDataNotFoundException(
            detail=f"No command found with id {command_id}")
    return Command(**command)

def get_many_commands_from_db(command_ids: list[Id]) -> list[dict | None]:
    filter = {"_id": {"$in": command_ids}}
    response = [x for x in commands_collection.find(filter)]
    return response

def get_many_commands_from_db_or_404(command_ids: list[Id]) -> list[Command] | RaisesException:
    commands = get_many_commands_from_db(command_ids)
    if len(commands) == 0:
        raise DefaultDataNotFoundException(
            detail=f"No commands found with ids {command_ids}")
    return [Command(**x) for x in commands]