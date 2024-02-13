from models.db.common import Id
from routes.devices import register_device
from unittest.mock import MagicMock, patch
from models.routes.devices import RegisterDeviceRequest
import pytest

from utils.errors import DatabaseNotModified


@pytest.fixture
def get_register_request_factory():
    def __get_register_request(user_id: Id):
        return RegisterDeviceRequest(**{
            "device_name": "test_device",
            "user_id": user_id,
            "issuer_id": user_id
        })
    return __get_register_request


class TestRegisterDeviceUnit:
    @pytest.mark.asyncio
    async def test_register_device_user_update_fails(
            self, get_register_request_factory, registered_user):
        # Arrange
        request = get_register_request_factory(registered_user.get_id())

        @patch('routes.devices.users_collection')
        async def inner(mock_collection):
            db_response = MagicMock()
            db_response.modified_count = 0
            mock_collection.update_one.return_value = db_response

            # Act
            try:
                await register_device(request)
                assert False
            except DatabaseNotModified as e:
                return e
            except Exception as _:
                assert False

        exception = await inner()
        # Assert
        assert exception.status_code == 500
        assert exception.detail == "Failed update user with device"

    @pytest.mark.asyncio
    async def test_register_device_device_insert_fails(
            self, get_register_request_factory, registered_user):
        # Arrange
        request = get_register_request_factory(registered_user.get_id())

        @patch('routes.devices.devices_collection')
        async def inner(mock_collection):
            db_response = MagicMock()
            db_response.inserted_id = None
            mock_collection.insert_one.return_value = db_response

            # Act
            try:
                await register_device(request)
                assert False
            except DatabaseNotModified as e:
                return e
            except Exception as _:
                assert False

        exception = await inner()
        # Assert
        assert exception.status_code == 500
        assert exception.detail == f"Failed to create device with name {request.device_name}"
