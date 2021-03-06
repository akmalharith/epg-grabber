from typing import List
import requests
from datetime import datetime
from helper.classes import Channel, Program
from helper.utils import get_epg_datetime
from sites.auth.redbull_tv_auth import get_session

session_headers = get_session()

PROGRAMS_URL = "https://api.redbull.tv/v3/epg?complete=true"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


# Hardcode since we are only dealing with one channel
def get_all_channels() -> List[Channel]:
    return [Channel(
        "redbulltv",
        "redbulltv.Us",
        "RedBull TV",
        "https://img.redbull.com/images/e_trim:10:transparent/w_260/q_auto,f_png/redbullcom/2020/9/28/thlczntgyjpczxckt3ii/redbulllogo"
    )]


def get_programs_by_channel(channel_name: str, *args) -> List[Program]:
    url = PROGRAMS_URL

    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:!eNULL:!MD5'

    try:
        r = requests.get(url, headers=session_headers)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    output = r.json()
    programs = []
    program_json = output["items"]

    for program in program_json:
        start_time = datetime.strptime(
            program["start_time"][:-10], DATETIME_FORMAT)
        end_time = datetime.strptime(
            program["end_time"][:-10], DATETIME_FORMAT)

        obj = Program(
            channel_name=get_all_channels()[0].tvg_id,
            title=program["title"] + " - " + program["subheading"],
            description=program["long_description"],
            start=get_epg_datetime(start_time),
            stop=get_epg_datetime(end_time)
        )
        programs.append(obj)

    return programs
