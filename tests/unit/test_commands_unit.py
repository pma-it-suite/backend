import logging
from models.db.command import CommandNames
from models.db.common import Id
from models.routes.commands.create_batch import CreateBatchRequest
from routes.commands import create_commands_for_multiple_devices
from unittest.mock import MagicMock, patch
import pytest

from utils.errors import DatabaseNotModified


@pytest.fixture
def get_register_request_factory():
    def __get_register_request(user_id: Id, device_ids: list[Id]):
        return CreateBatchRequest(**{
            "device_ids": device_ids,
            "name": CommandNames.UPDATE,
            "issuer_id": user_id
        })
    return __get_register_request


class TestRegisterCommandBatchUnit:
    @pytest.mark.asyncio
    async def test_register_command_device_update_fails(
            self, get_register_request_factory, registered_device_factory, registered_user):
        # Arrange
        devices = [registered_device_factory() for _ in range(2)]
        request = get_register_request_factory(
            registered_user.get_id(), [
                device.get_id() for device in devices])

        @patch('routes.commands.commands_collection')
        async def inner(mock_collection):
            db_response = MagicMock()
            db_response.inserted_ids = None
            mock_collection.insert_many.return_value = db_response

            # Act
            try:
                await create_commands_for_multiple_devices(request)
                assert False
            except DatabaseNotModified as e:
                return e
            except Exception as e:
                logging.debug(e)
                assert False

        exception = await inner()
        # Assert
        assert exception.status_code == 500
        assert exception.detail == "Failed to create batch commands"
