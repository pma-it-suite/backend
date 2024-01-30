# pylint: disable=redefined-outer-name
#       - this is how we use fixtures internally so this throws false positives
# pylint: disable=unsubscriptable-object
#       - this is actually a pylint bug that hasn't been resolved.
# pylint: disable=too-many-lines
#       - (needs refactor) ...
"""
pytest `conftest.py` file that holds global fixtures for tests
"""
import os
import logging
from typing import Callable, Dict, Any, Optional

import pytest
import fastapi
from icecream import ic
from faker import Faker
from asgiref.sync import async_to_sync
from requests.models import Response as HTTPResponse

import models.routes.users as user_models
import models.db.common as common_models
import models.db as db_models
import utils.users as user_utils

# TODO @felipearce: very hacky fix if possible
get_db_instance = None


# startup process
def pytest_configure(config):
    """
    Startup process for tests.

    The change of the testing flag **MUST** be the first statement done here,
    any other statements for setup must be placed afterwards.
    """
    os.environ['_called_from_test'] = 'True'
    os.environ['_called_from_test_with_mock'] = 'True'

    # TODO @felipearce: very hacky fix if possible
    # this is because the db instance is created as soon as the module is imported
    from config.db import _get_global_database_instance
    global get_db_instance
    get_db_instance = _get_global_database_instance

    logging.getLogger("faker").setLevel(logging.ERROR)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    del config  # unused variable


def pytest_unconfigure(config):
    """
    Shutdown process for tests, mostly involving the wiping of database
    documents and resetting the testing environment flag.
    """
    global_database_instance = get_db_instance()
    global_database_instance.delete_test_database()
    global_database_instance.close_client_connection()
    os.environ['_called_from_test'] = 'False'
    os.environ['_called_from_test_with_mock'] = 'False'
    del config  # unused variable


@pytest.fixture(autouse=True)
def run_around_tests():
    """
    Clears all documents in the test collections after every single test.
    """
    yield
    global_database_instance = get_db_instance()
    global_database_instance.clear_test_collections()


@pytest.fixture(scope='function')
def registered_user_redacted(
    registered_user_redacted_factory: Callable[[],
                                               db_models.user.DbUserRedacted]
) -> db_models.user.DbUser:
    """
    Fixture that generates a random valid user and registers it directly to
    the database through the `util` method.

    Returns the original user object.
    """
    user = registered_user_redacted_factory()
    return user


@pytest.fixture(scope='function')
def registered_user(
    registered_user_factory: Callable[[], db_models.user.DbUser]
) -> db_models.user.DbUser:
    """
    Fixture that generates a random valid user and registers it directly to
    the database through the `util` method.

    Returns the original user object.
    """
    user = registered_user_factory()
    return user

@pytest.fixture(scope='function')
def registered_user_orig(
    registered_user_factory: Callable[[], db_models.user.DbUser]
) -> db_models.user.DbUser:
    """
    Fixture that generates a random valid user and registers it directly to
    the database through the `util` method.

    Returns the original user object as well as the user reg form
    """
    user, user_reg_form = registered_user_factory()
    return user, user_reg_form


@pytest.fixture(scope='function')
def registered_user_factory(
    user_registration_form_factory: Callable[
        [], user_models.register_user.RegisterUserRequest]
) -> Callable[[], db_models.user.DbUser]:
    """
    Returns a factory that creates valid registered user and returns it's data
    """
    def _create_and_register_user(
    ) -> user_models.register_user.RegisterUserRequest:
        """
        Uses a registration form factory to create a valid user on-command,
        then registers it to the database and returns it.
        """
        user_reg_form = user_registration_form_factory()
        user_data = register_user_reg_form_to_db(user_reg_form)
        return user_data, user_reg_form

    return _create_and_register_user


@pytest.fixture(scope='function')
def registered_user_redacted_factory(
    user_registration_form_factory: Callable[
        [], user_models.register_user.RegisterUserRequest]
) -> Callable[[], db_models.user.DbUserRedacted]:
    """
    Returns a factory that creates valid registered user and returns it's data
    """
    def _create_and_register_user(
    ) -> user_models.register_user.RegisterUserRequest:
        """
        Uses a registration form factory to create a valid user on-command,
        then registers it to the database and returns it.
        """
        user_reg_form = user_registration_form_factory()
        user_data = register_user_reg_form_to_db(user_reg_form)
        return db_models.user.DbUserRedacted(**user_data.dict())

    return _create_and_register_user


