import asyncio
import websockets
from collections import deque

connected_clients = {}
message_deque_max_length = 100
message_deque = deque(maxlen=message_deque_max_length)


async def handle_connection(websocket, path):
    # Add the websocket to a list of connected clients
    user_name = await ask_user_name(websocket)
    await send_message_to_all_except_one(user_name, "'{}' joined. Please be kind to them.".format(user_name))
    connected_clients[user_name] = websocket
    await websocket.send("Connected!")
    if len(message_deque) > 0:
        await websocket.send(create_string_from_message_deque())
    try:
        while True:
            # Receive a message from the client
            message = await websocket.recv()
            message_deque.append("{}: {}".format(user_name, message))

            # Broadcast the message to all connected clients
            await send_message_to_all_except_one(user_name, "{}: {}".format(user_name, message))
    finally:
        # Remove the websocket from the list of connected clients
        del connected_clients[user_name]


async def send_message_to_all_except_one(user_name, message):
    for key in connected_clients.keys():
        if key != user_name:
            await connected_clients[key].send(message)


def create_string_from_message_deque():
    message_str = ""
    for message in message_deque:
        if message_str:
            message_str += "\r\n"
        message_str += message
    return message_str


async def ask_user_name(client):
    await client.send("Send username.")
    while True:
        user_name = await client.recv()
        if user_name in connected_clients.keys():
            await client.send("User name is already taken. Choose another user name.")
        else:
            return user_name

# Start the WebSocket server
start_server = websockets.serve(handle_connection, "localhost", 8000)
# Run the server indefinitely
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
