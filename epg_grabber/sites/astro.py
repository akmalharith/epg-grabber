from typing import List
from datetime import datetime, timedelta
from models.tvg import Channel, Program
from helper.utils import get_channel_by_name, get_epg_datetime
from pathlib import Path
import re
import requests

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
    program_detail_url = PROGRAM_DETAIL_URL.format(si_traffic_key=traffic_key)

    try:
        r = requests.get(program_detail_url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    if r.status_code != 200:
        return "", ""

    output = r.json()["response"]

    return get_clean_title(str(output["title"])), str(output["shortSynopsis"])


def get_episode_onscreen(title: str) -> str:
    try:
        season = re.search(r"[s]\d", title, re.IGNORECASE).group().upper()
        episode = re.search(r"Ep\d{2,5}", title, re.IGNORECASE).group().upper()
        onscreen = season + " " + episode
        return onscreen

    except AttributeError:
        return ""  # We need to leave <episode> tag blank


def get_clean_title(title: str) -> str:
    cleanup_ = re.sub(r"S\d{1,3}", "", title, re.IGNORECASE)
    cleanup = re.sub(r"Ep\d{2,5}", "", cleanup_, re.IGNORECASE)

    return cleanup.strip()


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

    program_json = output["response"]["schedule"]

    schedules = [schedule for schedule in program_json]

    if days > len(schedules):
        days = len(schedules)

    programs = []

    for i in range(days):
        program = program_json[schedules[i]]
        for p in program:
            try:
                start_time = datetime.strptime(p["datetime"], "%Y-%m-%d %H:%M:%S.%f")
                hour, min, sec = p["duration"].split(":")
                dur = int(sec) + (int(min) * 60) + (int(hour) * 3600)
                end_time = start_time + timedelta(seconds=dur)
                title, short_synopsis = get_program_details(p["siTrafficKey"])

                program_inner = Program(
                    channel_name=channel.tvg_id,
                    title=title,
                    description=short_synopsis,
                    start=get_epg_datetime(start_time, TIMEZONE_OFFSET),
                    stop=get_epg_datetime(end_time, TIMEZONE_OFFSET),
                    episode=get_episode_onscreen(title),
                )
            except KeyError:
                continue
            programs.append(program_inner)

    return programs
