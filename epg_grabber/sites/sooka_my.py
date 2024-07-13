from epg_grabber.models import Programme, ChannelMetadata, Channel

from datetime import date, datetime, timedelta
from pytz import timezone
from tzlocal import get_localzone_name
import requests

KALSIG = "1c9a9da646d991758f659424dccec62f"

LOGIN_URL = "https://app-kaltura-proxy.sooka.my/prod/api/v1/api_v3/service/ottuser/action/anonymousLogin"
LIST_URL = "https://app-kaltura-proxy.sooka.my/prod/api/v1/api_v3/service/asset/action/list"
DEFAULT_HEADERS = {
    "authority": "app-kaltura-proxy.sooka.my",
    "origin": "https://sooka.my",
    "referer": "https://sooka.my/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    'content-type': 'application/json'
}

def login() -> dict:

  try: 
    response = requests.post(LOGIN_URL, json={
        "partnerId": "3209",
        "udid": "WEB-6764bc29-d82d-3f3b-f9ac-bc0613757dca",
        "format": 1,
        "clientTag": "AstroQA",
        "apiVersion": "6.1.0.28839",
        "language": "en",
        "kalsig": KALSIG,
    }, 
    headers=DEFAULT_HEADERS)
  except Exception as e:
    raise e

  output = response.json()
  ks = output["result"]["ks"]
 
  return {
    'ks': ks,
    'kalsig': KALSIG
  }

session = login()

def generate() -> ChannelMetadata:
   
    try:
        response = requests.post(LIST_URL, json={
           "filter": {
                "objectType": "KalturaChannelFilter",
                "idEqual": "339523",
                "kSql": "(or (and asset_type = 'epg' ) (and Catalogue = 'sottott') )"
           },
            "pager": {
                "objectType": "KalturaFilterPager",
                "pageIndex": 1,
                "pageSize": 80
            },
            "format": 1,
            "clientTag": "AstroQA",
            "apiVersion": "6.1.0.28839",
            "language":"en",
            "ks": session.get('ks'),
            "kalsig": session.get('kalsig')
        },
        headers=DEFAULT_HEADERS
    )
    except Exception as e:
        raise e
    
    output = response.json()
    objects = output['result']['objects']

    channels = []

    for obj in objects:
       channel_obj = Channel(
          id=obj['externalIds'],
          display_name=obj['name'],
          icon=obj['images'][0]['url'],
       )

       channels.append(channel_obj)
    
    return ChannelMetadata(channels=channels)

def get_programs(channel_id: str, days: int = 1, channel_xml_id: str = None):

    channel_name = channel_xml_id if channel_xml_id else channel_id

    start_dt = date.today()   
    start_date = datetime.combine(start_dt, datetime.min.time())

    end_dt = start_dt + timedelta(days=days)
    end_date = datetime.combine(end_dt, datetime.max.time())

    # The KSQL is buggy, it expected end_date input for a start_date and the other way around
    end_timestamp = str(int(start_date.timestamp()))
    start_timestamp = str(int(end_date.timestamp()))

    epg_ksql = f"(and epg_channel_id = \'{channel_id}\' end_date>=\'{end_timestamp}\' start_date<\'{start_timestamp}\')"

    try:
        response = requests.post(LIST_URL, json={
           "filter": {
                "objectType": "KalturaSearchAssetFilter",
                "orderBy": "START_DATE_ASC",
                "kSql": epg_ksql
           },
            "pager": {
                "objectType": "KalturaFilterPager",
                "pageIndex": 1,
                "pageSize": 50
            },
            "format": 1,
            "clientTag": "AstroQA",
            "apiVersion": "6.1.0.28839",
            "language":"en",
            "ks": session.get('ks'),
            "kalsig": session.get('kalsig')
        },
        headers=DEFAULT_HEADERS
    )
    except Exception as e:
        raise e

    output = response.json()

    programs = []

    # Get caller TzInfo
    tz = timezone(get_localzone_name())

    for obj in output['result']['objects']:
        title = obj['metas']['TitleSortName']['value']

        try:
            description = obj['metas']['LongSynopsis']['value']
        except KeyError:
            description = ""
        start_date = tz.localize(datetime.fromtimestamp(obj['startDate']))
        end_date = tz.localize(datetime.fromtimestamp(obj['endDate']))

        program_obj = Programme(
            start=start_date,
            stop=end_date,
            channel=channel_name,
            title=title,
            desc=description
        )

        programs.append(program_obj)
    
    return programs
