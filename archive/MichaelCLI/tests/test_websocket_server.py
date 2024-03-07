import asyncio
import websockets

async def echo(websocket, path):
    # Receiving a message from the client
    message = await websocket.recv()
    print(f"Received from client: {message}")

    # Sending a response back to the client
    await websocket.send("Hello, client!")

start_server = websockets.serve(echo, "localhost", 8765)

# Running the WebSocket server
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
