from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from bleak import BleakScanner, BleakClient
import asyncio

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    with open('static/index.html', 'r') as f:
        return HTMLResponse(content=f.read())

@app.get("/scan")
async def scan():
    devices = await BleakScanner.discover()
    return [{"name": device.name or "Unknown", "address": device.address} for device in devices]

@app.post("/connect")
async def connect(request: Request):
    data = await request.json()
    address = data.get("address")
    if not address:
        return {"success": False, "message": "No address provided."}
    
    try:
        async with BleakClient(address) as client:
            if client.is_connected:
                return {"success": True, "message": f"Connected to {address}."}
            else:
                return {"success": False, "message": f"Failed to connect to {address}."}
    except Exception as e:
        return {"success": False, "message": str(e)}
