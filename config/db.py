"""
Global settings manager + instanciator of the database client instance.

No module other than this one has direct access to the database client;
this ensures that we have a single source of truth in regards to transactions
as well as making sure that we never accidentally swap from the production
database to the testing database.
"""
import os
from uuid import uuid4
from typing import Dict, Any
import gridfs
from pymongo import MongoClient, IndexModel
from config.main import DB_URI


def get_database() -> MongoClient:
    """
    Returns a valid client to the database.

    Even if called multiple times, the same object will
    always be returned.
    """
    db_instance = _get_global_database_instance()
    return db_instance.get_database_client()


def close_connection_to_mongo() -> None:
    """
    Public facing method for closing the database connection
    """
    db_instance = _get_global_database_instance()
    db_instance.close_client_connection()


def get_database_client_name() -> str:
    """
    Returns the name of the database singleton.

    Should always have the database instanciated prior,
    in the impossible case that it doesn't, it raises an exception.
    """
    db_instance = _get_global_database_instance()
    return db_instance.get_database_name()


def get_grid_fs_client() -> gridfs.GridFS:
    """
    Returns the singleton GridFS client. This function is lazy,
    so it will only instanciate the GridFS client _if_ called.

    Once instanciated will only return the same client
    """
    fs_client = _get_global_grid_fs_instance()
    return fs_client


# Utils for the file that don't have any need to be actually inside the class
def _is_testing() -> bool:
    """
    Simple but dynamic function that returns the testing status.
    Can be used for things other than database config.
    """
    return os.environ.get("_called_from_test") == "True"


def _get_database_name_str() -> str:
    """
    Dynamically return the name of the current database.

    Returns the production database name if not testing.
    """
    if _is_testing():
        test_db_name = _generate_test_database_name()
        return test_db_name

    production_db_name = "underline"
    return production_db_name


def _generate_test_database_name() -> str:
    """
    Generates a unique but identifiable database name for testing.
    """
    testing_db_name_prefix = "pytest-"

    # we need to truncate to 38 bytes for mongo
    random_uuid_str = str(uuid4())[:10]

    testing_db_name_str = testing_db_name_prefix + random_uuid_str
    return testing_db_name_str


class Database:
    """
    Utility class that holds the main database client instance.
    """
    def __init__(self):
        """
        Creates a Database instance with a MongoClient set to the global DB_URI.
        """
        self.client = MongoClient(DB_URI)
        self.database_name = _get_database_name_str()
        self.__setup_database_indexes()

    def get_database_client(self) -> MongoClient:
        """
        Returns the instance's db client.
        """
        return self.client

    def close_client_connection(self) -> None:
        """
        Closes the client's connection to mongo.
        """
        self.client.close()

    def get_database_name(self) -> str:
        """
        Get the mongo client's current database name
        """
        return self.database_name

    def clear_test_collections(self) -> None:
        """
        Runs through every collection in the testing database and deletes
        all of the documents within that collection.

        Will not interact with the production database at all.
        """
        current_db_is_for_tests = self.__check_current_db_is_for_testing()

        if current_db_is_for_tests:
            db_name = self.database_name
            test_database = self.client[db_name]
            test_collection_names = test_database.list_collection_names()

            for collection in test_collection_names:
                test_database[collection].delete_many({})

    def delete_test_database(self) -> None:
        """
        Deletes the current testing database.

        Will never delete the production database, even if it
        is the current database being used.
        """
        current_db_is_for_tests = self.__check_current_db_is_for_testing()

        if current_db_is_for_tests:
            test_database_name = self.database_name
            self.client.drop_database(test_database_name)

    def __check_current_db_is_for_testing(self) -> bool:  # pylint: disable=invalid-name
        """
        Safety guard that checks the name of the current database as well
        as the current testing status flags to ensure the database is for tests.
        """
        return "test" in self.database_name and _is_testing()

    def __setup_database_indexes(self) -> None:
        """
        Sets up the database indexes for the unique fields.

        If the indexes are set up already, does nothing, making
        it safe to call multiple times.
        """
        indexes_dict = self.__get_index_command_dict()
        db_instance = self.client[self.database_name]

        indexes_already_setup = self.__check_indexes_already_exist()

        if not indexes_already_setup:
            for collection_name, index_models in indexes_dict.items():
                db_instance[collection_name].create_indexes(index_models)

    def __get_index_command_dict(self) -> Dict[str, IndexModel]:  # pylint: disable=no-self-use
        """
        Returns a dict with all of the collection names as keys and
        their corresponding IndexModel.

        Can be iterated over to insert the correct indexes into the collections.
        """

        indexes_dict = {
            "users": [IndexModel("email", unique=True)],
        }

        return indexes_dict

    def __check_indexes_already_exist(self) -> bool:
        """
        Uses the database instance to check if all of the collection
        indexes have been created
        """
        db_instance = self.client[self.database_name]
        master_indexes_dict = self.__get_master_dict_of_indexes()

        try:
            for collection_name, index_dict in master_indexes_dict.items():
                db_collection = db_instance[collection_name]
                indexes_match = db_collection.index_information() == index_dict
                assert indexes_match
            return True
        except AssertionError as _assert_error:
            return False

    def __get_master_dict_of_indexes(self) -> Dict[str, Any]:  # pylint: disable=no-self-use
        """
        Returns the dict object with all of the indexes that should be
        in the collections.

        Keys for the dict are collection names, and the values are
        their indexes.

        Used to verify that the indexes present in the database are
        valid and match the spec.
        """

        indexes_dict = {
            "users": {
                '_id_': {
                    'v': 2,
                    'key': [('_id', 1)]
                },
                'email_1': {
                    'v': 2,
                    'unique': True,
                    'key': [('email', 1)]
                }
            },
        }

        return indexes_dict


# enforces singleton pattern behind the scenes
# must start uninstanciated so the env vars can load in prior
GLOBAL_DATABASE_INSTANCE = None
GLOBAL_GRID_FS_INSTANCE = None


def _get_global_database_instance() -> Database:
    """
    Primitive and dangerous method to get the database instance

    Assures that if you call this, the `global_database_instance` will
    be successfully instanciated before being returned.
    """
    database_already_instanciated = __check_global_db_already_exists()

    if not database_already_instanciated:
        global GLOBAL_DATABASE_INSTANCE  #pylint: disable=global-statement
        GLOBAL_DATABASE_INSTANCE = Database()

    return GLOBAL_DATABASE_INSTANCE


def __check_global_db_already_exists() -> bool:  # pylint: disable=invalid-name
    return isinstance(GLOBAL_DATABASE_INSTANCE, Database)


def _get_global_grid_fs_instance() -> gridfs.GridFS:
    """
    Primitive and dangerous method to get the global gridfs instance

    Assures that if you call this, the `GLOBAL_GRID_FS_INSTANCE` will
    be successfully instanciated before being returned.
    """
    gridfs_already_instanciated = __check_global_grid_fs_exists()

    if not gridfs_already_instanciated:
        global GLOBAL_GRID_FS_INSTANCE  #pylint: disable=global-statement
        db_client = get_database()[get_database_client_name()]
        GLOBAL_GRID_FS_INSTANCE = gridfs.GridFS(db_client)

    return GLOBAL_GRID_FS_INSTANCE


def __check_global_grid_fs_exists() -> bool:
    return isinstance(GLOBAL_GRID_FS_INSTANCE, gridfs.GridFS)