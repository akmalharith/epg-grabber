from typing import List
import requests
from pathlib import Path
from datetime import date, timedelta, datetime
from source.classes import Channel, Program
from source.utils import get_channel_by_name, get_epg_datetime

TIMEZONE_OFFSET = "+0700"
ALL_CHANNELS_URL = "http://www.dens.tv/tvpage_octo/channelgen/2"
PROGRAM_URL = "http://www.dens.tv/tvpage_octo/epgchannel2/{date}/{channel_id}"


def get_all_channels() -> List[Channel]:
    try:
        response = requests.post(ALL_CHANNELS_URL)
    except requests.RequestException as e:
        raise SystemExit(e)

    channels = response.json()["data"]

    channels = [
        Channel(
            id = channel["seq"],
            tvg_id = channel["title"] +
            ".Id",
            tvg_name = channel["title"],
            tvg_logo = "http://www.dens.tv/images/channel-logo/" +
            channel["seq"] +
            ".jpg",
            sanitize = True) for channel in channels]

    return channels


def get_programs_by_channel(channel_name: str, *args) -> List[Program]:
    days = args[0] if args else 1

    date_today = date.today()
    all_programs = []

    channel = get_channel_by_name(channel_name, Path(__file__).stem)

    for i in range(days):
        date_input = date_today + timedelta(days=i)
        url = PROGRAM_URL.format(date=date_input, channel_id=channel.id)

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
                channel_name = channel_name,
                title = program["title"],
                start = get_epg_datetime(start_time, TIMEZONE_OFFSET),
                stop = get_epg_datetime(end_time, TIMEZONE_OFFSET)
            )
            programs.append(obj)

        all_programs.extend(programs)

    return all_programs
