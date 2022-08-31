from typing import List
from datetime import datetime, timedelta
from models.tvg import Channel, Program
from helper.utils import get_channel_by_name, get_epg_datetime
from pathlib import Path
import requests
import itertools

TIMEZONE_OFFSET = "+0800"
ALL_CHANNELS_URL = "https://contenthub-api.eco.astro.com.my/channel/all.json"
PROGRAM_URL = "https://contenthub-api.eco.astro.com.my/channel/{channel_id}.json"
PROGRAM_DETAIL_URL = "https://contenthub-api.eco.astro.com.my/api/v1/linear-detail?siTrafficKey={si_traffic_key}"


def get_all_channels() -> List[Channel]:
    try:
        r = requests.get(ALL_CHANNELS_URL)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    output = r.json()

    if r.status_code != 200:
        raise Exception(r.raise_for_status())
    if output["responseCode"] != 200:
        raise Exception(output["responseMessage"])

    channel_jsons = output["response"]

    channels = [
        Channel(
            id=channel["id"],
            tvg_id=channel["title"] + ".My",
            tvg_name=channel["title"],
            tvg_logo=channel["imageUrl"],
        )
        for channel in channel_jsons
    ]

    return channels


def get_program_details(traffic_key: str) -> str:
    program_detail_url = f"https://contenthub-api.eco.astro.com.my/api/v1/linear-detail?siTrafficKey={traffic_key}"
    print(program_detail_url)

    try:
        response = requests.get(program_detail_url)
    except Exception as e:
        raise e

    output = response.json()["response"]
    return output["shortSynopsis"]


def get_programs_by_channel(channel_name: str, days: int = 1) -> List[Program]:
    days = 7 if days > 7 else days

    channel = get_channel_by_name(channel_name, Path(__file__).stem)

    channel_url = PROGRAM_URL.format(channel_id=channel.id)

    try:
        r = requests.get(channel_url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    if r.status_code != 200:
        return

    output = r.json()

    schedules_filtered = dict(
        itertools.islice(output["response"]["schedule"].items(), days)
    )
    values = schedules_filtered.values()

    schedules = []

    for v in values:
        schedules.extend(v)

    programs = []

    for schedule in schedules:
        try:
            start_time = datetime.strptime(schedule["datetime"], "%Y-%m-%d %H:%M:%S.%f")
            hour, min, sec = schedule["duration"].split(":")
            dur = int(sec) + (int(min) * 60) + (int(hour) * 3600)
            end_time = start_time + timedelta(
                hours=int(hour), minutes=int(min), seconds=int(sec)
            )
            title = schedule["title"]
            # get_program_details API is massively slow
            # disable it for now
            # short_synopsis = get_program_details(schedule["siTrafficKey"])
        except KeyError:
            continue

        program_inner = Program(
            channel_name=channel.tvg_id,
            title=title,
            description="",
            start=get_epg_datetime(start_time, TIMEZONE_OFFSET),
            stop=get_epg_datetime(end_time, TIMEZONE_OFFSET),
        )

        programs.append(program_inner)

    return programs
