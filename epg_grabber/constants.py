from pathlib import Path
# CLI
SHOW_INDENT = 2

XML_FILE_EXT = ".xml"

SITES_DIR = Path(__file__).parent/"sites"
CHANNELS_METADATA_DIR = SITES_DIR/"channels_metadata"

# importlib
SITES_MODULE_IMPORT_PATH = "epg_grabber.sites"

# EPG constants
EPG_GENERATOR = "epg_grabber"
EPG_XMLTV_TIMEFORMAT = "%Y%m%d%H%M%S %z" 
EPG_XMLTV_OFFSET = "+0000"
