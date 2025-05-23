from flask import Blueprint, request, jsonify, current_app
from flask.views import MethodView
from ..models.models import db, Device, User
from datetime import datetime
import uuid

devices_bp = Blueprint('devices', __name__, url_prefix='/devices')

class DeviceView(MethodView):
    def get(self, device_id=None):
        """
        Get a list of all devices or details of a specific device
        """
        if device_id:
            # Get details of a specific device
            device = Device.query.get(device_id)
            if not device:
                return jsonify({"error": "Device not found"}), 404
            
            return jsonify(device.to_dict()), 200
        else:
            # Get list of all devices
            devices = Device.query.all()
            return jsonify([device.to_dict() for device in devices]), 200
    
    def post(self):
        """
        Register a new device for a user
        """
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Check if required fields are provided
        required_fields = ['name', 'device_type', 'user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if user exists
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Create a new device
        new_device = Device(
            id=str(uuid.uuid4()),
            name=data['name'],
            device_type=data['device_type'],
            user_id=data['user_id'],
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_device)
        db.session.commit()
        
        return jsonify(new_device.to_dict()), 201
    
    def put(self, device_id):
        """
        Update an existing device
        """
        device = Device.query.get(device_id)
        if not device:
            return jsonify({"error": "Device not found"}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Update device fields
        if 'name' in data:
            device.name = data['name']
        
        if 'device_type' in data:
            device.device_type = data['device_type']
        
        if 'user_id' in data:
            # Check if new user exists
            user = User.query.get(data['user_id'])
            if not user:
                return jsonify({"error": "User not found"}), 404
            device.user_id = data['user_id']
        
        db.session.commit()
        
        return jsonify(device.to_dict()), 200
    
    def delete(self, device_id):
        """
        Delete a device
        """
        device = Device.query.get(device_id)
        if not device:
            return jsonify({"error": "Device not found"}), 404
        
        db.session.delete(device)
        db.session.commit()
        
        return jsonify({"message": "Device deleted successfully"}), 200

# Register the view
device_view = DeviceView.as_view('device_api')
devices_bp.add_url_rule('/', view_func=device_view, methods=['GET', 'POST'])
devices_bp.add_url_rule('/<string:device_id>', view_func=device_view, methods=['GET', 'PUT', 'DELETE'])

# Add route to get sensor data for a device
@devices_bp.route('/<string:device_id>/sensor-data', methods=['GET'])
def get_sensor_data(device_id):
    """
    Get sensor data for a specific device
    """
    from ..models.models import SensorData
    
    # Check if device exists
    device = Device.query.get(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404
    
    # Get query parameters for filtering
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Query sensor data
    sensor_data = (
        SensorData.query
        .filter_by(device_id=device_id)
        .order_by(SensorData.timestamp.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    
    return jsonify([data.to_dict() for data in sensor_data]), 200

# Add route for users to select a device
@devices_bp.route('/user/<string:user_id>/select', methods=['GET'])
def get_user_devices(user_id):
    """
    Get all devices for a specific user
    """
    # Check if user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Query devices
    devices = Device.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        "user": {
            "id": user.id,
            "name": user.nume
        },
        "devices": [device.to_dict() for device in devices]
    }), 200

@devices_bp.route('/assign', methods=['POST'])
def assign_device_to_user():
    """
    Assign an existing device to a user
    """
    data = request.get_json()
    
    # Validate input
    if not data or 'device_id' not in data or 'user_id' not in data:
        return jsonify({"error": "Missing device_id or user_id"}), 400
    
    # Check if device exists
    device = Device.query.get(data['device_id'])
    if not device:
        return jsonify({"error": "Device not found"}), 404
    
    # Check if user exists
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Update device
    device.user_id = data['user_id']
    if 'name' in data:
        device.name = data['name']
    
    db.session.commit()
    
    return jsonify({
        "message": "Device assigned successfully",
        "device": device.to_dict()
    }), 200
