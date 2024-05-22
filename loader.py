import json

# Channel ids are defined here
CHANNEL_IDS = [
    "C0XXXXXXXXX",  # test-fridge-management
]  # channel id of the test channel


def _blank_session():
    DCDNAME = {cid: "-1" for cid in CHANNEL_IDS}  # cooldown name
    DREQUESTED_USERS = {cid: {} for cid in CHANNEL_IDS}  # key: channel_id, value: dict
    DSETTLED_USERS = {cid: {} for cid in CHANNEL_IDS}  # key: channel_id, value: dict
    DMANAGEMENT_BOARD_TS = {
        cid: "-1" for cid in CHANNEL_IDS
    }  # timestamp of the management board

    return (DCDNAME, DREQUESTED_USERS, DSETTLED_USERS, DMANAGEMENT_BOARD_TS)


import glob
import pathlib


def _parse(js):
    cid = js["CHANNEL_ID"]
    n = js["CDNAME"]
    r = js["REQUESTED_USERS"]
    s = js["SETTLED_USERS"]
    ts = js["MANAGEMENT_BOARD_TS"]
    st = js["STATUS"]

    return (n, r, s, ts)


def _recover_channel(channel_id):
    fpath = "./tmp/" + channel_id + ".json"
    with open(fpath, "r") as f:
        js = json.load(f)
    ch = _parse(js)
    return ch


def _recover_session():
    files = glob.glob("./tmp/*.json")
    channel_logs = [pathlib.Path(file).stem for file in files]

    loadable_channel_ids = list(set(CHANNEL_IDS) & set(channel_logs))

    DCDNAME, DREQUESTED_USERS, DSETTLED_USERS, DMANAGEMENT_BOARD_TS = _blank_session()

    for cid in CHANNEL_IDS:
        if cid in loadable_channel_ids:
            print("loading channel: ", cid)
            n, r, s, ts = _recover_channel(cid)

            DCDNAME[cid] = n
            DREQUESTED_USERS[cid] = r
            DSETTLED_USERS[cid] = s
            DMANAGEMENT_BOARD_TS[cid] = ts

    return (DCDNAME, DREQUESTED_USERS, DSETTLED_USERS, DMANAGEMENT_BOARD_TS)


def initialize_session(load=True):
    if load:
        sess = _recover_session()
    else:
        sess = _blank_session()

    return sess
