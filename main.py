from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, WebSocket, Request
from fastapi.params import Body
from pydantic import BaseModel
import json
import asyncio
import datetime
from util import filter_json_btw_time, get_datetime, filter_by_msg_type
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000"
]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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


messageType = {
    'NewOrderRequest': 1, 'NewOrderAcknowledged': 2, 'CancelRequest': 3, 'CancelAcknowledged': 4, 'Cancelled': 5, "Trade": 6, }


def normalize_uid(data):
    anomalies_cache = {}
    for i in data:
        uid = i["OrderID"]
        if uid not in anomalies_cache:
            messageTypeNum = messageType[i["MessageType"]]
            anomalies_cache[uid] = [messageTypeNum]
        else:
            messageTypeNum = messageType[i["MessageType"]]
            anomalies_cache[uid].append(messageTypeNum)
    return anomalies_cache


# Change the json file timestamp
data = clean_data()

correct_messageType_a = [1, 2, 3, 4, 5]
correct_messageType_b = [1, 2, 6]

# with open(file_name,"r") as json_file:
#     data = iter(json.loads(json_file.read()))


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
async def get_top_gainers_top_losers(end_time: str, start_time: str = "2023-01-06 09:27:00.000000"):
    result = []
    symbol = {}
    start_time1 = get_datetime(start_time)
    end_time1 = get_datetime(end_time)

    old_data = data

    filtered_data = filter_json_btw_time(
        old_data, end_time=end_time1, start_time=start_time1)

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


@app.get("/getTreeMap")
async def get_tree_map(msg_type: str, end_time: str, start_time: str = "2023-01-06 09:27:00.000000"):
    end_time1 = get_datetime(end_time)
    start_time1 = get_datetime(start_time)
    filtered_data_with_time = filter_json_btw_time(
        data, end_time=end_time1, start_time=start_time1)
    filtered_traded_data = filter_by_msg_type(
        filtered_data_with_time, msg_type)

    symbol = {}
    for i in filtered_traded_data:
        key = i["Symbol"]
        if key not in symbol:

            symbol[key] = 1
        else:
            symbol[key] += 1
    return {"message": symbol}


def is_valid_messageType(values):
    bool_message_a = True
    bool_message_b = True
    for i in range(len(values)):
        if (values[i] == correct_messageType_a[i]):
            bool_message_a = False

    for i in range(len(values)):

        if (i < 3 and values[i] == correct_messageType_b[i]):
            bool_message_b = False

    if (bool_message_a or bool_message_b):
        return False
    else:
        return True


@app.get("/getAnamolies")
async def get_anomalies(end_time: str, start_time: str = "2023-01-06 09:27:00.000000"):
    end_time1 = get_datetime(end_time)
    start_time1 = get_datetime(start_time)
    filtered_data_with_time = filter_json_btw_time(
        data, end_time=end_time1, start_time=start_time1)
    anomalies_cache = normalize_uid(filtered_data_with_time)
    anomaly_dict = {}
    for key in anomalies_cache:
        values = anomalies_cache[key]
        anomaly_dict[key] = is_valid_messageType(values=values)
    return {"message": anomaly_dict}
