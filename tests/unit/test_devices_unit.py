from models.db.auth import Token
from models.db.common import Id
from routes.devices import register_device
from unittest.mock import MagicMock, patch
from models.routes.devices import RegisterDeviceRequest
import pytest

from utils.errors import DatabaseNotModified


@pytest.fixture
def get_register_request_factory():
    def __get_register_request(user_id: Id, secret: str):
        return RegisterDeviceRequest(**{
            "device_name": "test_device",
            "user_id": user_id,
            "issuer_id": user_id,
            "user_secret": secret
        })
    return __get_register_request


class TestRegisterDeviceUnit:
    @pytest.mark.asyncio
    async def test_register_device_user_update_fails(
            self, get_register_request_factory, registered_user_orig):
        # Arrange
        registered_user, registered_user_form = registered_user_orig
        device_secret = Token.get_enc_token_str_from_dict(
            {"secret": registered_user_form.raw_user_secret, "user_id": registered_user.get_id()})
        request = get_register_request_factory(
            registered_user.get_id(), device_secret)

        @patch('routes.devices.users_collection')
        async def inner(mock_collection):
            db_response = MagicMock()
            db_response.modified_count = 0
            nested_mock = MagicMock()
            nested_mock.update_one.return_value = db_response
            mock_collection.return_value = nested_mock

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
            self, get_register_request_factory, registered_user_orig):
        registered_user, registered_user_form = registered_user_orig
        device_secret = Token.get_enc_token_str_from_dict(
            {"secret": registered_user_form.raw_user_secret, "user_id": registered_user.get_id()})
        # Arrange
        request = get_register_request_factory(
            registered_user.get_id(), device_secret)

        @patch('routes.devices.devices_collection')
        async def inner(mock_collection):
            db_response = MagicMock()
            db_response.inserted_id = None
            nested_mock = MagicMock()
            nested_mock.insert_one.return_value = db_response
            mock_collection.return_value = nested_mock

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
