from fastapi import APIRouter
from config.db import get_database, get_users_collection, get_devices_collection
from models.db.device import Device
import models.routes.devices as device_models
from utils.errors import DatabaseNotModified
from utils.users import get_db_user_or_throw_if_404
import uuid

router = APIRouter()
ROUTE_BASE = "/devices"
TAG = "devices"

users_collection = get_users_collection()
devices_collection = get_devices_collection()


@router.post(
    ROUTE_BASE + "/register",
    response_model=device_models.register_device.RegisterDeviceResponse,
    summary="Register a device for a given user",
    tags=[TAG],
    status_code=201,
)
async def register_device(
        request: device_models.register_device.RegisterDeviceRequest):
    user_id = request.user_id
    user = get_db_user_or_throw_if_404(user_id)

    # TODO @felipearce: add auth to this with header

    device = Device(**{"name": request.device_name, "user_id": user_id})
    device_id = device.get_id()

    user.device_ids.append(device_id)
    response = users_collection.update_one({"_id": user_id},
                                           {"$set": {
                                               "device_ids": user.device_ids
                                           }})

    if response.modified_count == 0:
        raise DatabaseNotModified(detail="Failed update user with device")

    response = devices_collection.insert_one(device.dict())
    if not response.inserted_id:
        raise DatabaseNotModified(
            detail="Failed to create device with name " +
            request.device_name)

    return device_models.register_device.RegisterDeviceResponse(
        device_id=response.inserted_id)
