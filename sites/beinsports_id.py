import requests
from datetime import date, datetime
from bs4 import BeautifulSoup
from common.classes import Channel, Program
from common.utils import get_channelid_by_name, get_channel_by_name, get_epg_time

TIMEZONE_OFFSET = "+0800"
PROGRAM_URL = "https://epg.beinsports.com/utctime_id.php?cdate={date}&offset=+8&mins=00&category=sports&id=123"


def get_all_channels():
    return [Channel(
        "channels_1",
        "beInSPORTS1.Id",
        "beIN SPORTS 1",
        ""),
        Channel(
        "channels_2",
        "beInSPORTS2.Id",
            "beIN SPORTS 2",
            "")]


def get_programs_by_channel(channel_name, *args):
    # TODO: Accept days as input and increment the date_input in an outer for loop
    date_input = date.today()
    datetime_today = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0)

    url = PROGRAM_URL.format(
        date=date_input)

    channel_id = get_channelid_by_name(channel_name, "beinsports_id")

    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    soup = BeautifulSoup(r.text, features="html.parser")
    divs = soup.find_all("div", {"id": channel_id})

    programs = []
    for div in divs:
        line = div.find_all("li", {"parent": "slider_1"})
        for value in line:
            time_period = str(value.find("p", {"class": "time"}).string)
            time_start, time_end = time_period.split("-")
            print(time_start)

            start_hour, start_minute = time_start.split(":")
            start_time = datetime_today.replace(
                hour=int(start_hour), minute=int(start_minute))

            end_hour, end_minute = time_end.split(":")
            end_time = datetime_today.replace(
                hour=int(end_hour), minute=int(end_minute))

            obj = Program(
                get_channel_by_name(channel_name, "beinsports_id").name,
                value.find("p", {"class": "title"}).string,
                value.find("p", {"class": "format"}).string,
                get_epg_time(start_time, TIMEZONE_OFFSET),
                get_epg_time(end_time, TIMEZONE_OFFSET),
                ""
            )
            programs.append(obj)
    return programs
