import requests
import json
import os
from pathlib import Path
from datetime import date, timedelta, datetime
from pytz import timezone
from unicodedata import normalize
from bs4 import BeautifulSoup
from source.classes import Program, Channel
from source.utils import get_channel_by_name, get_epg_datetime
from config.env import starhubtvplus_app_session, starhubtvplus_app_key

temp_file = "starhubtvplus_all_programs_temp.json"
api_url = "https://api.starhubtvplus.com/"
image_url = "https://poster.starhubgo.com/Linear_channels2/{ch_id}_1920x1080_HTV.png"

normalize_format = "NFKD"
on_demand_suffix = "On Demand"

def get_all_channels():

    url = 'https://www.starhub.com/personal/tvplus/passes/channel-listing.html'

    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    soup = BeautifulSoup(r.text,features="html.parser")
    if r.status_code != 200:
        raise Exception(r.raise_for_status())

    channel_tables = soup.find_all("div", {"class": "free-form-table_v1 section"})

    channel_table_tags = []

    for table in channel_tables:
        channel_table_tags_inner = table.find_all("td")

        for tag in channel_table_tags_inner:
            if tag.has_attr("colspan"):
                channel_table_tags_inner.remove(tag)
        
        channel_table_tags.extend(channel_table_tags_inner)

    channel_tags_pair = [[normalize(normalize_format, channel_table_tags[i].text).
                            replace("\n","").strip(), 
                        normalize(normalize_format, channel_table_tags[i + 1].text).
                            replace("\n","").
                            replace(on_demand_suffix,"").strip()]
                            for i in range(len(channel_table_tags) - 1)
                                if not i % 2
                                if channel_table_tags[i + 1].text.lower() != "app"]
                            
    channels = []

    for tags_pair in channel_tags_pair:
        tup_id = tags_pair[1].lower().replace("ch ","").replace("via","").strip(),
        str_id = ''.join(tup_id)

        ch_obj = Channel(
            id = str_id,
            tvg_id = tags_pair[0]+".Sg",
            tvg_name = tags_pair[0],
            tvg_logo = image_url.format(ch_id=str_id),
            sanitize=True
        )

        channels.append(ch_obj)

    return channels

def _get_programs(date_from, date_to):
    if os.path.isfile(temp_file):
        file_data = open(temp_file, "r")
        temp_data = json.load(file_data)
        return temp_data
    
    get_programs_query = """query webFilteredEpg($category: String, $dateFrom: DateWithoutTime, $dateTo: DateWithoutTime!) {
nagraEpg(category: $category) {
    items {
    channelId: tvChannel
    id
    image
    isIptvMulticast
    isOttUnicast
    title: description
    programs: programsByDate(dateFrom: $dateFrom, dateTo: $dateTo) {
        channel {
        isIptvMulticast
        isOttUnicast
        __typename
        }
        endTime
        id
        startOverSupport
        startTime
        title
        __typename
    }
    __typename
    }
    __typename
}
}
"""
    headers = {
        "x-application-session": starhubtvplus_app_session,
        "x-application-key": starhubtvplus_app_key
    }

    programs_payload = {
        "operationName": "webFilteredEpg",
        "variables": {
            "id": "GLOBAL_58",
            "category": "",
            "dateFrom": date_from, 
            "dateTo": date_to
        },
        "query": get_programs_query
    }

    try:
        response = requests.post(api_url, headers=headers, json=programs_payload)
    except Exception as e:
        raise (e)
    if response.status_code != 200:
        raise Exception

    output = response.json()
    

    all_channels_program = output["data"]["nagraEpg"]["items"]
    
    with open(temp_file, "w") as infile:
        json.dump(all_channels_program, infile)
        infile.close()
    
    return all_channels_program


def _get_program_details(program_id):
    get_programs_details_query = """query webEpgDetails($id: String!) {
  details(id: $id) {
    description
    duration
    genres
    id
    image
    productRefs
    rating
    title
    products {
      pack {
        id
        productId
        purchasableUfinityProduct {
          productId
          __typename
        }
        __typename
      }
      __typename
    }
    ... on LinearInterface {
      endTime
      isCatchUpSupported
      startOverSupport
      startTime
      __typename
    }
    ... on NagraProgram {
      channel {
        image
        __typename
      }
      next {
        duration
        id
        rating
        title
        __typename
      }
      channel {
        id
        tvChannel
        catchUpSupport
        __typename
      }
      __typename
    }
    ... on NagraChannel {
      tvChannel
      nowPlaying {
        id
        next {
          duration
          id
          rating
          title
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
}
"""

    program_details_payload = {
        "operationName": "webEpgDetails",
        "variables": {
            "id": program_id
        },
        "query": get_programs_details_query
    }

    headers = {
        "x-application-session": starhubtvplus_app_session,
        "x-application-key": starhubtvplus_app_key
    }
    try:
        response = requests.post(api_url, headers=headers, json=program_details_payload)
    except Exception as e:
        raise (e)
    if response.status_code != 200:
        raise Exception

    output = response.json()

    details = output["data"]["details"]

    if "description" in details:
        description = details["description"]
    
    if "genres" in details and len(details["genres"]) != 0:
        category = details["genres"][0] # Only get one genre for now

    if "rating" in details:
        rating = details["rating"] # <rating system="USA Parental Rating">

    return description, category, rating
        
def get_programs_by_channel(channel_name, *args):
    """_summary_

    Args:
        channel_name (_type_): _description_
    """
    days = args[0] if args else 1
    days = 7 if days > 7 else days

    date_from = date.today()
    date_to = date_from + timedelta(days = days)
    
    programs = _get_programs(str(date_from), str(date_to))
    
    channel = get_channel_by_name(channel_name, Path(__file__).stem)

    programs_channel = [programs_per_channel["programs"] for programs_per_channel in programs
                        if programs_per_channel["channelId"] == int(channel.id)][0]

    all_programs = []

    for programs_inner in programs_channel:
        try:
            description, category, rating = _get_program_details(programs_inner["id"])
        except Exception as e:
            return [Program()]

        start_timestamp = programs_inner["startTime"] / 1000
        start_program = datetime.fromtimestamp(start_timestamp, timezone("UTC"))

        end_timestamp = programs_inner["endTime"] / 1000
        end_program = datetime.fromtimestamp(end_timestamp, timezone("UTC"))

        program_object = Program(
            channel_name=channel_name,
            title=programs_inner["title"],
            description=description,
            start=get_epg_datetime(start_program),
            stop=get_epg_datetime(end_program),
            category=category,
            rating=rating
        )

        all_programs.append(program_object)

    return all_programs
