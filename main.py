from typing import Union
from slack_bolt import App
from slack_sdk.web.client import WebClient
from slack_bolt.context.ack.ack import Ack
from slack_bolt.context.say.say import Say
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt import App
import os
import pandas as pd
from backend import get_body
import json
import time
from loader import (
    CHANNEL_IDS,
    initialize_session,
)

# -------------------initialize the app----------------------------
with open("config/credentials.json", "r") as f:
    base = json.load(f)
    credentials = base["CooldownManager"]

app = App(token=credentials["SLACK_BOT_TOKEN"])
client = WebClient(token="YOUR_BOT_USER_ACCESS")

(
    DCDNAME,
    DREQUESTED_USERS,
    DSETTLED_USERS,
    DMANAGEMENT_BOARD_TS,
) = initialize_session(load=True)


# FLAG_LOAD_BACKUP = False
# if FLAG_LOAD_BACKUP:
#     with open("config/managing_now.json", "r") as f:
#         managing_now = json.load(f)
#         for key, value in managing_now.items():
#             CHANNEL_ID = key
#             DCDNAME[key] = value["cdname"]
#             DREQUESTED_USERS[key] = value["requested_users"]
#             DSETTLED_USERS[key] = value["settled_users"]
#             DMANAGEMENT_BOARD_TS[key] = value["management_board_ts"]

# -----------------------Example format---------------------------
# DREQUESTED_USERS = {
# "user000": None,
# "user001": None,
# }  # key: user_id, value: dict

# DSETTLED_USERS = {
#     "user000-$ts": {
#         "device_name": "device000",
#         "expriment_description": "measure",
#         "ts": "",
#     },
#     "user001-$ts": {
#         "device_name": "device000",
#         "expriment_description": "measure",
#         "ts": "",
#     },
# }  # key: user_id, value: dict
# --------------------------------------------------------------


@app.command("/echo_info")
def echo_info(ack, body, say):
    ack()
    print(body)
    # dump body to a file with datetime
    dt_str = time.strftime("%Y%m%d-%H%M%S")
    with open(f"./debug/body_{dt_str}.json", "w") as f:
        json.dump(body, f)
    return


def _save_snapshot(channel_id, status=""):
    # make a dataframe of global variables and save it by appending to the csv
    snapshot = {
        "CHANNEL_ID": channel_id,
        "CDNAME": DCDNAME[channel_id],
        "REQUESTED_USERS": DREQUESTED_USERS[channel_id],
        "SETTLED_USERS": DSETTLED_USERS[channel_id],
        "MANAGEMENT_BOARD_TS": DMANAGEMENT_BOARD_TS[channel_id],
        "STATUS": status,  # "OPEN", "COMPLETE", "ABORT", "NEWPOST", "UPDATE", "DELETE", "BACKUP"
    }
    df_oneline = pd.DataFrame.from_dict([snapshot])
    # print(df_oneline)
    # check if history.csv exists
    if not os.path.exists("history/history.csv"):
        df_oneline.to_csv("./history/history.csv", index=False)
    else:
        df_oneline.to_csv("./history/history.csv", mode="a", header=False, index=False)

    # overwrite tmp file
    with open(f"./tmp/{channel_id}.json", "w") as f:
        json.dump(snapshot, f)
    print("SNAPSHOT SAVED:", status)
    return


