import asyncio
import json
from collections import deque
from datetime import datetime
import websockets


connected_clients = {}
MESSAGE_LOG_MAX_LENGTH = 100
message_log = deque(maxlen=MESSAGE_LOG_MAX_LENGTH)


async def initialize_connection(client, path):
    user_name = await ask_user_name(client)
    connected_clients[user_name] = client
    await broadcast_message(f"{user_name} joined. Please be kind to them.", user_name)
    await retrieve_message_log(client)
    await client.send("Connected!")
    while True:
        try:
            await wait_for_messages(user_name, client)
        except websockets.exceptions.ConnectionClosed:
            if user_name in connected_clients:
                await broadcast_message(f"{user_name} disconnected.", user_name)
                del connected_clients[user_name]
            break


async def wait_for_messages(user_name, client):
    while True:
        message = {
            "user_name": user_name,
            "message": await client.recv(),
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }
        message_log.append(message)
        await broadcast_message(json.dumps(message))


async def retrieve_message_log(client):
    if len(message_log) > 0:
        message_json = json.dumps(list(message_log))
        await client.send(message_json)


async def broadcast_message(message, sender_name=None):
    for user_name, client in connected_clients.items():
        if sender_name is None or (
            sender_name is not None and user_name != sender_name
        ):
            await client.send(message)


async def ask_user_name(client):
    await client.send("Please enter a name.")
    while True:
        user_name = await client.recv()
        if not user_name:
            await client.send("Name cannot be empty. Please enter a name.")
        elif user_name in connected_clients:
            await client.send("User name is already taken. Choose another user name.")
        else:
            return user_name


start_server = websockets.serve(initialize_connection, "localhost", 8000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
