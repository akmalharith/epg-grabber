import requests
from datetime import date, datetime, timedelta
from source.classes import Channel, Program
from source.utils import get_epg_datetime
from config.env import thetennischannel_api_key

DATETIME_FORMAT = "%Y-%m-%dT%H:%MZ"
PROGRAMS_URL = "http://data.tmsapi.com/v1.1/stations/33395/airings?api_key={apikey}&startDateTime={start}&endDateTime={end}"


def get_all_channels():  # Hardcode since we are only dealing with one channel
    return [Channel(
        "tennischannel",
        "tennischannel.Us",
        "Tennis Channel",
        "https://tch.spott2.sportradar.com/assets/img/Tennischannel/TC-logo-green.png"
    )]


def get_programs_by_channel(channel_name, *args):
    days = args[0] if args else 1
    days = 7 if days > 7 else days

    date_today = date.today()
    end_date = date_today + timedelta(days=days)

    url = PROGRAMS_URL.format(
        start=date_today,
        end=end_date,
        apikey=thetennischannel_api_key)

    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    output = r.json()
    programs = []

    for program in output:
        start_time = datetime.strptime(program["startTime"], DATETIME_FORMAT)
        end_time = datetime.strptime(program["endTime"], DATETIME_FORMAT)

        obj = Program(
            get_all_channels()[0].tvg_id,
            program['program']['title'],
            "",
            get_epg_datetime(start_time),
            get_epg_datetime(end_time),
            ""
        )
        programs.append(obj)

    return programs
