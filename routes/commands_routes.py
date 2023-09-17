# commands_routes.py
from flask import Blueprint, request, jsonify
from pymongo import DESCENDING
import uuid
from config.db import get_database

# Initialize the Blueprint
commands_routes = Blueprint('commands_routes', __name__)

# Initialize MongoDB client
client = get_database()
db = client["pma-it-suite"]
commands_collection = db["commands"]

@commands_routes.route('/recent', methods=['GET'])
def get_most_recent_command():
    try:
        data = request.json
        device_id = data.get('device_id')
        if not device_id:
            return jsonify({'status': 'error', 'message': 'Device ID is required'}), 400

        command = commands_collection.find_one(
            {'device_id': device_id, 'status': 'pending'},
            sort=[('_id', DESCENDING)]
        )
        
        if not command:
            return jsonify({'status': 'error', 'message': 'No commands found for this device'}), 404

        return jsonify({
            'status': command['status'],
            'command_id': str(command['_id']),
            'name': command['name'],
            'args': command.get('args', '') if command.get('args') else ''
        }), 200

    except Exception as e:
        print(e)
        return jsonify({'status': 'error', 'message': 'An error occurred'}), 500

@commands_routes.route('/status', methods=['PUT'])
def update_command_status():
    try:
        data = request.json
        command_id = data.get('command_id')
        status = data.get('status')
        
        if not command_id or not status:
            return jsonify({'status': 'error', 'message': 'Command ID and Status are required'}), 400

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

@commands_routes.route('/', methods=['POST'])
def create_command():
    try:
        data = request.json
        device_id = data.get('device_id')
        name = data.get('name')
        args = data.get('args')

        if not device_id or not name:
            return jsonify({'status': 'error', 'message': 'Device ID, Command name, and Arguments are required'}), 400

        command_data = {
            "_id": str(uuid.uuid4()),  # Use uuid instead of ObjectId
            "name": name,
            "args": args,
            "device_id": device_id,
            "status": "pending"  # default status
        }

        commands_collection.insert_one(command_data)

        return jsonify({'status': 'OK', 'message': f"Command created successfully for device {device_id}", 'newCommand': command_data}), 201

    except Exception as e:
        print(e)
        return jsonify({'status': 'error', 'message': 'An error occurred'}), 500
    
@commands_routes.route('/batch', methods=['POST'])
def create_commands_for_multiple_devices():
    try:
        data = request.json
        device_ids = data.get("device_ids")
        name = data.get("name")
        args = data.get("args")

        if not device_ids:
            return jsonify({"status": "error", "message": "Device IDs are required"}), 400
        if not name:
            return jsonify({"status": "error", "message": "Command name is required"}), 400

        new_commands = []
        for device_id in device_ids:
            command_data = {
                "_id": str(uuid.uuid4()),  # Use uuid instead of ObjectId
                "name": name,
                "args": args,
                "device_id": device_id,
                "status": "pending"  # default status
            }
            commands_collection.insert_one(command_data)
            new_commands.append(command_data)

        return jsonify({"status": "OK", "message": "Commands created successfully", "newCommands": new_commands}), 201

    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": "An error occurred"}), 500