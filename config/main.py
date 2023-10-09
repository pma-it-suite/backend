"""
Holds global config settings for the whole runtime.

Mostly made up of environment config variables.
Also instanciates the `FastAPI()` router instance.
"""
import os
import dotenv
dotenv.load_dotenv()
DB_URI = os.environ.get("MONGO_DB_URI")
SERVER_HOST = os.environ.get("SERVER_HOST")
SERVER_PORT = os.environ.get("SERVER_PORT")
DB_URI = os.environ.get("MONGO_DB_URI")
if not DB_URI:
    raise Exception("Key Error: DB_URI not set!")

DB_NAME = "itx"
USERS_COLLECTION_NAME = "members"
