# WebSocket module initialization
import asyncio
import logging
from .routes import register_device

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
