from epg_grabber.models import (
    Programme,
    Channel,
    ChannelMetadata,
    InputConfig,
    InputConfigItem,
    TvData
)
from epg_grabber.constants import XML_FILE_EXT, CHANNELS_METADATA_DIR, SITES_MODULE_IMPORT_PATH
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from xmltodict import unparse
from importlib import import_module
from typing import Tuple, List
from loguru import logger


def _run_by_config_item(config: InputConfigItem, days: int) -> Tuple[List[Programme], List[Channel]]:

    programmes: List[Programme] = []
    channels: List[Channel] = []

    try:
        site = import_module(f"{SITES_MODULE_IMPORT_PATH}.{config.site}")
    except ModuleNotFoundError as e:
        logger.error(f"Site {config.site} doesn't exist. Skipping.")
        return

    for channel_id in config.channels:
        append_channel_id = (f"{channel_id}.{config.site}").lower()

        logger.info(f"Grabbing programs for {append_channel_id}...")

        ch_metadata_path = CHANNELS_METADATA_DIR/f"{config.site}.json"
        ch_metadata = ChannelMetadata.parse_file(ch_metadata_path)

        valid_channel = [
            valid_ch
            for valid_ch in ch_metadata.channels
            if valid_ch.id == channel_id
        ]

        if valid_channel:
            valid_channel[0].id = append_channel_id
            channels.append(valid_channel[0])
        else:
            logger.error(
                f"Channel {append_channel_id} doesn't exist in channel metadata. Skipping.")
            continue

        try:
            programmes_inner = site.get_programs(
                channel_id=channel_id,
                days=days,
                channel_xml_id=append_channel_id,
            )
        except Exception as e:
            logger.error(
                f"Error get_programs() at {append_channel_id}. {e}. Programmes will not be returned.")
            continue

        programmes.extend(programmes_inner)
        logger.info(
            f"Completed for {append_channel_id}! Found {len(programmes_inner)} programmes.")

    return programmes, channels


def run(input_config: InputConfig) -> Tuple[List[Programme], List[Channel]]:
    """
    Performs the scraping by executing get_programs() under the supported site.

    Args:
        input_config (InputConfig)

    Returns:
        Tuple[Programmes, Channels]: List of programmes, List of channels
    """
    logger.info("Starting epg-grabber...")

    programmes: List[Programme] = []
    channels: List[Channel] = []

    executor = ThreadPoolExecutor(max_workers=input_config.workers)

    for prog, chan in executor.map(
            _run_by_config_item, input_config.configs, repeat(input_config.days)):
        programmes.extend(prog)
        channels.extend(chan)

    return programmes, channels


def save_to_file(tv_data: TvData, filename: str):
    """
    Saves TV data to an XML file.

    Args:
        tv_data (TvData)
        filename (str)
    """
    if not filename.endswith(XML_FILE_EXT):
        filename += XML_FILE_EXT

    xml_dict = tv_data.dict(by_alias=True)
    xml_string = unparse(xml_dict, pretty=True, short_empty_elements=True)

    with open(filename, "w") as output_file:
        output_file.write(xml_string)
        output_file.close()

    logger.info(f"XMLTV file {filename} generated.")
