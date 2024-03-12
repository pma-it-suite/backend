from fastapi import APIRouter, Depends
from config.db import get_users_collection, get_devices_collection
from models.db.auth import Token
from models.db.common import Id
from models.db.device import Device
import models.routes.devices as device_models
from utils.auth import get_user_id_from_header_and_check_existence, hash_and_compare
from utils.devices import get_device_from_db_or_404, get_many_devices_from_db_or_404_by_user_id
from utils.errors import DatabaseNotModified, InvalidPasswordException
from utils.users import get_db_user_or_throw_if_404
import uuid

router = APIRouter()
ROUTE_BASE = "/devices"
TAG = "devices"

devices_collection = get_devices_collection
users_collection = get_users_collection


@router.post(
    ROUTE_BASE + "/register",
    response_model=device_models.register_device.RegisterDeviceResponse,
    summary="Register a device for a given user",
    tags=[TAG],
    status_code=201,
)
async def register_device(
        request: device_models.register_device.RegisterDeviceRequest):
    devices_collection_handle = devices_collection()
    users_collection_handle = users_collection()
    user_id = request.user_id
    user = get_db_user_or_throw_if_404(user_id)

    # for now (TODO @felipearce) only the user can register a device for itself
    # eventually admins should be able to

    secret = user.user_secret_hash
    secret_data = Token.get_dict_from_enc_token_str(request.user_secret)
    (user_id_from_secret, raw_secret) = (
        secret_data.get('user_id'), secret_data.get('secret'))

    # TODO @felipearce: make the jwt data typed
    if not all([user_id_from_secret == user_id, raw_secret is not None,
                hash_and_compare(raw_secret, secret)]):
        msg = f"invalid secret for user_id: {user_id}"
        raise InvalidPasswordException(detail=msg)

    device = Device(**{"name": request.device_name, "user_id": user_id})
    device_id = device.get_id()

    user.device_ids.append(device_id)
    response = users_collection_handle.update_one({"_id": user_id},
                                                  {"$set": {
                                                      "device_ids": user.device_ids
                                                  }})

    if response.modified_count == 0:
        raise DatabaseNotModified(detail="Failed update user with device")

    response = devices_collection_handle.insert_one(device.dict())
    if not response.inserted_id:
        raise DatabaseNotModified(
            detail="Failed to create device with name " +
            request.device_name)

    return device_models.register_device.RegisterDeviceResponse(
        device_id=response.inserted_id)


@router.get(
    ROUTE_BASE + "/get",
    response_model=device_models.get_device.GetDeviceResponse,
    summary="Get a device by id",
    tags=[TAG],
    status_code=200,
)
async def fetch_device(device_id: Id, user_id: Id = Depends(get_user_id_from_header_and_check_existence)):
    # TODO @felipearce: add check if user is allowed to see this device
    device = get_device_from_db_or_404(device_id)
    return device_models.get_device.GetDeviceResponse(device=device)


@router.get(
    ROUTE_BASE + "/get/all",
    response_model=device_models.get_devices.GetDevicesResponse,
    summary="Get devices by user id",
    tags=[TAG],
    status_code=200,
)
async def fetch_devices(user_id: Id = Depends(get_user_id_from_header_and_check_existence)):
    # TODO @felipearce: add check if user is allowed to see this
    get_db_user_or_throw_if_404(user_id)
    devices = get_many_devices_from_db_or_404_by_user_id(user_id)
    return device_models.get_devices.GetDevicesResponse(devices=devices)
