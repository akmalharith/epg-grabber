import requests
from pathlib import Path
from datetime import datetime, timedelta, timezone
from source.classes import Channel, Program
from source.utils import get_epg_datetime, get_channel_by_name

ALL_CHANNELS_URL = "https://api.cgtn.com/website/api/live/channel/list"
PROGRAM_URL = "https://api.cgtn.com/website/api/live/channel/epg/list?channelId={channel_id}&startTime={start_time}&endTime={end_time}"


def get_all_channels():
    query_url = ALL_CHANNELS_URL

    try:
        r = requests.get(query_url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    output = r.json()["data"]

    channels = [
        Channel(
            channel["id"],
            channel["title"] +
            ".Cn",
            channel["title"],
            channel["shareBody"]["iconUrl"]) for channel in output]

    return channels


def get_programs_by_channel(channel_name, *args):
    days = args[0] if args else 1
    days = 7 if days > 7 else days

    channel = get_channel_by_name(channel_name, Path(__file__).stem)

    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date_epoch = int(start_date.timestamp() * 1000)

    end_date = start_date + timedelta(days=1)
    end_date_epoch = int(end_date.timestamp() * 1000)

    url = PROGRAM_URL.format(
        channel_id=channel.id,
        start_time=start_date_epoch,
        end_time=end_date_epoch)

    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    output = r.json()["data"]

    programs = []

    for program in output:
        start_time_epoch = int(int(program["startTime"]) / 1000)
        start_time = datetime.fromtimestamp(start_time_epoch, timezone.utc)

        end_time_epoch = int(int(program["endTime"]) / 1000)
        end_time = datetime.fromtimestamp(end_time_epoch, timezone.utc)

        obj = Program(
            channel.tvg_id,
            program["name"],
            "",
            get_epg_datetime(start_time),
            get_epg_datetime(end_time),
            ""
        )
        programs.append(obj)

    return programs
