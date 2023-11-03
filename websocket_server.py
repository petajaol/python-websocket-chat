import asyncio
import websockets
from collections import deque

connected_clients = {}
message_deque_max_length = 100
message_deque = deque(maxlen=message_deque_max_length)


async def handle_connection(websocket, path):
    user_name = await ask_user_name(websocket)
    message = f"{user_name} joined. Please be kind to them."
    await broadcast_message(message)
    connected_clients[user_name] = websocket
    await websocket.send("Connected!")
    if len(message_deque) > 0:
        await websocket.send(create_string_from_message_deque())
    try:
        while True:
            message = await websocket.recv()
            message_deque.append("{}: {}".format(user_name, message))

            await broadcast_message(message)
    finally:
        del connected_clients[user_name]


async def broadcast_message(message):
    for key in connected_clients.keys():
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


start_server = websockets.serve(handle_connection, "localhost", 8000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
