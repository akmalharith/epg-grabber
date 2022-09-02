from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List
from helper.utils import get_channel_by_name, get_epg_datetime
from models.tvg import Program, Channel
import requests

X_PLEX_PROVIDER_VERSION = "5.1"

##############################
# Default request attributes #
##############################

request_session = requests.Session()

headers = dict()
headers["accept"] = "application/json"
headers["x-plex-provider-version"] = X_PLEX_PROVIDER_VERSION


def get_all_channels() -> List[Channel]:
    api_channels_url = "https://epg.provider.plex.tv/lineups/plex/channels"
    try:
        channel_response = request_session.get(url=api_channels_url, headers=headers)
    except Exception as e:
        raise e

    channels_raw = channel_response.json()["MediaContainer"]["Channel"]

    channels = [
        Channel(
            id=channel["gridKey"],
            tvg_id=f"{channel['slug']}.plex",
            tvg_name=channel["title"],
            tvg_logo=channel["thumb"],
        )
        for channel in channels_raw
    ]

    return channels


def get_programs_by_channel(channel_name: str, days: int = 1) -> List[Program]:
    channel = get_channel_by_name(channel_name, Path(__file__).stem)
    i = 0
    days = days if days <= 7 else 7
    programs = []

    while i < days:
        date_cur = date.today() + timedelta(days=i)
        epg_url = f"https://epg.provider.plex.tv/grid?channelGridKey={channel.id}&date={date_cur}"
        try:
            epg_response = request_session.get(url=epg_url, headers=headers)
        except Exception as e:
            raise e

        programs_raw = epg_response.json()["MediaContainer"]["Metadata"]
        i += 1

        programs.extend(
            [
                Program(
                    channel_name=channel_name,
                    title=program["title"],
                    description=program.get("summary", ""),
                    start=get_epg_datetime(
                        datetime.utcfromtimestamp(program["Media"][0]["beginsAt"])
                    ),
                    stop=get_epg_datetime(
                        datetime.utcfromtimestamp(program["Media"][0]["endsAt"])
                    ),
                )
                for program in programs_raw
            ]
        )

    return programs
