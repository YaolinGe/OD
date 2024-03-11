import asyncio
import websockets

async def websocket_client():
    uri = "ws://localhost:8765"  # URL of the WebSocket server
    async with websockets.connect(uri) as websocket:
        # Sending a message to the server
        await websocket.send("Hello, server!")

        # Receiving and printing the response from the server
        response = await websocket.recv()
        print(f"Received from server: {response}")

# Running the WebSocket client
asyncio.get_event_loop().run_until_complete(websocket_client())
