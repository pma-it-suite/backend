# devices_routes.py

from flask import Blueprint, request, jsonify
from pymongo import MongoClient, DESCENDING

# Initialize the Blueprint
devices = Blueprint('devices', __name__)

# Initialize MongoDB client
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database_name']
commands_collection = db['commands']

@devices.route('/device/<device_id>/command', methods=['GET'])
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

@devices.route('/command/<command_id>/status', methods=['PUT'])
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
