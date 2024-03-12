import logging
from config.db import get_devices_collection
from models.db.common import Id, RaisesException
from models.db.device import Device
from utils.errors import DefaultDataNotFoundException


def get_device_from_db(device_id: Id) -> dict | None:
    devices_collection = get_devices_collection()
    device = devices_collection.find_one({'_id': device_id})
    return device


def get_device_from_db_or_404(device_id: Id) -> Device | RaisesException:
    device = get_device_from_db(device_id)
    if not device:
        raise DefaultDataNotFoundException(
            detail=f"No device found with id {device_id}")
    return Device(**device)


def get_many_devices_from_db_or_404_by_user_id(
        user_id: Id) -> list[Device] | RaisesException:
    devices_collection = get_devices_collection()
    devices = [x for x in devices_collection.find({'user_id': user_id})]
    if len(devices) == 0:
        raise DefaultDataNotFoundException(
            detail=f"No devices found with user id {user_id}")
    return [Device(**x) for x in devices]
