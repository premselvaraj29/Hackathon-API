from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException,WebSocket,Request
from fastapi.params import Body
from pydantic import BaseModel
import json
import asyncio

app = FastAPI()

file_name ="./assets/TSXData.json"

with open(file_name,"r") as json_file:
    data = iter(json.loads(json_file.read()))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await asyncio.sleep(0.1)
        payload = next(data)
        await websocket.send_json(payload)

