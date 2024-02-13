import logging
from fastapi import APIRouter
from config.db import get_devices_collection, get_users_collection, get_commands_collection
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
from utils.auth import get_auth_token_from_user_id, hash_and_compare
import utils.errors as exceptions
import models.routes.commands as cmd_models
from pymongo import DESCENDING

router = APIRouter()
ROUTE_BASE = "/commands"
TAG = "commands"

users_collection = get_users_collection()
commands_collection = get_commands_collection()
devices_collection = get_devices_collection()


@router.get(
    ROUTE_BASE + "/get",
    response_model=cmd_models.get_command.GetCommandResponse,
    summary="Get single command",
    tags=[TAG],
    status_code=200,
)
async def get_command(command_id: Id):
    return cmd_models.get_command.GetCommandResponse(
        command=utils.get_command_from_db_or_404(command_id))


@router.post(
    ROUTE_BASE + "/batch/get",
    response_model=cmd_models.batch_commands.BatchCommandsResponse,
    summary="Get batch commands",
    tags=[TAG],
    status_code=200,
)
async def get_batch_cmds(request: cmd_models.batch_commands.BatchCommandsRequest):
    commands = utils.get_many_commands_from_db_or_404(request.command_ids)
    return cmd_models.batch_commands.BatchCommandsResponse(commands=commands)


@router.patch(
    ROUTE_BASE + "/update/status",
    response_model=None,
    summary="Change command status",
    tags=[TAG],
    status_code=204,
)
async def update_command_status(
        request: cmd_models.command_status.CommandStatusRequest):
    command_id = request.command_id
    status = request.status

    if not commands_collection.find_one({'_id': command_id}):
        raise DefaultDataNotFoundException(
            detail=f"No command found with id {command_id}")

    updated = commands_collection.update_one({'_id': command_id},
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
        request: cmd_models.get_recent_command.GetRecentCommandRequest):
    device_id = request.device_id
    command = commands_collection.find_one(
        {
            'device_id': device_id,
            'status': CommandStatus.PENDING
        },
        sort=[('_id', DESCENDING)])

    if not command:
        raise DefaultDataNotFoundException(
            detail=f"No commands found for device {device_id}")

    return cmd_models.get_recent_command.GetRecentCommandResponse(
        {command: Command(**command)})


@router.post(
    ROUTE_BASE + "/create",
    response_model=cmd_models.create_command.CreateCommandResponse,
    summary="Create a command",
    tags=[TAG],
    status_code=201,
)
async def create_command(request: cmd_models.create_command.CreateCommandRequest):
    get_device_from_db_or_404(request.device_id)
    command_data = {
        "status": CommandStatus.PENDING,  # default status
        "args": request.args,
        "name": request.name,
        "device_id": request.device_id,
        "issuer_id": request.issuer_id
    }
    command = Command(**command_data)

    result = commands_collection.insert_one(command.dict())
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
async def create_commands_for_multiple_devices(request: cmd_models.create_batch.CreateBatchRequest):
    [get_device_from_db_or_404(device_id) for device_id in request.device_ids]

    devices = request.device_ids
    commands = [Command(**{"name": request.name,
                           "args": request.args,
                           "device_id": device_id,
                           "issuer_id": request.issuer_id,
                           "status": CommandStatus.PENDING  # default status
                           }) for device_id in devices]

    response = commands_collection.insert_many(
        [x.dict() for x in commands])

    if not response.inserted_ids or len(response.inserted_ids) != len(devices):
        raise DatabaseNotModified(detail="Failed to create batch commands")

    return cmd_models.create_batch.CreateBatchResponse(
        command_ids=response.inserted_ids)


# @commands_routes.route('/status', methods=['GET'])
# @cross_origin()
# def get_command_status():
#     try:
#         command_id = request.args.get('command_id')

#         if not command_id:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Command ID is required'
#             }), 400

#         # Query the command by its ID
#         command = commands_collection.find_one({'_id': command_id})

#         if not command:
#             return jsonify({
#                 'status': 'error',
#                 'message': 'No command found with this ID'
#             }), 404

#         return command['status'], 200

#     except Exception as e:
#         print(e)
#         return jsonify({
#             'status': 'error',
#             'message': 'An error occurred'
#         }), 500


# @commands_routes.route('/delete_pending', methods=['DELETE'])
# @cross_origin()
# def delete_pending_commands():
#     try:
#         # Delete all commands with status 'pending'
#         result = commands_collection.delete_many({'status': 'pending'})

#         if result.deleted_count == 0:
#             return jsonify({
#                 'status': 'OK',
#                 'message': 'No pending commands found'
#             }), 200

#         return jsonify({
#             'status':
#             'OK',
#             'message':
#             f'{result.deleted_count} pending command(s) deleted'
#         }), 200

#     except Exception as e:
#         print(e)
#         return jsonify({
#             'status': 'error',
#             'message': 'An error occurred'
#         }), 500
