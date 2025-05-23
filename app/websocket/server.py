import asyncio
import threading
import websockets
import os

from app.websocket.routes import register_device

def start_ws_server(app):
    async def _serve():
        async def wrapped_handler(websocket, path):
            # Push Flask app context here
            with app.app_context():
                await register_device(websocket, path)

        # Bind to all interfaces so ESP32 can connect
        async with websockets.serve(wrapped_handler, "0.0.0.0", 8765):
            print("WebSocket server started on port 8765")
            await asyncio.Future()  # run forever

    # Each thread needs its own event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_serve())
    except Exception as e:
        print(f"WebSocket server failure: {e}")
    finally:
        loop.close()

def launch_in_thread(app):
    t = threading.Thread(target=start_ws_server, args=(app,), daemon=True)
    t.start()
    print("WebSocket server thread started")
