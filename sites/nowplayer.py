from datetime import datetime
from pytz import timezone
import requests
from urllib3 import request
from common.classes import Channel, Program
from common.utils import get_channel_by_name, get_channelid_by_name, get_epg_time
from bs4 import BeautifulSoup

ALL_CHANNELS_URL = "https://nowplayer.now.com/channels"
PROGRAMS_URL = "https://nowplayer.now.com/tvguide/epglist?channelIdList={id}&day={days}"
PROGRAMS_DETAIL_URL = "https://nowplayer.now.com/tvguide/epgprogramdetail?programId={program_id}"

def get_all_channels():
    try:
        r = requests.get(ALL_CHANNELS_URL)
    except request.exceptions.RequestException as e:
        raise SystemExit(e)
    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    soup = BeautifulSoup(r.text,features="html.parser")
    divs = soup.find_all("div", {"class": "col-md-2 col-sm-3 product-item tv-guide-all"})

    channels = [Channel(
                div.find("p", {"class": "channel"}).text.replace("CH",""),
                div.find("p", {"class": "img-name"}).text.strip()+".Hk",
                div.find("p", {"class": "img-name"}).text.strip(),
                div.find("img")['src']
            ) for div in divs]

    return channels

def get_programs_by_channel(channel_name, *args):
    days = args[0] if args else 1
    days = 7 if days > 7 else days

    channel = get_channel_by_name(channel_name, "nowplayer")
    
    channel_url = PROGRAMS_URL.format(id=channel.id,days=days)

    try:
        r = requests.get(channel_url)

    except requests.exceptions.RequestException as e:
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

        obj = Program (
            channel.tvg_id,
            title, 
            description,
            get_epg_time(start_program),
            get_epg_time(end_program),
            "" # TODO: episode
        )
        programs.append(obj)
            
    return programs

def get_program_details(program_id):
    programs_detail_url = PROGRAMS_DETAIL_URL.format(program_id=program_id)

    try:
        r = requests.get(programs_detail_url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    output = r.json()

    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    return output['engSeriesName'], output['engSynopsis']
