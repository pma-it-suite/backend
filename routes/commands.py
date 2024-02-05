from fastapi import APIRouter
from config.db import get_users_collection, get_commands_collection
from bson.objectid import ObjectId
from models.db.command import CommandStatus, Command
import models.routes.users as models
from models.db.common import Id, EmailStr, RaisesException
from models.db.user import DbUser, RawUser
from utils.errors import (
    DatabaseNotModified,
    DefaultDataNotFoundException,
    InvalidDataException,
    InvalidPasswordException,
)
from utils.users import validate_user_id_or_throw, get_db_user_or_throw_if_404, register_user_to_db
from utils.auth import get_auth_token_from_user_id, hash_and_compare
import utils.errors as exceptions
import models.routes.commands as cmd_models
from pymongo import DESCENDING

router = APIRouter()
ROUTE_BASE = "/commands"
TAG = "commands"

# Initialize MongoDB client
users_collection = get_users_collection()
commands_collection = get_commands_collection()


@router.get(
    ROUTE_BASE + "/get",
    response_model=cmd_models.batch_commands.BatchCommandsResponse,
    summary="Get batch commands",
    tags=[TAG],
    status_code=200,
)
async def get_batch_cmds(user_id: Id):
    validate_user_id_or_throw(user_id)

    user = get_db_user_or_throw_if_404(user_id)
    return models.get_user.GetUserResponse(**user.dict())


@router.patch(
    ROUTE_BASE + "/status",
    response_model=cmd_models.command_status.CommandStatusResponse,
    summary="Change command status",
    tags=[TAG],
    status_code=200,
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

    return cmd_models.command_status.CommandStatusResponse()


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
    status_code=200,
)
async def create_command(request: cmd_models.create_command.CreateCommandRequest):
    command_data = {
        "status": CommandStatus.PENDING,  # default status
        "args": request.args,
        "name": request.name,
        "device_id": request.device_id,
        "issuer_id": request.issuer_id
    }
    command = Command(**command_data)

    result = commands_collection.insert_one(command.dict())
    if not result:
        raise DatabaseNotModified(detail="Failed to create command")
    
    return cmd_models.create_command.CreateCommandResponse(command_id=result.inserted_id)


# @commands_routes.route('/batch', methods=['POST'])
# @cross_origin()
# def create_commands_for_multiple_devices():
#     try:
#         data = request.json
#         user_id = data.get("user_id")
#         name = data.get("name")
#         args = data.get("args")

#         if not user_id:
#             return jsonify({
#                 "status": "error",
#                 "message": "User ID is required"
#             }), 400
#         if not name:
#             return jsonify({
#                 "status": "error",
#                 "message": "Command name is required"
#             }), 400

#         user = members_collection.find_one({"_id": user_id})

#         if not user:
#             return jsonify({
#                 "status": "error",
#                 "message": "User not found"
#             }), 404

#         devices = user.get("devices", [])
#         print("devices: ", devices)
#         device_ids = user.get("device_ids", [])
#         print("device_ids: ", device_ids)
#         new_commands = []
#         for device in devices:
#             command_data = {
#                 "_id": str(uuid.uuid4()),
#                 "name": name,
#                 "args": args,
#                 "device_id": device["device_id"],
#                 "status": "pending"  # default status
#             }
#             print(command_data)
#             commands_collection.insert_one(command_data)
#             new_commands.append(command_data)

#         return jsonify({
#             "status": "OK",
#             "message": "Commands created successfully",
#             "newCommands": new_commands
#         }), 201

#     except Exception as e:
#         print(e)
#         return jsonify({
#             "status": "error",
#             "message": "An error occurred"
#         }), 500


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
