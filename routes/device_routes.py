from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from config.db import get_database
from bson.objectid import ObjectId
import random
import string

devices_routes = Blueprint('device_routes', __name__, url_prefix='/devices')

# Initialize MongoDB client
client = get_database()
db = client["pma-it-suite"]
users_collection = db["members"]
devices_collection = db["devices"]


@devices_routes.route('/register', methods=['POST'])
@cross_origin()
def register_device():
    data = request.json

    required_fields = ["user_id", "user_secret"]
    for field in required_fields:
        if field not in data:
            return jsonify({
                "status": "error",
                "message": f"{field} is required"
            }), 400

    try:
        user_id = data["user_id"]
        filter = {"_id": user_id}
        print(f"looking for user {user_id} to register device...")
        user = users_collection.find_one(filter)
        if not user:
            return jsonify({"message": f"User with {user_id} not found"}), 404

        if data["user_secret"] != get_user_secret(user_id):
            return jsonify({"message": f"User secret invalid"}), 401

        device_id = str(ObjectId())

        try:
            device_id = user["device_ids"] + device_id
        except:
            print(f"adding device id ({device_id}) to user ({user_id})...")
            device_ids = [device_id]

        users_collection.update_one(filter,
                                    {"$set": {
                                        "device_ids": device_ids
                                    }})

        device = {"_id": device_id, "user_id": user_id}
        devices_collection.insert_one(device)

        return jsonify({
            "message":
            f"User {user['username']} updated with device {device_id} successfully",
            "device_id": device_id
        }), 200
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


def get_user_secret(user_id: str):
    # TODO @felipearce
    return user_id + "-test-token"
