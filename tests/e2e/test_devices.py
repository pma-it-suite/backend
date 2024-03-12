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
            device_name: str, user_id: str, issuer_id: str, user_secret: str) -> Dict[str, Any]:
        return {"device_name": device_name,
                "user_id": user_id, "issuer_id": issuer_id, "user_secret": user_secret}

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
    def test_register_device_successful(self, get_register_device_req: Callable[[
                                        str, str, str], Dict[str, Any]], get_user_from_db, get_device_from_db, registered_user_orig) -> None:
        """
        Tries to register a device for an existing user
        """
        registered_user, registered_user_form = registered_user_orig
        device_secret = Token.get_enc_token_str_from_dict(
            {"secret": registered_user_form.raw_user_secret, "user_id": registered_user.get_id()})
        json_dict = get_register_device_req(
            "test_device",
            registered_user.get_id(),
            registered_user.get_id(),
            device_secret)
        endpoint_url = get_device_register_endpoint_string()
        response = client.post(
            endpoint_url,
            json=json_dict)

        assert check_register_device_response_valid(response)

        user = get_user_from_db(registered_user.get_id())
        assert response.json().get("device_id") in user.device_ids

        device = get_device_from_db(response.json().get("device_id"))
        assert device.user_id == registered_user.get_id()

    def test_register_device_fail_no_user(self, unregistered_user: user_models.DbUser, get_register_device_req: Callable[[
            str, str, str], Dict[str, Any]], get_header_dict_from_user_id, registered_user) -> None:
        """
        Tries to register a device for a non-existing user, failing
        """
        json_dict = get_register_device_req(
            "test_device",
            unregistered_user.get_id(),
            unregistered_user.get_id(),
            "test")
        endpoint_url = get_device_register_endpoint_string()
        response = client.post(
            endpoint_url,
            json=json_dict,
            headers=get_header_dict_from_user_id(
                registered_user.get_id()))

        assert not check_register_device_response_valid(response)


class TestGetDevice:
    def test_get_device_successful(
            self, registered_device_factory, get_device_from_db, get_header_dict_from_user_id, registered_user):
        """
        Tries to query a registered device from the database
        succesfully.
        """
        registered_device = registered_device_factory(registered_user.get_id())
        endpoint_url = "/devices/get"
        response = client.get(
            endpoint_url, params={
                "device_id": registered_device.get_id()}, headers=get_header_dict_from_user_id(registered_device.user_id))

        assert response.status_code == 200
        assert "device" in response.json()
        assert response.json().get("device").get("_id") == registered_device.get_id()

    def test_get_device_fail_404_no_device(
            self, unregistered_device, get_header_dict_from_user_id, registered_user):
        """
        Tries to query a nonexistent device expecting 404 failure.
        """
        endpoint_url = "/devices/get"
        response = client.get(
            endpoint_url, params={
                "device_id": unregistered_device.get_id()}, headers=get_header_dict_from_user_id(registered_user.get_id()))

        assert response.status_code == 404
        assert "detail" in response.json()
        assert response.json().get(
            "detail") == f"No device found with id {unregistered_device.get_id()}"


class TestGetDevices:
    def test_get_devices_by_user_id_successful(
            self, registered_user, registered_device_factory, get_device_from_db, get_header_dict_from_user_id):
        """
        Tries to query a registered device from the database
        succesfully.
        """
        registered_device = registered_device_factory(registered_user.get_id())
        endpoint_url = "/devices/get/all"
        response = client.get(
            endpoint_url, params={
                "user_id": registered_user.get_id()}, headers=get_header_dict_from_user_id(registered_user.get_id()))

        assert response.status_code == 200
        assert "devices" in response.json()
        assert len(response.json().get("devices")) == 1
        assert response.json().get("devices")[0].get(
            "_id") == registered_device.get_id()

    def test_get_devices_by_user_id_404_no_user_fail(
            self, unregistered_user, get_header_dict_from_user_id):
        """
        Tries to query a nonexistent device expecting 404 failure.
        """
        endpoint_url = "/devices/get/all"
        response = client.get(
            endpoint_url, params={
                "user_id": unregistered_user.get_id()}, headers=get_header_dict_from_user_id(unregistered_user.get_id()))

        assert response.status_code == 404
        assert "detail" in response.json()
        assert response.json().get(
            "detail") == f"no user found with user identifier: {unregistered_user.get_id()}"
