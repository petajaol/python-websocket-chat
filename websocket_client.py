import threading
import asyncio
import websockets


async def receive_messages(websocket):
    while True:
        response = await websocket.recv()
        print(response)


def send_messages(websocket):
    while True:
        message = input()
        asyncio.run(websocket.send(message))  # Use asyncio.run to send the message


async def connect_to_server():
    async with websockets.connect("ws://localhost:8000") as websocket:
        # Create a thread for sending messages
        send_thread = threading.Thread(target=send_messages, args=(websocket,))
        send_thread.daemon = (
            True  # Set the thread as a daemon to exit when the main program exits
        )
        send_thread.start()

        # Run the event loop for receiving messages
        await receive_messages(websocket)


# Connect the WebSocket client
asyncio.get_event_loop().run_until_complete(connect_to_server())
