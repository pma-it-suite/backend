# devices_routes.py
from flask import Blueprint, request, jsonify
from pymongo import DESCENDING
import uuid
from config.db import get_database

# Initialize the Blueprint
devices_routes = Blueprint('devices_routes', __name__)

# Initialize MongoDB client
client = get_database()
db = client["pma-it-suite"]
commands_collection = db["commands"]

@devices_routes.route('/device/<device_id>/command', methods=['GET'])
def get_most_recent_command(device_id):
    try:
        # Query the most recent command for the given device_id
        command = commands_collection.find_one(
            {'device_id': device_id},
            sort=[('_id', DESCENDING)]
        )
        
        if not command:
            return jsonify({'status': 'error', 'message': 'No commands found for this device'}), 404

        return jsonify({
            'status': 'OK',
            'command_id': str(command['_id']),
            'name': command['name'],
            'args': command['args']
        }), 200

    except Exception as e:
        print(e)
        return jsonify({'status': 'error', 'message': 'An error occurred'}), 500

@devices_routes.route('/command/<command_id>/status', methods=['PUT'])
def update_command_status(command_id):
    try:
        data = request.json
        status = data.get('status')
        
        if not status:
            return jsonify({'status': 'error', 'message': 'Status is required'}), 400

        updated = commands_collection.update_one(
            {'_id': command_id},
            {'$set': {'status': status}}
        )

        if updated.modified_count == 0:
            return jsonify({'status': 'error', 'message': 'Failed to update command status'}), 400

        return jsonify({'status': 'OK', 'message': 'Command status updated successfully'}), 200

    except Exception as e:
        print(e)
        return jsonify({'status': 'error', 'message': 'An error occurred'}), 500
    
@devices_routes.route('/device/<device_id>/command', methods=['POST'])
def create_command(device_id):
    try:
        data = request.json
        name = data.get("name")
        args = data.get("args")

        if not name:
            return jsonify({"status": "error", "message": "Command name is required"}), 400
        if not args:
            return jsonify({"status": "error", "message": "Arguments are required"}), 400

        # Prepare command data
        command_data = {
            "_id": str(uuid.uuid4()),  # Use uuid instead of ObjectId
            "name": name,
            "args": args,
            "device_id": device_id,
            "status": "pending"  # default status
        }

        # Insert command into MongoDB
        commands_collection.insert_one(command_data)

        return jsonify({"status": "OK", "message": f"Command created successfully for device {device_id}", "newCommand": command_data}), 201

    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": "An error occurred"}), 500