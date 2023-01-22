import datetime


def hello():
    pass


def filter_json_btw_time(old_data, end_time, start_time):
    return [i for i in old_data if start_time < i["TimeStamp"] and i["TimeStamp"] < end_time]


def filter_by_msg_type(old_data, msg_type):
    return [i for i in old_data if i["MessageType"] == msg_type]


def get_datetime(strTime: str):
    return datetime.datetime.fromisoformat(strTime)
