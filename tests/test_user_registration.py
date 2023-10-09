# pylint: disable=no-self-use
#       - pylint test classes must pass self, even if unused.
# pylint: disable=logging-fstring-interpolation
#       - honestly just annoying to use lazy(%) interpolation.
"""
Endpoint tests for user registration.
"""
import logging
from typing import Dict, Any
from fastapi.testclient import TestClient
from requests.models import Response as HTTPResponse

from app import app
import models.routes.users as user_models

client = TestClient(app)


def generate_bad_user_data_json(
    user_form: user_models.register_user.RegisterUserRequest
) -> Dict[str, Any]:
    """
    Generates an invalid user registration form dict to be sent as json.

    Does this by swapping out every value for an int or string of itself
    """
    user_dict = user_form.dict()
    for key, value in user_dict.items():
        try:
            assert not isinstance(value, int)
            assert not isinstance(value, float)
            new_val = int(value)
        except:  # pylint: disable=bare-except
            new_val = str(value)
        user_dict[key] = new_val
    return user_dict


def get_reg_user_json_from_form(
        user_reg_form: user_models.UserRegistrationForm) -> Dict[str, Any]:
    """
    Returns a valid json dict from a user registration object.
    """
    return user_reg_form.dict()


def check_user_register_resp_valid(response: HTTPResponse) -> bool:
    """
    Given a raw server response, checks it and returns true if all checks pass.
    """
    try:
        assert response.status_code == 201
        # TODO: fixme
        # assert "jwt" in response.json()
        # assert check_jwt_response_valid(response.json()["jwt"])
        return True
    except AssertionError as assert_error:
        debug_msg = f"failed at: {assert_error}. resp json: {response.json()}"
        logging.debug(debug_msg)
        return False


def get_register_user_endpoint_url() -> str:
    """
    Returns the url string for the user registration endpoint
    """
    return "/users/register"


class TestUserRegister:
    def test_register_user_success(
            self, user_registration_form: user_models.UserRegistrationForm):
        """
        Tries to register a valid user form, expecting success.
        """
        user_data = get_reg_user_json_from_form(user_registration_form)
        endpoint_url = get_register_user_endpoint_url()
        response = client.post(endpoint_url, json=user_data)
        assert check_user_register_resp_valid(response)

    def test_register_dupe_data_fail(
            self, user_registration_form: user_models.UserRegistrationForm):
        """
        Tries to register and user using duplicate unique identifiers,
        expecting failure.
        """
        user_data = get_reg_user_json_from_form(user_registration_form)
        endpoint_url = get_register_user_endpoint_url()
        response = client.post(endpoint_url, json=user_data)
        assert check_user_register_resp_valid(response)

        # re-send request expecting failure
        response = client.post(endpoint_url, json=user_data)
        assert not check_user_register_resp_valid(response)
        assert response.status_code == 409

    def test_register_user_invalid_data(
            self, user_registration_form: user_models.UserRegistrationForm):
        """
        Tries to register a user with invalid data, expecting 422 failure.
        """
        bad_user_data = generate_bad_user_data_json(user_registration_form)
        endpoint_url = get_register_user_endpoint_url()
        response = client.post(endpoint_url, json=bad_user_data)
        assert check_user_register_resp_valid(response)

    def test_reg_user_empty_data_fail(self):
        """
        Tries to register a user but sends no data, expecting 422 failure
        """
        endpoint_url = get_register_user_endpoint_url()
        response = client.post(endpoint_url, json={})

        assert not check_user_register_resp_valid(response)


class TestAdminUserRegister:
    """
    Tests the user registration endpoint for an admin type user.
    """
    def test_register_user_success(
            self,
            admin_user_registration_form: user_models.UserRegistrationForm):
        """
        Tries to register a valid user form, expecting success.
        """
        user_data = get_reg_user_json_from_form(admin_user_registration_form)
        endpoint_url = get_register_user_endpoint_url()
        response = client.post(endpoint_url, json=user_data)
        assert check_user_register_resp_valid(response)

    def test_register_dupe_data_fail(
            self,
            admin_user_registration_form: user_models.UserRegistrationForm):
        """
        Tries to register and admin user using duplicate unique identifiers,
        expecting failure.
        """
        user_data = get_reg_user_json_from_form(admin_user_registration_form)
        endpoint_url = get_register_user_endpoint_url()
        response = client.post(endpoint_url, json=user_data)
        assert check_user_register_resp_valid(response)

        # re-send request expecting failure
        response = client.post(endpoint_url, json=user_data)
        assert not check_user_register_resp_valid(response)
        assert response.status_code == 409

    def test_register_user_invalid_data(
            self,
            admin_user_registration_form: user_models.UserRegistrationForm):
        """
        Tries to register a user with invalid data, expecting 422 failure.
        """
        bad_user_data = generate_bad_user_data_json(
            admin_user_registration_form)
        endpoint_url = get_register_user_endpoint_url()
        response = client.post(endpoint_url, json=bad_user_data)
        assert check_user_register_resp_valid(response)

    def test_reg_user_empty_data_fail(self):
        """
        Tries to register a user but sends no data, expecting 422 failure
        """
        endpoint_url = get_register_user_endpoint_url()
        response = client.post(endpoint_url, json={})

        assert not check_user_register_resp_valid(response)
