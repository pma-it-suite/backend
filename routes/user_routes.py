from flask import Blueprint, request, jsonify
from config.db import get_database
from bson.objectid import ObjectId
import random
import string

user_routes = Blueprint('user_routes', __name__, url_prefix='/users')

# Initialize MongoDB client
client = get_database()
db = client["pma-it-suite"]
users_collection = db["members"]

@user_routes.route('/check', methods=['GET'])
def check_username():
    username = request.args.get('username')
    if username is None:
        return jsonify({"status": "error", "message": "Username is required"}), 400
    
    user = users_collection.find_one({"username": username})
    
    if user:
        # Remove the _id field as it's not JSON-serializable
        user.pop("_id", None)
        return jsonify({"status": "OK", "user": user})
    else:
        return jsonify({"status": "NO"})

@user_routes.route('/', methods=['POST'])
def create_user():
    data = request.json

    required_fields = ["username", "type", "tenant_id", "subscription_id"]
    for field in required_fields:
        if field not in data:
            return jsonify({"status": "error", "message": f"{field} is required"}), 400

    try:
        data["_id"] = str(ObjectId())  # Generate new ObjectId
        users_collection.insert_one(data)
        return jsonify({"status": "OK", "message": f"User {data['username']} created successfully", "_id": data["_id"]}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"}), 500

@user_routes.route('/', methods=['GET'])
def read_user():
    username = request.args.get('username')
    if username is None:
        return jsonify({"status": "error", "message": "Username is required"}), 400

    user = users_collection.find_one({"username": username})
    
    if user:
        return jsonify({"status": "OK", "user": user})
    else:
        return jsonify({"status": "NO", "message": "User not found"}), 404

@user_routes.route('/', methods=['PUT'])
def update_user():
    data = request.json
    username = data.get("username")
    new_username = data.get("new_username")
    if not username or not new_username:
        return jsonify({"status": "error", "message": "Both username and new_username are required"}), 400

    result = users_collection.update_one({"username": username}, {"$set": {"username": new_username}})
    
    if result.modified_count > 0:
        return jsonify({"status": "OK", "message": f"User {username} updated successfully"}), 200
    else:
        return jsonify({"status": "NO", "message": "User not found or not modified"}), 404

@user_routes.route('/', methods=['DELETE'])
def delete_user():
    username = request.args.get('username')
    if username is None:
        return jsonify({"status": "error", "message": "Username is required"}), 400

    result = users_collection.delete_one

@user_routes.route('/delete_all', methods=['DELETE'])
def delete_all_users():
    result = users_collection.delete_many({})
    return jsonify({"status": "OK", "message": f"{result.deleted_count} users deleted"})

@user_routes.route('/generate', methods=['POST'])
def generate_users():
    count = int(request.args.get('count', 10))  # default to generating 10 users
    tenant_id = str(ObjectId())
    subscription_id = str(ObjectId())

    # Delete existing special users
    users_collection.delete_many({"username": {"$in": ["testadmin", "testuser"]}})

    # Generate new special users
    special_users = ["testadmin", "testuser"]
    users = []

    for username in special_users:
        user_type = "admin" if username == "testadmin" else "user"
        user_id = str(ObjectId())
        user = {
            "_id": user_id,
            "username": username,
            "type": user_type,
            "tenant_id": tenant_id,
            "subscription_id": subscription_id
        }
        users.append(user)

    # Generate other random users
    for _ in range(count - len(special_users)):  # Adjust count for the special users
        user_id = str(ObjectId())
        user_type = random.choice(["admin", "user"])
        user = {
            "_id": user_id,
            "username": ''.join(random.choices(string.ascii_letters, k=10)),
            "type": user_type,
            "tenant_id": tenant_id,
            "subscription_id": subscription_id
        }
        users.append(user)

    result = users_collection.insert_many(users)
    return jsonify({"status": "OK", "message": f"{len(result.inserted_ids)} users generated"})