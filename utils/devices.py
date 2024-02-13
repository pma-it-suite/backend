import logging
from config.db import get_devices_collection
from models.db.common import Id, RaisesException
from models.db.device import Device
from utils.errors import DefaultDataNotFoundException

devices_collection = get_devices_collection()


def get_device_from_db(device_id: Id) -> dict | None:
    device = devices_collection.find_one({'_id': device_id})
    return device


def get_device_from_db_or_404(device_id: Id) -> Device | RaisesException:
    device = get_device_from_db(device_id)
    if not device:
        raise DefaultDataNotFoundException(
            detail=f"No device found with id {device_id}")
    return Device(**device)
