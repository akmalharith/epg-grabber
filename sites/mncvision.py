import requests
import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from source.classes import Channel, Program
from source.utils import get_channel_by_name, get_epg_datetime


WEBSITE_HOST = "https://mncvision.id/"
LANG_SWITCHER = "https://mncvision.id/language_switcher/setlang/english/"
TABLE_URL = "https://www.mncvision.id/schedule/table"
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
TIMEZONE_OFFSET = "+0700"

ALL_CHANNELS_URL = "https://mncvision.id/channel"

# Initiate a session and set Language to English
s = requests.Session()
s.get(LANG_SWITCHER)


def get_all_channels():
    url = ALL_CHANNELS_URL
    channels = []

    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    soup = BeautifulSoup(r.text, features="html.parser")

    channel_lineup = soup.find_all(
        "div", {"class": "col-xs-6 col-sm-4 col-md-3 col-lg-2 tm-col"})

    for channel in channel_lineup:
        ch_id = channel.find("span", {"class": "tm-channel-no"}).text
        ch_name_tag = channel.find("div", {"class": "tm-channel-name"})
        ch_name = " ".join(ch_name_tag.text.split()).replace(" ", "")
        ch_icon_url = WEBSITE_HOST + channel.find("img")["src"]

        obj = Channel(
            ch_id,
            ch_name + ".Id",
            ch_name,
            ch_icon_url
        )

        channels.append(obj)

    return channels


def get_program_details(prog_url):
    url = prog_url
    try:
        r = s.get(url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    soup = BeautifulSoup(r.text, features="html.parser")

    desc_tag = soup.find("blockquote", {"class": "bloquet synopsis"})
    description = " ".join(desc_tag.text.split())

    if description == "-":
        return ""

    return description


def get_soup(url, payload):
    url = TABLE_URL
    try:
        r = s.post(url, data=payload)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    soup = BeautifulSoup(r.text, features="html.parser")

    return soup


def get_next_page(url):
    try:
        r = s.get(url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    soup = BeautifulSoup(r.text, features="html.parser")

    return soup


def get_programs(program, channel_name, request_date):
    time = program.find_all("td", {"class": "text-center"})
    start = time[0].text
    duration = time[1].text

    title_tags = program.find("a")
    title = title_tags.text
    description_url = title_tags["href"]

    sample_date = request_date + " " + start

    # Get duration in seconds
    dur = duration.split(":")
    seconds = (int(dur[0]) * 3600) + (int(dur[1]) * 60)

    start_time = datetime.datetime.strptime(sample_date, DATETIME_FORMAT)
    end_time = start_time + datetime.timedelta(seconds=seconds)

    channel = get_channel_by_name(channel_name, Path(__file__).stem)

    obj = Program(
        channel.tvg_id,
        title,
        get_program_details(description_url),
        get_epg_datetime(start_time, TIMEZONE_OFFSET),
        get_epg_datetime(end_time, TIMEZONE_OFFSET),
        "")

    return obj


def get_programs_by_channel(channel_name, *args):
    days = args[0] if args else 1
    days = 7 if days > 7 else days

    today = datetime.datetime.today()
    channel = get_channel_by_name(channel_name, Path(__file__).stem)
    programs = []

    for day in range(days):
        new_day = today + datetime.timedelta(days=day)
        request_date = new_day.strftime(DATE_FORMAT)

        payload = {
            "search_model": "channel",
            "af0rmelement": "aformelement",
            "fdate": request_date,
            "fchannel": channel.id,
            "submit": "Cari"
        }

        page_url = []

        i = 0

        soup = get_soup(TABLE_URL, payload)
        pages = soup.find("div", {"class": "box well"})

        if pages:
            for p in pages.find_all("a", href=True):
                if p["href"] not in page_url:
                    page_url.append(p["href"])

        souped = soup.find_all("tr", {"valign": "top"})

        for program in souped:
            obj = get_programs(program, channel_name, request_date)
            programs.append(obj)

        while i < len(page_url):
            url_z = page_url[i]

            soup = get_next_page(url_z)
            souped = soup.find_all("tr", {"valign": "top"})

            for program in souped:
                obj = get_programs(program, channel_name, request_date)
                programs.append(obj)

            i += 1

    return programs
