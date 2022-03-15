"""
Source website: https://content.astro.com.my/
"""
import re
import requests
from datetime import datetime, timedelta
from common.classes import Channel, Program
from common.utils import get_channelid_by_name, get_epg_time

TIMEZONE_OFFSET = "+0800"
ALL_CHANNELS_URL = "https://contenthub-api.eco.astro.com.my/channel/all.json"
PROGRAM_URL = "https://contenthub-api.eco.astro.com.my/channel/{channel_id}.json"
PROGRAM_DETAIL_URL = "https://contenthub-api.eco.astro.com.my/api/v1/linear-detail?siTrafficKey={si_traffic_key}"


def get_all_channels():
    """Retrieves all available channels for scraping

    Returns:
        list[Channel]: List of channels that was scraped
    """
    query_url = ALL_CHANNELS_URL

    try:
        r = requests.get(query_url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    output = r.json()

    if r.status_code != 200:
        raise Exception(r.raise_for_status())
    if output["responseCode"] != 200:
        raise Exception(output["responseMessage"])

    channel_jsons = output["response"]

    channels = [Channel(channel["id"], channel["title"]+".My", channel["title"],
                        channel["imageUrl"]) for channel in channel_jsons]

    return channels


def get_program_details(traffic_key):
    program_detail_url = PROGRAM_DETAIL_URL.format(si_traffic_key=traffic_key)

    try:
        r = requests.get(program_detail_url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    if r.status_code != 200:
        return "", ""

    output = r.json()["response"]

    return get_clean_title(str(output["title"])), str(output["shortSynopsis"])


def get_episode_onscreen(title):
    try:
        season = re.search(r"[s]\d", title, re.IGNORECASE).group().upper()
        episode = re.search(r"Ep\d{2,5}", title, re.IGNORECASE).group().upper()
        onscreen = season + " " + episode
        return onscreen

    except AttributeError:
        return ""  # We need to leave <episode> tag blank


def get_clean_title(title):
    cleanup_ = re.sub(r"S\d{1,3}", "", title, re.IGNORECASE)
    cleanup = re.sub(r"Ep\d{2,5}", "", cleanup_, re.IGNORECASE)

    return cleanup.strip()


def get_programs_by_channel(channel_name, *args):
    """The main function that does the scraping given the channel_name

    Args:
        channel_name (String): Channel name

    Returns:
        list[Programs]: List of programs that was scraped
    """
    days = args[0] if args else 1
    days = 7 if days > 7 else days

    channel_url = PROGRAM_URL.format(
        channel_id=get_channelid_by_name(channel_name, "astro"))
    

    try:
        r = requests.get(channel_url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    if r.status_code != 200:
        return [Program()]

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
                start_time = datetime.strptime(
                    p["datetime"], "%Y-%m-%d %H:%M:%S.%f")
                hour, min, sec = p["duration"].split(":")
                dur = int(sec) + (int(min) * 60) + (int(hour) * 3600)
                end_time = start_time + timedelta(seconds=dur)
                title, short_synopsis = get_program_details(p["siTrafficKey"])

                obj = Program(
                    channel_name,
                    title,
                    short_synopsis,
                    get_epg_time(start_time, TIMEZONE_OFFSET),
                    get_epg_time(end_time, TIMEZONE_OFFSET),
                    get_episode_onscreen(title)
                )
            except KeyError:
                continue
            programs.append(obj)

    return programs
