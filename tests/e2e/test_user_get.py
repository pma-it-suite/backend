# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for the get user info endpoint
"""
import logging
from typing import Dict, Any, Callable
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse
from icecream import ic

from app import app
import models.routes.users.get_user as user_models
import models.db.user as db_user_models

client = TestClient(app)


def check_get_user_response_valid(response: HTTPResponse) -> bool:
    """
    Checks that the raw server response is valid.
    Returns true if all checks pass, else false
    """
    try:
        fields_to_check = [
            "name",
            "email",
            "metadata",
            "subscription_id",
            "tenant_id",
            "role_id",
        ]
        for field in fields_to_check:
            assert field in response.json()

        fields_to_check_not_in = [
            "password_hash",
            "user_secret_hash",
        ]
        for field in fields_to_check_not_in:
            assert field not in response.json()
        assert response.status_code == 200
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def check_user_matches_response(
        response: HTTPResponse,
        user_data: db_user_models.DbUserRedacted) -> bool:
    """
    Checks that the user data from the response is the same as
    the given user model passed.
    """
    try:
        user_data_dict = user_data.dict()
        response_dict = response.json()

        for key in [x for x in response_dict]:
            assert user_data_dict[key] == response_dict[key]
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def get_user_query_endpoint_string() -> str:
    """
    Returns the endpoint url string for "get user"
    """
    return "/users/get"


class TestGetRegularUser:
    def test_get_user_success(
        self, registered_user_redacted: db_user_models.DbUserRedacted,
        get_identifier_dict_from_user: Callable[
            [db_user_models.DbUserRedacted], Dict[str, Any]], get_header_dict_from_user_id):
        """
        Tries to query a registered user from the database
        succesfully.
        """
        json_dict = get_identifier_dict_from_user(registered_user_redacted)
        endpoint_url = get_user_query_endpoint_string()
        response = client.get(
            endpoint_url,
            params=json_dict,
            headers=get_header_dict_from_user_id(
                registered_user_redacted.get_id()))

        assert check_get_user_response_valid(response)
        assert check_user_matches_response(response, registered_user_redacted)

    def test_get_nonexistent_user_fail(
        self, unregistered_user: db_user_models.DbUserRedacted,
        get_identifier_dict_from_user: Callable[
            [db_user_models.DbUserRedacted], Dict[str, Any]], get_header_dict_from_user_id):
        """
        Tries to query a nonexistent user expecting 404 failure.
        """
        json_dict = get_identifier_dict_from_user(unregistered_user)
        endpoint_url = get_user_query_endpoint_string()
        response = client.get(
            endpoint_url,
            params=json_dict,
            headers=get_header_dict_from_user_id(
                unregistered_user.get_id()))

        assert not check_get_user_response_valid(response)
        assert response.status_code == 404

    def test_get_user_no_data_failure(self):
        """
        Try to query a valid user but sending no data, expecting a 422 failure
        """
        empty_json_dict = {}
        endpoint_url = get_user_query_endpoint_string()
        response = client.get(
            endpoint_url,
            params=empty_json_dict,
            headers={
                "token": ""})

        assert not check_get_user_response_valid(response)
        assert response.status_code == 422
