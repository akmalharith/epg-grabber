import importlib
import os
import re
import sys
import time
import requests
import logging

from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple

# Environment variables
from config.constants import (
    CONFIG_REGEX,
    DEVELOP_FILE,
    TESTS_FILE,
    TITLE,
    EMPTY_CONFIG_ERROR_MESSAGE,
)
from config.env import config_name, config_url, develop, epg_days, tests, tmp_epg_file
from helper.epgwriter import EpgWriter
from helper.utils import get_channel_by_name
from models.tvg import Channel, Program

sys.tracebacklimit = 0
log = logging.getLogger(TITLE)
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=os.environ.get("LOGLEVEL", "INFO"),
    datefmt="%Y-%m-%d %H:%M:%S",
)


def load_config() -> List[str]:
    """
    _summary_

    Returns:
        List[str]: _description_
    """

    if tests():
        with open(TESTS_FILE, "r") as r:
            text_buffer = r.read()
    elif develop():
        with open(DEVELOP_FILE, "r") as r:
            text_buffer = r.read()
    else:
        try:
            r = requests.get(config_url)
            r.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            raise Exception(e)
        except requests.exceptions.RequestException as e:
            raise Exception(e)
        except Exception as e:
            raise Exception(e)
        text_buffer = r.text

    config_items = [
        config
        for config in text_buffer.splitlines()
        if config
        if re.match(CONFIG_REGEX, config)
        if not config.startswith("#")
    ]

    if not config_items:
        raise Exception(EMPTY_CONFIG_ERROR_MESSAGE.format(config_url=config_url))

    return config_items


def scrape_by_site(site_name: str, channel_name: str) -> Tuple[List[str], Channel]:
    """
    _summary_

    Args:
        site_name (str): _description_
        channel_name (str): _description_

    Returns:
        Tuple[List[str], Channel]: _description_
    """

    log.info("[%s] Start scrape_by_site from %s", channel_name, site_name)

    try:
        site = importlib.import_module("sites." + site_name)
    except Exception as e:
        log.error("Site unsupported! {}: {}".format(type(e).__name__, e))
        raise e

    try:
        programs_by_channel = site.get_programs_by_channel(
            channel_name=channel_name, days=int(epg_days)
        )
    except Exception as e:
        log.error("{}: {}".format(type(e).__name__, e))
        raise e

    try:
        channel = get_channel_by_name(channel_name, site_name)
    except Exception as e:
        log.error("{}: {}".format(type(e).__name__, e))
        raise e

    log.info("[%s] Total programs = %d", channel_name, len(programs_by_channel))
    log.info("[%s] Scraping completed.", channel_name)

    return programs_by_channel, channel


def scrape_single(config_item) -> Tuple[List[Program], List[Channel]]:
    site_name = config_item.split(";")[0]
    channel_name = config_item.split(";")[1].strip()

    try:
        programs_by_channel, channel = scrape_by_site(site_name, channel_name)
    except Exception:
        pass

    return programs_by_channel, channel


def scrape() -> Tuple[List[Program], List[Channel]]:
    """
    _summary_

    Returns:
        Tuple[List[Program], List[Channel]]: _description_
    """
    channels = []
    programs = []

    config_items = load_config()

    executor = ThreadPoolExecutor(max_workers=4)

    for programs_by_channel, channel_inner in executor.map(scrape_single, config_items):

        channels.append(channel_inner)
        programs.extend(programs_by_channel)

    return programs, channels


if __name__ == "__main__":

    start_time = time.time()
    log.info("START: Starting scraping for config %s ...", config_name)

    programs, channels = scrape()

    # Writing XMLTV format to a temporary file
    EpgWriter.save(file=tmp_epg_file, channels=channels, programs=programs)

    log.info("FINISH: Finished scraping.")
    print("--- %s seconds ---" % (time.time() - start_time))
    exit()
