import logging
from fastapi import APIRouter, Depends
from config.db import get_commands_collection, get_devices_collection
from bson.objectid import ObjectId
from models.db.command import CommandStatus, Command
import models.routes.users as models
from models.db.common import Id, EmailStr, RaisesException
from models.db.user import DbUser, RawUser
from utils.devices import get_device_from_db_or_404
from utils.errors import (
    DatabaseNotModified,
    DefaultDataNotFoundException,
    check_insert_was_successful,
    check_update_was_successful,
)
import utils.commands as utils
from utils.users import validate_user_id_or_throw, get_db_user_or_throw_if_404, register_user_to_db
from utils.auth import get_auth_token_from_user_id, get_user_id_from_header_and_check_existence, hash_and_compare
import utils.errors as exceptions
import models.routes.commands as cmd_models
from pymongo import ASCENDING, DESCENDING

router = APIRouter()
ROUTE_BASE = "/commands"
TAG = "commands"

commands_collection = get_commands_collection


@router.get(
    ROUTE_BASE + "/get",
    response_model=cmd_models.get_command.GetCommandResponse,
    summary="Get single command",
    tags=[TAG],
    status_code=200,
)
async def get_command(command_id: Id, user_id: Id = Depends(get_user_id_from_header_and_check_existence)):
    return cmd_models.get_command.GetCommandResponse(
        command=utils.get_command_from_db_or_404(command_id))


@router.post(
    ROUTE_BASE + "/batch/get",
    response_model=cmd_models.batch_commands.BatchCommandsResponse,
    summary="Get batch commands",
    tags=[TAG],
    status_code=200,
)
async def get_batch_cmds(request: cmd_models.batch_commands.BatchCommandsRequest, user_id: Id = Depends(get_user_id_from_header_and_check_existence)):
    commands = utils.get_many_commands_from_db_or_404(request.command_ids)
    return cmd_models.batch_commands.BatchCommandsResponse(commands=commands)


@router.get(
    ROUTE_BASE + "/batch/get/all",
    response_model=cmd_models.batch_commands_all.BatchAllCommandsResponse,
    summary="Get all batch commands for device id",
    tags=[TAG],
    status_code=200,
)
async def get_batch_cmds_all(device_id: Id, user_id: Id = Depends(get_user_id_from_header_and_check_existence)):
    commands_collection_handle = commands_collection()
    commands = commands_collection_handle.find({'device_id': device_id})
    if not commands:
        raise DefaultDataNotFoundException(
            detail=f"No commands found for device {device_id}")
    return cmd_models.batch_commands_all.BatchAllCommandsResponse(
        commands=commands)


@router.patch(
    ROUTE_BASE + "/update/status",
    response_model=None,
    summary="Change command status",
    tags=[TAG],
    status_code=204,
)
async def update_command_status(
        request: cmd_models.command_status.CommandStatusRequest):
    commands_collection_handle = commands_collection()
    command_id = request.command_id
    status = request.status

    if not commands_collection_handle.find_one({'_id': command_id}):
        raise DefaultDataNotFoundException(
            detail=f"No command found with id {command_id}")

    updated = commands_collection_handle.update_one({'_id': command_id},
                                                    {'$set': {
                                                        'status': status
                                                    }})
    if updated.modified_count == 0:
        raise DatabaseNotModified(detail=f"Failed to update command status")

    return


@router.get(
    ROUTE_BASE + "/recent",
    response_model=cmd_models.get_recent_command.GetRecentCommandResponse,
    summary="Get most recent command for a device",
    tags=[TAG],
    status_code=200,
)
async def get_most_recent_command(
        device_id: Id):
    commands_collection_handle = commands_collection()

    get_device_from_db_or_404(device_id)
    command = commands_collection_handle.find_one(
        {
            'device_id': device_id,
            'status': CommandStatus.Pending.value
        },
        sort=[('$natural', ASCENDING)])

    if not command:
        raise DefaultDataNotFoundException(
            detail=f"No commands found for device {device_id}")

    return cmd_models.get_recent_command.GetRecentCommandResponse(
        command=Command(**command))


@router.post(
    ROUTE_BASE + "/create",
    response_model=cmd_models.create_command.CreateCommandResponse,
    summary="Create a command",
    tags=[TAG],
    status_code=201,
)
async def create_command(request: cmd_models.create_command.CreateCommandRequest, user_id: Id = Depends(get_user_id_from_header_and_check_existence)):
    devices_collection = get_devices_collection()
    commands_collection_handle = commands_collection()
    get_device_from_db_or_404(request.device_id)
    command_data = {
        "status": CommandStatus.Pending,  # default status
        "args": request.args,
        "name": request.name,
        "device_id": request.device_id,
        "issuer_id": request.issuer_id
    }
    command = Command(**command_data)

    result = commands_collection_handle.insert_one(command.dict())
    check_insert_was_successful(result, "Failed to create command")
    command_id = result.inserted_id

    result = devices_collection.update_one({'_id': request.device_id}, {
                                           "$push": {"command_ids": command_id}})
    check_update_was_successful(
        result, "Failed to update device with new command id")

    return cmd_models.create_command.CreateCommandResponse(
        command_id=command_id)


@router.post(
    ROUTE_BASE + "/batch/create",
    response_model=cmd_models.create_batch.CreateBatchResponse,
    summary="Create a batch command for many devices",
    tags=[TAG],
    status_code=201,
)
async def create_commands_for_multiple_devices(request: cmd_models.create_batch.CreateBatchRequest, user_id: Id = Depends(get_user_id_from_header_and_check_existence)):
    commands_collection_handle = commands_collection()
    [get_device_from_db_or_404(device_id) for device_id in request.device_ids]

    devices = request.device_ids
    commands = [Command(**{"name": request.name,
                           "args": request.args,
                           "device_id": device_id,
                           "issuer_id": request.issuer_id,
                           "status": CommandStatus.Pending  # default status
                           }) for device_id in devices]

    response = commands_collection_handle.insert_many(
        [x.dict() for x in commands])

    if not response.inserted_ids or len(response.inserted_ids) != len(devices):
        raise DatabaseNotModified(detail="Failed to create batch commands")

    return cmd_models.create_batch.CreateBatchResponse(
        command_ids=response.inserted_ids)
