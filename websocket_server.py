import asyncio
import json
from collections import deque
from datetime import datetime
import websockets
import pytz


connected_clients = {}
MESSAGE_LOG_MAX_LENGTH = 100
message_log = deque(maxlen=MESSAGE_LOG_MAX_LENGTH)


async def initialize_connection(client, path):
    user_name = await ask_user_name(client)
    connected_clients[user_name] = client
    message = {
        "type": "join_message",
        "user_name": user_name,
        "message": f"{user_name} joined. Please be kind to them.",
    }
    await broadcast_message(message)
    await retrieve_message_log(client)
    await retrieve_connected_users(client)
    await client.send(f"Joined as {user_name}!")
    while True:
        try:
            await wait_for_messages(user_name, client)
        except websockets.exceptions.ConnectionClosed:
            if user_name in connected_clients:
                message = {
                    "type": "part_message",
                    "user_name": user_name,
                    "message": f"{user_name} left.",
                }
                await broadcast_message(message)
                del connected_clients[user_name]
            break


async def wait_for_messages(user_name, client):
    message = {
        "type": "chat_message",
        "user_name": user_name,
        "message": await client.recv(),
        "timestamp": datetime.now(pytz.timezone("Europe/Helsinki")).strftime(
            "%H:%M:%S"
        ),
    }
    message_log.append(message)
    await broadcast_message(message)


async def retrieve_connected_users(client):
    if len(connected_clients) > 0:
        users_json = json.dumps(
            {"type": "user_list", "users": list(connected_clients.keys())}
        )
        await client.send(users_json)


async def retrieve_message_log(client):
    if len(message_log) > 0:
        message_json = json.dumps(
            {"type": "message_log", "messages": list(message_log)}
        )
        await client.send(message_json)


async def broadcast_message(message):
    for user_name, client in connected_clients.items():
        if message["type"] == "chat_message" or user_name != message["user_name"]:
            await client.send(json.dumps(message))


async def ask_user_name(client):
    await client.send("Please enter a name.")
    while True:
        user_name = await client.recv()
        if not user_name:
            await client.send("Name cannot be empty. Please enter a name.")
        elif len(user_name) > 10:
            await client.send("Name cannot be longer than 10 characters.")
        elif user_name in connected_clients:
            await client.send("User name is already taken. Choose another user name.")
        else:
            return user_name


start_server = websockets.serve(initialize_connection, "localhost", 8000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
