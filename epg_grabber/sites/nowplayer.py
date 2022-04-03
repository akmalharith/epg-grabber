from typing import List
import requests
from datetime import datetime
from pathlib import Path
from pytz import timezone
from urllib3 import request
from source.classes import Channel, Program
from source.utils import get_channel_by_name, get_epg_datetime
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'

try:
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass

ALL_CHANNELS_URL = "https://nowplayer.now.com/channels"
PROGRAMS_URL = "https://nowplayer.now.com/tvguide/epglist?channelIdList={id}&day={days}"
PROGRAMS_DETAIL_URL = "https://nowplayer.now.com/tvguide/epgprogramdetail?programId={program_id}"


def get_all_channels() -> List[Channel]:
    try:
        r = requests.get(ALL_CHANNELS_URL)
    except request.exceptions.RequestException as e:
        raise SystemExit(e)
    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    soup = BeautifulSoup(r.text, features="html.parser")
    divs = soup.find_all(
        "div", {
            "class": "col-md-2 col-sm-3 product-item tv-guide-all"})

    channels = [Channel(
                id = div.find("p", {"class": "channel"}).text.replace("CH", ""),
                tvg_id = div.find("p", {"class": "img-name"}).text.strip() + ".Hk",
                tvg_name = div.find("p", {"class": "img-name"}).text.strip(),
                tvg_logo = div.find("img")['src'],
                sanitize = True
                ) for div in divs]

    return channels


def get_programs_by_channel(channel_name: str, *args) -> List[Program]:
    days = args[0] if args else 1
    days = 7 if days > 7 else days

    channel = get_channel_by_name(channel_name, Path(__file__).stem)

    channel_url = PROGRAMS_URL.format(id=channel.id, days=days)

    try:
        r = requests.get(channel_url)

    except Exception as e:
        raise SystemExit(e)

    output = r.json()

    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    program_json = output[0]

    programs = []

    for program in program_json:

        title, description = get_program_details(program['vimProgramId'])

        start_timestamp = int(int(program["start"]) / 1000)
        start_program = datetime.fromtimestamp(
            start_timestamp, timezone("UTC"))

        end_timestamp = int(int(program["end"]) / 1000)
        end_program = datetime.fromtimestamp(end_timestamp, timezone("UTC"))

        obj = Program(
            channel_name = channel.tvg_id,
            title = title,
            description = description,
            start = get_epg_datetime(start_program),
            stop = get_epg_datetime(end_program)
        )
        programs.append(obj)

    return programs


def get_program_details(program_id: str) -> str:
    programs_detail_url = PROGRAMS_DETAIL_URL.format(program_id=program_id)

    try:
        r = requests.get(programs_detail_url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    output = r.json()

    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    if "engSynopsis" in output:
        return output['engSeriesName'], output['engSynopsis']
    else:
        return output['engSeriesName'], ""
