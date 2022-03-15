import requests
from datetime import date, timedelta, datetime
from common.classes import Channel, Program
from common.utils import get_channelid_by_name, get_epg_time
from sites.astro import ALL_CHANNELS_URL

TIMEZONE_OFFSET = "+0700"
ALL_CHANNELS_URL = "http://www.dens.tv/tvpage_octo/channelgen/2"
PROGRAM_URL = "http://www.dens.tv/tvpage_octo/epgchannel2/{date}/{channel_id}"


def get_all_channels():
    try:
        response = requests.post(ALL_CHANNELS_URL)
    except requests.RequestException as e:
        raise SystemExit(e)

    channels = response.json()["data"]

    channels = [Channel(
        channel["seq"],
        channel["title"]+".Id",
        channel["title"],
        "http://www.dens.tv/images/channel-logo/"+channel["seq"]+".jpg") for channel in channels]

    return channels


def get_programs_by_channel(channel_name, *args):
    days = args[0] if args else 1

    date_today = date.today()
    all_programs = []

    channel_id = get_channelid_by_name(channel_name, "dens_tv")

    for i in range(days):
        date_input = date_today + timedelta(days=i)
        url = PROGRAM_URL.format(date=date_input, channel_id=channel_id)

        try:
            r = requests.get(url)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        if r.status_code != 200:
            return [Program()]

        output = r.json()["data"]

        programs = []

        for program in output:
            start_time = datetime.strptime(
                program["starttime"], "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(
                program["endtime"], "%Y-%m-%d %H:%M:%S")
            obj = Program(
                channel_name,
                program["title"],
                "",
                get_epg_time(start_time, TIMEZONE_OFFSET),
                get_epg_time(end_time, TIMEZONE_OFFSET),
                ""
            )
            programs.append(obj)

        all_programs.extend(programs)

    return all_programs