@pytest.fixture(scope='function')
def unregistered_user() -> db_models.user.DbUser:
    """
    Fixture that generates a valid user and returns it
    WITHOUT registering it to the database first.
    """
    return generate_random_db_user()


@pytest.fixture(scope='function')
def user_registration_form(
    user_registration_form_factory: Callable[
        [], user_models.register_user.RegisterUserRequest]
) -> user_models.register_user.RegisterUserRequest:
    """
    Returns an unregistered, random, valid user registration form object.
    """
    return user_registration_form_factory()


@pytest.fixture(scope='function')
def user_registration_form_factory(
) -> Callable[[], user_models.register_user.RegisterUserRequest]:
    """
    Returns a function which creates random, valid user registration forms
    """
    def _create_user_reg_form(
    ) -> user_models.register_user.RegisterUserRequest:
        """
        Generates a random user data dict and then casts it into
        a registration form, and returns it
        """
        user_dict = generate_random_register_user_request().dict()
        return user_models.register_user.RegisterUserRequest(**user_dict)

    return _create_user_reg_form


@pytest.fixture(scope='function')
def get_identifier_dict_from_user(
) -> Callable[[db_models.user.DbUserRedacted], Dict[str, Any]]:
    def _get_identifier_from_user(
        user: db_models.user.DbUserRedacted | db_models.user.DbUser
    ) -> Dict[str, Any]:
        return {"user_id": user.get_id()}

    return _get_identifier_from_user


def register_user_reg_form_to_db(
    reg_form: user_models.register_user.RegisterUserRequest
) -> db_models.user.DbUser:
    """
    Helper function for registering a user given a registration form
    and returning the user data.
    """
    user_data = get_user_from_user_reg_form(reg_form)

    # user ID auto-instanciates so we reassign it to the actual ID
    user_id = user_utils.register_user_to_db(reg_form)
    user_data.id = user_id

    return user_data


def get_user_from_user_reg_form(
    user_reg_form: user_models.register_user.RegisterUserRequest
) -> db_models.user.DbUser:
    """
    Helper method that correctly casts a `UserRegistrationForm` into
    a valid `User` object and returns it.
    """
    fake = Faker()
    dbuser_dict = {
        "_id": fake.uuid4(),
        "metadata": {},
        "user_secret_hash": fake.password(),
        "password_hash": test_hash_pwd(user_reg_form.raw_password),
        "device_ids": [],
        **user_reg_form.dict()
    }
    user_object = db_models.user.DbUser(**dbuser_dict)
    return user_object


def test_hash_pwd(pwd: str) -> str:
    """
    fixture for fake-hash
    """
    return pwd + "-hash"


def generate_random_db_user(
    user_type: Optional[
        db_models.user.UserTypeEnum] = db_models.user.UserTypeEnum.USER
) -> db_models.user.DbUser:
    """
    Uses a fake data generator to generate a unique
    and valid user object.
    """
    fake = Faker()
    user_data = {
        "name": f"{fake.first_name()} {fake.last_name()}",
        "email": fake.email(),
        "metadata": {},
        "password_hash": fake.password(),
        "user_secret_hash": fake.password(),
        "tenant_id": fake.uuid4(),
        "subscription_id": fake.uuid4(),
        "device_ids": [fake.uuid4(), fake.uuid4()],
        "role_id": fake.uuid4(),
        "user_type": user_type,
    }
    return db_models.user.DbUser(**user_data)


def generate_random_register_user_request(
    user_type: Optional[
        db_models.user.UserTypeEnum] = db_models.user.UserTypeEnum.USER
) -> user_models.register_user.RegisterUserRequest:
    """
    Uses a fake data generator to generate a unique
    and valid user object.
    """
    fake = Faker()
    user_data = {
        "name": f"{fake.first_name()} {fake.last_name()}",
        "email": fake.email(),
        "raw_password": fake.password(),
        "tenant_id": fake.uuid4(),
        "role_id": fake.uuid4(),
        "subscription_id": fake.uuid4(),
        "user_type": user_type,
    }
    return user_models.register_user.RegisterUserRequest(**user_data)
