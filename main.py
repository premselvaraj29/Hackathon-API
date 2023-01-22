from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, WebSocket, Request
from fastapi.params import Body
from pydantic import BaseModel
import json
import asyncio
import datetime
from util import hello


app = FastAPI()

file_name = "./assets/TSXData.json"

f = open(r"C:\Users\prems\Documents\Untitled Folder\Assets\TSXData.json")

# returns JSON object as
# a dictionary
data = json.load(f)


def clean_data():
    length_timestamp = len(data[0]["TimeStamp"])
    str_split = slice(0, length_timestamp-6)

    for i in data:
        i["TimeStamp"] = datetime.datetime.fromisoformat(
            i["TimeStamp"][str_split])
    return data


# Change the json file timestamp
data = clean_data()


# with open(file_name,"r") as json_file:
#     data = iter(json.loads(json_file.read()))


def filter_json_btw_time(old_data, end_time, start_time):
    return [i for i in old_data if start_time < i["TimeStamp"] and i["TimeStamp"] < end_time]



@app.get("/")
async def root():
    # print("Hello world is printing")
    start_time = datetime.datetime.fromisoformat("2023-01-06 09:29:00.000000")
    end_time = datetime.datetime.fromisoformat('2023-01-06 09:30:00.995262')
   
    return {"message": "hello world"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await asyncio.sleep(0.1)
        payload = next(data)
        await websocket.send_json(payload)


@app.get("/topgainers")
async def get_top_gainers_top_losers(end_time: str, start_time: str="2023-01-06 09:27:00.000000"):
    result = []
    symbol = {}
    start_time1 = datetime.datetime.fromisoformat(start_time)
    end_time1 = datetime.datetime.fromisoformat(end_time)

    old_data= data

    filtered_data = filter_json_btw_time( old_data, end_time=end_time1, start_time=start_time1)

   
    for i in filtered_data:
  
        if (i["MessageType"] == "Trade"):
            key = i["Symbol"]
            if not key in symbol:

                symbol[key] = []
            symbol[key].append(i["OrderPrice"])


    # Calculating percent
    for key in list(symbol):
        values = symbol[key]
        if len(values) > 1:
            symbol["percent"] = symbol[key][len(values)-1] - symbol[key][0]
        else:
            symbol["percent"] = 0

        result.append({key: symbol["percent"]})
    return {"message": result}
