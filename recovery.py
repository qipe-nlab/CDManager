# recover previous session from tmp files
import glob
import pathlib


def _parse(js):
    return


def _recover_channel(channel_id):
    pass


def recover_session():

    channel_sess = []

    # recover channels
    files = glob.glob("./tmp/*.json")
    for file in files:
        channel_id = pathlib.Path(file).stem
        ch = _recover_channel(channel_id)
        channel_sess.append(ch)

    session = ()


def _initialize_session():
    pass
