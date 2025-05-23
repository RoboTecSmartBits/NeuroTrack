import json
import asyncio
import logging
import websockets
from datetime import datetime
from struct import unpack
from uuid import UUID
from ..models.models import db, Device, SensorData, User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

connected_clients = set()

def get_first_user_id():
    """
    Helper function to get a valid user ID for auto-creating devices.
    Returns the ID of the first user in the database or None if no users exist.
    """
    user = User.query.first()
    if user:
        return user.id
    logger.warning("No users found in the database for device auto-creation")
    return None

async def register_device(websocket, path):
    connected_clients.add(websocket)
    logger.info(f"New client connected. Total clients: {len(connected_clients)}")

    try:
        async for message in websocket:
            try:
                if isinstance(message, bytes):
                    await process_binary_sensor_data(message)
                    await websocket.send(json.dumps({"status": "success", "message": "Binary data received"}))
                else:
                    data = json.loads(message)
                    logger.info(f"Received JSON data: {data}")
                    await process_sensor_data(data)
                    await websocket.send(json.dumps({"status": "success", "message": "Data received"}))
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await websocket.send(json.dumps({"status": "error", "message": str(e)}))
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client connection closed")
    finally:
        connected_clients.remove(websocket)
        logger.info(f"Client disconnected. Remaining clients: {len(connected_clients)}")


async def process_binary_sensor_data(binary_data):
    """
    Unpack binary data: 16 bytes UUID + 7 floats (28 bytes).
    """
    try:
        if len(binary_data) < 44:
            raise ValueError(f"Invalid binary packet size: {len(binary_data)} bytes")

        uuid_bytes = binary_data[:16]
        try:
            uuid = str(UUID(bytes=uuid_bytes))
        except Exception as e:
            raise ValueError(f"Failed to parse UUID: {e}")

        # Unpack 7 floats from the next 28 bytes
        float_data = unpack('7f', binary_data[16:44])
        a_x, a_y, a_z, g_x, g_y, g_z, battery = float_data

        logger.info(f"[BINARY] UUID: {uuid}, Accel: {a_x},{a_y},{a_z}, Gyro: {g_x},{g_y},{g_z}, Battery: {battery}")

        from flask import current_app
        with current_app.app_context():
            device = Device.query.get(uuid)
            
            # Auto-create the device if it doesn't exist
            if not device:
                logger.info(f"Creating new device with UUID: {uuid}")
                device = Device(
                    id=uuid,
                    name=f"ESP32 Auto-created {uuid[:8]}",
                    device_type="ESP32",
                    user_id=get_first_user_id(),  # Helper function to get a valid user ID
                    created_at=datetime.utcnow()
                )
                db.session.add(device)
            
            # Update last_seen timestamp
            device.last_seen = datetime.utcnow()
                
            # Add sensor data
            sensor_data = SensorData(
                device_id=uuid,
                timestamp=datetime.utcnow(),
                accel_x=a_x,
                accel_y=a_y,
                accel_z=a_z,
                gyro_x=g_x,
                gyro_y=g_y,
                gyro_z=g_z,
                battery_level=battery
            )
            db.session.add(sensor_data)
            db.session.commit()
    except Exception as e:
        logger.error(f"Error decoding binary sensor data: {e}")
        raise


async def process_sensor_data(data):
    """
    Handle regular JSON data.
    """
    try:
        uuid = data.get("device_id")
        if not uuid:
            raise ValueError("Missing device_id in JSON data")

        from flask import current_app
        with current_app.app_context():
            device = Device.query.get(uuid)
            if device:
                device.last_seen = datetime.utcnow()
                sensor_data = SensorData(
                    device_id=uuid,
                    timestamp=datetime.utcnow(),
                    accel_x=data.get("accel_x", 0.0),
                    accel_y=data.get("accel_y", 0.0),
                    accel_z=data.get("accel_z", 0.0),
                    gyro_x=data.get("gyro_x", 0.0),
                    gyro_y=data.get("gyro_y", 0.0),
                    gyro_z=data.get("gyro_z", 0.0),
                    battery_level=data.get("battery_level", 0.0)
                )
                db.session.add(sensor_data)
                db.session.commit()
            else:
                logger.warning(f"Device with UUID {uuid} not found in JSON payload")
    except Exception as e:
        logger.error(f"Error processing JSON sensor data: {e}")
        raise