@app.command("/cdm_open")
def open_board(ack, body, say):
    ack()  # acknowledge the command
    global DMANAGEMENT_BOARD_TS, CDNAME
    # get the name of the cooldown cycle
    CDNAME = body["text"]
    channel_id = body["channel_id"]
    # print("OEPN BOARD", CDNAME)

    params = {
        "cdname": CDNAME,
        "users_settled": DSETTLED_USERS[channel_id],
        "users_requested": DREQUESTED_USERS[channel_id],
    }

    message = {
        "channel": channel_id,
        "blocks": get_body(params),
        "text": "CDM for {} is now open".format(CDNAME),
    }
    time.sleep(1)
    response = say.client.chat_postMessage(**message)

    DMANAGEMENT_BOARD_TS[channel_id] = str(response.data["ts"])
    DCDNAME[channel_id] = CDNAME

    # add binding information
    message_binding = {
        "channel": channel_id,
        "text": f"Binding for this board : {DMANAGEMENT_BOARD_TS[channel_id]}",  # ts of the management board
    }
    response_binding = say.client.chat_postMessage(**message_binding)
    # say(f"Binding for this board : {MANAGEMENT_BOARD_TS}")

    _save_snapshot(channel_id, "OPEN")
    return response


@app.command("/cdm_close")
def close_board(ack, body, say):
    ack()
    global DCDNAME, DREQUESTED_USERS, DSETTLED_USERS, DMANAGEMENT_BOARD_TS

    channel_id = body["channel_id"]
    # make it archive
    params = {
        "cdname": DCDNAME[channel_id] + "(COMPLETE)",
        "users_settled": DSETTLED_USERS[channel_id],
        "users_requested": DREQUESTED_USERS[channel_id],
    }
    message_update = {
        "channel": channel_id,
        "blocks": get_body(params),
        "text": "CDM for {} is now closed".format(DCDNAME[channel_id]),
    }
    say.client.chat_update(ts=DMANAGEMENT_BOARD_TS[channel_id], **message_update)

    _save_snapshot(channel_id, "COMPLETE")

    DCDNAME[channel_id] = "-1"  # cooldown name
    DREQUESTED_USERS[channel_id] = {}
    DSETTLED_USERS[channel_id] = {}
    DMANAGEMENT_BOARD_TS[channel_id] = "-1"  # timestamp of the management board
    
    # remove tmp file
    os.remove(f"./tmp/{channel_id}.json")
    return


@app.command("/cdm_force_abort")
def force_abort(ack, body, say):
    """
    Remove the board message from slack
    """
    ack()  # acknowledge the command
    global DMANAGEMENT_BOARD_TS, CDNAME
    # get the name of the cooldown cycle
    confirm = body["text"]
    if not (confirm == "0000"):
        return

    channel_id = body["channel_id"]
    board_ts = DMANAGEMENT_BOARD_TS[channel_id]

    response = say.client.chat_delete(channel=channel_id, ts=board_ts)

    DCDNAME[channel_id] = "-1"  # cooldown name
    DREQUESTED_USERS[channel_id] = {}
    DSETTLED_USERS[channel_id] = {}
    DMANAGEMENT_BOARD_TS[channel_id] = "-1"

    return response


def _update_board(channel_id, client):

    params = {
        "cdname": DCDNAME[channel_id],
        "users_requested": DREQUESTED_USERS[channel_id],
        "users_settled": DSETTLED_USERS[channel_id],
    }
    message_update = {
        "channel": channel_id,
        "blocks": get_body(params),
        "text": "CDM for {} updated".format(DCDNAME[channel_id]),
    }
    time.sleep(1)
    client.chat_update(ts=DMANAGEMENT_BOARD_TS[channel_id], **message_update)
    _save_snapshot(channel_id, "UPDATE")
    pass


@app.action("want_to_use_fridge")
def add_to_requested_users(ack: Ack, body: dict, say: Say):
    global DREQUESTED_USERS
    ack()  # acknowledge the action
    # Access the user ID who clicked the button
    user_id = body["user"]["id"]
    channel_id = body["container"]["channel_id"]

    DREQUESTED_USERS[channel_id][user_id] = None

    params = {
        "cdname": DCDNAME[channel_id],
        "users_settled": DSETTLED_USERS[channel_id],
        "users_requested": DREQUESTED_USERS[channel_id],
    }

    message_update = {
        "channel": channel_id,
        "blocks": get_body(params),
        "text": "A user reqested a slot for {}".format(DCDNAME[channel_id]),
    }
    say.client.chat_update(ts=DMANAGEMENT_BOARD_TS[channel_id], **message_update)
    _save_snapshot(channel_id, "REQUEST")


