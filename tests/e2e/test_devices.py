import logging
from typing import Dict, Callable, Any
import pytest
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse
from icecream import ic
import models.db.user as user_models
from models.db.auth import Token

from app import app

client = TestClient(app)


@pytest.fixture
def get_register_device_req() -> Dict[str, Any]:
    def __get_register_device_req(
            device_name: str, user_id: str, issuer_id: str) -> Dict[str, Any]:
        return {"device_name": device_name,
                "user_id": user_id, "issuer_id": issuer_id}

    return __get_register_device_req


def check_register_device_response_valid(response: HTTPResponse) -> bool:
    """
    Checks that the raw server response is valid.
    Returns true if all checks pass, else false
    """
    try:
        assert response.status_code == 201
        assert "device_id" in response.json()
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def get_device_register_endpoint_string() -> str:
    return "/devices/register"


class TestRegisterDevice:
    def test_register_device_successful(self, registered_user: user_models.DbUser, get_register_device_req: Callable[[
                                        str, str, str], Dict[str, Any]], get_user_from_db, get_device_from_db) -> None:
        """
        Tries to register a device for an existing user
        """
        json_dict = get_register_device_req(
            "test_device",
            registered_user.get_id(),
            registered_user.get_id())
        endpoint_url = get_device_register_endpoint_string()
        response = client.post(endpoint_url, json=json_dict)

        assert check_register_device_response_valid(response)

        user = get_user_from_db(registered_user.get_id())
        assert response.json().get("device_id") in user.device_ids

        device = get_device_from_db(response.json().get("device_id"))
        assert device.user_id == registered_user.get_id()

    def test_register_device_fail_no_user(self, unregistered_user: user_models.DbUser, get_register_device_req: Callable[[
            str, str, str], Dict[str, Any]]) -> None:
        """
        Tries to register a device for a non-existing user, failing
        """
        json_dict = get_register_device_req(
            "test_device",
            unregistered_user.get_id(),
            unregistered_user.get_id())
        endpoint_url = get_device_register_endpoint_string()
        response = client.post(endpoint_url, json=json_dict)

        assert not check_register_device_response_valid(response)
