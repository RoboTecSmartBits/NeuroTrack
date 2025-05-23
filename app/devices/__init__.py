# Devices module initialization
from flask import Blueprint

# Create a Blueprint for device routes
from .routes import devices_bp

# Import routes is done in routes.py to avoid circular imports