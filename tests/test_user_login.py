# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=redefined-outer-name
#       - calling an internal fixture; pylint does not like this.
# pylint: disable=unsubscriptable-object
#       - false positive lint; pylint not updated to use advanced type hints yet
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint testing for attempting a user login

Tests both admin and regular user logins.
"""
import logging
from typing import Dict, Callable, Any
from config.db import get_users_collection
import pytest
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse
from icecream import ic
import models.db.user as user_models
from models.db.auth import Token

from app import app

client = TestClient(app)
"""
Helper functions go outside the class
"""


def get_user_login_endpoint_url() -> str:
    """
    Returns the url string for the user login endpoint.

    Might seem a little verbose and unnecessary but raw strings
    are always trouble and take away lots of readability and flexibility.
    """
    return "/users/login"


@pytest.fixture
def get_login_request_from_user(
    get_identifier_dict_from_user: Callable[[user_models.DbUser], Dict[str,
                                                                       Any]]
) -> Dict[str, Any]:
    """
    Internal fixture that returns a `Callable` function which creates
    and returns a valid json dict for the login endpoint given a user object.
    """
    def __get_login_request_from_user(
            user: user_models.DbUser) -> Dict[str, Any]:
        """
        Returned internal method that takes in a user object and uses
        the `get_identifier_dict_from_user` fixture in order to create
        and return the correct json data dict for the endpoint.
        """
        identifier_dict = get_identifier_dict_from_user(user)
        password = user.password_hash
        identifier_dict["password"] = password
        return identifier_dict

    return __get_login_request_from_user

@pytest.fixture
def get_login_request_from_user_form(
    get_identifier_dict_from_user: Callable[[user_models.DbUser], Dict[str,
                                                                       Any]]
) -> Dict[str, Any]:
    """
    Internal fixture that returns a `Callable` function which creates
    and returns a valid json dict for the login endpoint given a user object.
    """
    def __get_login_request_from_user(user_form) -> Dict[str, Any]:
        """
        Returned internal method that takes in a user object and uses
        the `get_identifier_dict_from_user` fixture in order to create
        and return the correct json data dict for the endpoint.
        """
        identifier_dict = {"user_id": user_form.email}
        password = user_form.raw_password
        identifier_dict["password"] = password
        return identifier_dict

    return __get_login_request_from_user



def check_user_login_response_valid(response: HTTPResponse) -> bool:
    """
    Helper function that checks if status code is valid
    """
    try:
        assert response.status_code == 200
        assert check_jwt_valid(response)
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}."
        logging.debug(debug_msg)
        return False


def check_jwt_valid(response: HTTPResponse) -> bool:
    response_dict = response.json()
    if 'jwt' in response_dict:
        enc_string = response_dict['jwt']
        valid_check = Token.check_if_valid(enc_string)
        return valid_check
    return False


class TestAttemptRegularDbUserLogin:
    def test_correct_pass(
        self, registered_user_orig: user_models.DbUser,
        get_login_request_from_user_form: Callable[[user_models.DbUser],
                                              Dict[str, Any]]):
        """
        Tries to login an existing user with valid credentials.
        Expects success and 200 response code
        """
        request_url = get_user_login_endpoint_url()
        _, registered_user_form = registered_user_orig
        json_payload = get_login_request_from_user_form(registered_user_form)
        ic(json_payload)
        response = client.post(request_url, json=json_payload)
        assert check_user_login_response_valid(response)

    def test_incorrect_pass(
        self, registered_user: user_models.DbUser,
        get_login_request_from_user: Callable[[user_models.DbUser],
                                              Dict[str, Any]]):
        """
        Tries to login with a user and incorrect pass.
        Expects failure and a 422 response code
        """
        request_url = get_user_login_endpoint_url()
        json_payload = get_login_request_from_user(registered_user)
        false_pass = 'aaaaaaaaaa'
        assert json_payload.get("password") != false_pass
        json_payload["password"] = false_pass
        ic(json_payload)
        response = client.post(request_url, json=json_payload)
        assert not check_user_login_response_valid(response)
        assert response.status_code == 422

    def test_nonexisting_user(
        self, unregistered_user: user_models.DbUser,
        get_login_request_from_user: Callable[[user_models.DbUser],
                                              Dict[str, Any]]):
        """
        Tries to login with a user that isn't in database.
        Expects failure and a 404 response code
        """
        request_url = get_user_login_endpoint_url()
        nonexistent_user_payload = get_login_request_from_user(
            unregistered_user)

        response = client.post(request_url, json=nonexistent_user_payload)
        ic(nonexistent_user_payload)

        ic(get_users_collection())

        assert not check_user_login_response_valid(response)
        ic(response)
        assert response.status_code == 404
