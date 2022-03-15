import requests
from datetime import date, datetime, timedelta
from common.classes import Channel, Program
from common.utils import get_epg_time
from sites.auth.thetennischannel_auth import get_api_key

api_key = get_api_key()

DATETIME_FORMAT = "%Y-%m-%dT%H:%MZ"


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

    url = "http://data.tmsapi.com/v1.1/stations/33395/airings?api_key={apikey}&startDateTime={start}&endDateTime={end}".format(
        start=date_today, end=end_date, apikey=api_key)

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
            channel_name,
            program['program']['title'],
            "",
            get_epg_time(start_time),
            get_epg_time(end_time),
            ""
        )
        programs.append(obj)

    return programs
