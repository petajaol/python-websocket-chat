import asyncio
import websockets
from collections import deque

connected_clients = []
message_deque_max_length = 100
message_deque = deque(maxlen=message_deque_max_length)


async def handle_connection(websocket, path):
    # Add the websocket to a list of connected clients
    connected_clients.append(websocket)
    if len(message_deque) > 0:
        await websocket.send(create_string_from_message_deque())
    try:
        while True:
            # Receive a message from the client
            message = await websocket.recv()
            message_deque.append(message)

            # Broadcast the message to all connected clients
            for client in connected_clients:
                if client != websocket:
                    await client.send(message)
    finally:
        # Remove the websocket from the list of connected clients
        connected_clients.remove(websocket)


def create_string_from_message_deque():
    message_str = ""
    for message in message_deque:
        if message_str:
            message_str += "\r\n"
        message_str += message
    return message_str


# Start the WebSocket server
start_server = websockets.serve(handle_connection, "localhost", 8000)
# Run the server indefinitely
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
