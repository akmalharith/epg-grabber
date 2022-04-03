from typing import List
import requests
from pathlib import Path
from datetime import datetime, timedelta
from helper.utils import get_channel_by_name, get_epg_datetime
from helper.classes import Channel, Program
from sites.auth.fetchtv_auth import get_session

ALL_CHANNELS_URL = "https://www.fetchtv.com.au/v4/epg/channels"
CHANNEL_IMAGE_URL = "https://www.fetchtv.com.au/v2/epg/channels/{channel_id}/image"
programlist_url = "https://www.fetchtv.com.au/v2/epg/programslist?channel_ids="
PROGRAM_URL = "https://www.fetchtv.com.au/v2/epg/programslist?channel_ids={channel_id}&block=24-{date_seconds}"

session = get_session()


def get_all_channels() -> List[Channel]:
    try:
        response = session.get(ALL_CHANNELS_URL)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    output = response.json()

    channels_data = [channel[1] for channel in output["channels"].items()]

    channels = [Channel(
        channel["channel_id"],
        channel["name"] + ".Au",
        channel["name"],
        CHANNEL_IMAGE_URL.format(channel_id=channel["channel_id"]),
        True) for channel in channels_data]

    return channels


def get_programs_by_channel(channel_name: str, *args) -> List[Program]:
    days = args[0] if args else 1

    channel = get_channel_by_name(channel_name, Path(__file__).stem)

    today = datetime.utcnow()
    programs = []

    for i in range(days):
        diff = timedelta(days=i)
        date = today + diff
        date_seconds = str((date - datetime(1970, 1, 1)).days)
        url = PROGRAM_URL.format(
            channel_id=channel.id,
            date_seconds=date_seconds)

        try:
            r = session.get(url)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        output = r.json()

        programs_items = list(output["channels"].items())
        synopsis = list(output["synopses"].items())

        for index, p in programs_items:
            for a in p:  # Iterate through the sublist
                title = a[1]
                program_id = str(a[4])  # Force str type

                start_time = datetime.utcfromtimestamp(int(a[2]) / 1000.0)
                end_time = datetime.utcfromtimestamp(int(a[3]) / 1000.0)

                for index, syno in synopsis:
                    if index == program_id:
                        description = syno

                obj = Program(
                    channel_name=channel.tvg_id,
                    title=title,
                    description=description,
                    start=get_epg_datetime(start_time),
                    stop=get_epg_datetime(end_time)
                )
                programs.append(obj)

    return programs
