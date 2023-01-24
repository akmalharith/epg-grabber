from epg_grabber.constants import SITES_DIR, CHANNELS_METADATA_DIR
from typing import List
import os


def get_sites() -> List[str]:
    sites = [f.removesuffix(".py") for f in os.listdir(SITES_DIR)
             if os.path.isfile(SITES_DIR/f)
             if not f.startswith("__")
             ]

    return sites
