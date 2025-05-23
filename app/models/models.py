import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nume = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    password = db.Column(db.String(200), nullable=False)
    
    # Store multiple emails as a comma-separated string
    emails = db.Column(db.String(500), nullable=False)
    medicamente = db.Column(db.String(1000), nullable=True)  # Also stored as comma-separated values
    
    devices = db.relationship('Device', backref='user', lazy=True)
    parkinson_metrics = db.relationship('ParkinsonMetric', backref='user', lazy=True)
    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verifies the password against the stored hash."""
        return check_password_hash(self.password, password)

    def set_emails(self, emails):
        """
        Accepts a list of emails and stores them as a comma-separated string.
        """
        if isinstance(emails, list):
            self.emails = ','.join(emails)
        else:
            self.emails = emails  # fallback if already a string

    def get_emails(self):
        """
        Returns the emails as a list.
        """
        return self.emails.split(',') if self.emails else []

    def set_medicamente(self, meds):
        if isinstance(meds, list):
            self.medicamente = ','.join(meds)
        else:
            self.medicamente = meds

    def get_medicamente(self):
        return self.medicamente.split(',') if self.medicamente else []
        
    def to_dict(self):
        """Serialize user data into a dictionary."""
        return {
            'id': self.id,
            'nume': self.nume,
            'age': self.age,
            'emails': self.get_emails(),
            'medicamente': self.get_medicamente()
        }

class Device(db.Model):
    __tablename__ = 'device'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, nullable=True)
    
    sensor_data = db.relationship('SensorData', backref='device', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'device_type': self.device_type,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }

class SensorData(db.Model):
    __tablename__ = 'sensordata'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(36), db.ForeignKey('device.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    accel_x = db.Column(db.Float, nullable=True)
    accel_y = db.Column(db.Float, nullable=True)
    accel_z = db.Column(db.Float, nullable=True)
    gyro_x = db.Column(db.Float, nullable=True)
    gyro_y = db.Column(db.Float, nullable=True)
    gyro_z = db.Column(db.Float, nullable=True)
    battery_level = db.Column(db.Float, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'timestamp': self.timestamp.isoformat(),
            'accel_x': self.accel_x,
            'accel_y': self.accel_y,
            'accel_z': self.accel_z,
            'gyro_x': self.gyro_x,
            'gyro_y': self.gyro_y,
            'gyro_z': self.gyro_z,
            'battery_level': self.battery_level
        }
    
class ParkinsonMetric(db.Model):
    __tablename__ = 'parkinson_metric'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    shake_per_minute = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat(),
            'shake_per_minute': self.shake_per_minute
        }

class MedicationLog(db.Model):
    __tablename__ = 'medication_log'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat()
        }