@app.action("skip_fridge")
def remove_from_requested_users(ack, body, say):
    global DREQUESTED_USERS
    ack()  # acknowledge the action
    # Access the user ID who clicked the button
    user_id = body["user"]["id"]
    channel_id = body["container"]["channel_id"]

    if user_id in DREQUESTED_USERS[channel_id]:
        del DREQUESTED_USERS[channel_id][user_id]

    params = {
        "cdname": DCDNAME[channel_id],
        "users_settled": DSETTLED_USERS[channel_id],
        "users_requested": DREQUESTED_USERS[channel_id],
    }
    message_update = {
        "channel": channel_id,
        "blocks": get_body(params),
        "text": "A user removed request for {}".format(DCDNAME[channel_id]),
    }
    say.client.chat_update(ts=DMANAGEMENT_BOARD_TS[channel_id], **message_update)
    _save_snapshot(channel_id, "WITHDRAW")


def _handle_boardmessage_update(event, channel_id, client):
    global DSETTLED_USERS
    # extrace parameters and update them
    username = event.get("user")
    text = event.get("text")[3:-3]  # strip the ``` from the text

    ts = event.get("ts")
    device_name = text.split(" ")[0]
    expriment_description = " ".join(text.split(" ")[1:])

    # use - to allow multiple requests from the same user
    username += "-" + ts
    DSETTLED_USERS[channel_id][username] = {
        "device_name": device_name,
        "expriment_description": expriment_description,
        "ts": ts,
    }

    # update the board
    _update_board(channel_id, client)

    return


def _handle_boardmessage_delete(event, channel_id, client):
    global DSETTLED_USERS
    username = event.get("user")
    ts = event.get("ts")

    username = username + "-" + ts
    if username in DSETTLED_USERS[channel_id]:
        del DSETTLED_USERS[channel_id][username]
    # update the board
    _update_board(channel_id, client)


def _is_device_settlement_request(s: str) -> Union[bool]:
    return s.startswith("```") and s.endswith("```")


def _flag_boardmessage(event):
    # print(event)
    thread_ts = ""
    message_type = ""
    channel_id = event.get("channel")
    event_purified = None

    if event.get("subtype") == "message_changed":
        thread_ts = event.get("message").get("thread_ts")
        text = event.get("message").get("text")

        if _is_device_settlement_request(text):
            message_type = "update"
            event_purified = event.get("message")
    elif event.get("subtype") == "message_deleted":
        thread_ts = event.get("previous_message").get("thread_ts")
        text = event.get("previous_message").get("text")

        if _is_device_settlement_request(text):
            message_type = "delete"
            event_purified = event.get("previous_message")
    else:
        thread_ts = event.get("thread_ts")
        text = event.get("text")

        if _is_device_settlement_request(text):
            message_type = "newpost"
            event_purified = event

    if thread_ts == DMANAGEMENT_BOARD_TS[channel_id]:
        return (thread_ts, message_type, channel_id, event_purified)
    else:
        return (thread_ts, "other", channel_id, event_purified)


@app.event("message")
def handle_message_events(ack, event, client):
    ack()
    thread_ts, message_type, channel_id, event_msg = _flag_boardmessage(event)

    # print(event)
    if message_type == "newpost":
        _handle_boardmessage_update(event_msg, channel_id, client)
    elif message_type == "update":
        event_msg = event.get("message")
        assert event_msg is not None
        _handle_boardmessage_update(event_msg, channel_id, client)
    elif message_type == "delete":
        event_msg = event.get("previous_message")
        assert event_msg is not None
        _handle_boardmessage_delete(event_msg, channel_id, client)
    else:
        pass
    return


if __name__ == "__main__":
    SocketModeHandler(app, credentials["SLACK_APP_TOKEN"]).start()
