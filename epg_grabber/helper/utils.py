from datetime import datetime
from typing import Any, Mapping
from config.constants import EPG_XMLTV_TIMEFORMAT
from models.tvg import Channel
import os
import json


def get_epg_datetime(datetime: datetime, offset="+0000") -> str:
    """
    _summary_

    Args:
        datetime (datetime): _description_
        offset (str, optional): _description_. Defaults to "+0000".

    Returns:
        str: _description_
    """
    return datetime.strftime(EPG_XMLTV_TIMEFORMAT) + " " + offset


def load_channels_metadata(metadata_path: str) -> Mapping[str, Any]:
    """
    _summary_

    Args:
        metadata_path (str): _description_

    Returns:
        Mapping[str, Any]: _description_
    """
    f = open(metadata_path, "r")

    data = json.load(f)

    f.close()

    return data


def get_channel_by_name(tvg_id: str, site_name: str) -> Channel:
    """
    Retrieve the whole Channel object given its name and its site.

    If you don't want to hardcode the site_name parameter, use __file__
    as the site_name input.

    Eg:
        get_channel_by_name(channel_name, Path(__file__).stem)

    TODO: We could retrieve the caller filename and override the call in here.
        I never got it to work.

    Args:
        tvg_id (str): _description_
        site_name (str): _description_

    Returns:
        Channel: _description_
    """
    metadata_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "sites/channels_metadata")
    )
    metadata_path = metadata_dir + "/" + site_name + ".json"
    all_channels = load_channels_metadata(metadata_path)

    try:
        chan = next(
            channel
            for channel in all_channels
            if channel["tvg_id"].lower() == tvg_id.lower()
        )
    except Exception:
        raise ValueError("Channel metadata %s not found.", tvg_id)
    return Channel(
        id=chan["id"],
        tvg_id=chan["tvg_id"],
        tvg_name=chan["tvg_name"],
        tvg_logo=chan["tvg_logo"],
    )


def get_channelid_by_name(tvg_id: str, site_name: str) -> str:
    return get_channel_by_name(tvg_id, site_name).id
