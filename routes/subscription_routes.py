from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from config.db import get_database

subscription_routes = Blueprint('subscription_routes', __name__)

# Initialize MongoDB client
client = get_database()
db = client["pma-it-suite"]
users_collection = db["members"]

@subscription_routes.route('/', methods=['GET'])
@cross_origin()
def get_users_in_subscription():
    subscription_id = request.args.get('subscription_id')
    if subscription_id is None:
        return jsonify({"status": "error", "message": "Subscription ID is required"}), 400

    users = list(users_collection.find({"subscription_id": subscription_id}))

    # Remove the _id field as it's not JSON-serializable
    return jsonify({"status": "OK", "users": users})
