import logging
from typing import Dict, Callable, Any
import pytest
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse
from icecream import ic
from models.db.command import Command, CommandNames
from models.db.common import Id
import models.db.user as user_models
from models.db.auth import Token

from app import app
from models.routes.commands.create_command import CreateCommandRequest

client = TestClient(app)


@pytest.fixture
def get_get_command_req():
    def __get_get_command_req(command_id: str) -> Dict[str, Any]:
        return {"command_id": command_id}

    return __get_get_command_req


@pytest.fixture
def get_register_command_req() -> Dict[str, Any]:
    def __get_register_command_req(
            device_id: Id, name: CommandNames, issuer_id: Id) -> Dict[str, Any]:
        req = CreateCommandRequest(
            **{"device_id": device_id, "name": name, "issuer_id": issuer_id})
        logging.debug(f"req: {req}")
        return req.model_dump()

    return __get_register_command_req


def check_create_command_response_valid(response: HTTPResponse) -> bool:
    """
    Checks that the raw server response is valid.
    Returns true if all checks pass, else false
    """
    try:
        assert response.status_code == 201
        assert "command_id" in response.json()
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def check_command_dicts_same(
        cmd: Command, dict_to_check: Dict[str, Any]) -> bool:
    cmd_dict = cmd.dict()
    for key in cmd_dict.keys():
        if key == "id":
            continue
        if cmd_dict.get(key) != dict_to_check.get(key):
            return False
    return True


def check_get_command_response_valid(
        response: HTTPResponse, command: Command) -> bool:
    try:
        assert response.status_code == 200
        command_resp = response.json().get("command")
        assert check_command_dicts_same(command, command_resp)
        return True
    except Exception as error:
        debug_msg = f"failed at: {error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def check_get_batch_commands_response_valid(
        response: HTTPResponse, commands: list[Command]) -> bool:
    try:
        assert response.status_code == 200
        command_resp = response.json().get("commands")
        # match up commands with the response json commands by id
        commands.sort(key=lambda x: x.get_id())
        command_resp.sort(key=lambda x: x.get("_id"))
        for cmd, resp in zip(commands, command_resp):
            assert check_command_dicts_same(cmd, resp)
        return True
    except Exception as error:
        debug_msg = f"failed at: {error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def get_command_endpoint_str() -> str:
    return "/commands"


class TestGetCommand:
    def test_get_command_success(
            self, registered_command, get_get_command_req):
        params = get_get_command_req(registered_command.get_id())
        endpoint_url = get_command_endpoint_str() + "/get"
        response = client.get(endpoint_url, params=params)
        assert check_get_command_response_valid(response, registered_command)

    def test_get_command_no_command_fail(
            self, unregistered_command, get_get_command_req):
        params = get_get_command_req(unregistered_command.get_id())
        endpoint_url = get_command_endpoint_str() + "/get"
        response = client.get(endpoint_url, params=params)
        assert not check_get_command_response_valid(
            response, unregistered_command)
        assert "No command found" in response.json().get("detail")
        assert unregistered_command.get_id() in response.json().get("detail")


class TestGetBatchCommands:
    def test_get_batch_commands_success(self, registered_command_factory):
        cmds = []
        for _ in range(5):
            cmds.append(registered_command_factory())
        endpoint_url = get_command_endpoint_str() + "/batch/get"
        json = {"command_ids": [cmd.get_id() for cmd in cmds]}
        response = client.post(endpoint_url, json=json)
        assert check_get_batch_commands_response_valid(response, cmds)

    def test_get_batch_commands_fail_no_data(
            self, unregistered_command_factory):
        cmds = []
        for _ in range(5):
            cmds.append(unregistered_command_factory())
        endpoint_url = get_command_endpoint_str() + "/batch/get"
        json = {"command_ids": [cmd.get_id() for cmd in cmds]}
        response = client.post(endpoint_url, json=json)
        assert response.status_code == 404
        assert not check_get_batch_commands_response_valid(response, cmds)


class TestCreateCommand:
    def test_create_command_success(
            self, registered_device, registered_user, get_register_command_req, get_device_from_db):
        json_dict = get_register_command_req(
            registered_device.get_id(),
            CommandNames.UPDATE,
            registered_user.get_id())
        endpoint_url = get_command_endpoint_str() + "/create"
        response = client.post(endpoint_url, json=json_dict)

        assert check_create_command_response_valid(response)

        device = get_device_from_db(registered_device.get_id())
        assert response.json().get("command_id") in device.command_ids