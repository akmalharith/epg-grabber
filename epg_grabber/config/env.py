import os
from dotenv import load_dotenv

load_dotenv()

# For local developments, you can specify local.txt at the project dir
# without having to upload a text file on the internet
develop_mode = os.getenv("DEVELOP", "false")

tests_mode = os.getenv("TESTS", "false")


def develop() -> bool:
    return develop_mode.lower() == "true"


def tests() -> bool:
    return tests_mode.lower() == "true"


# EPG configurations
epg_days = os.getenv("EPG_DAYS", "1")
config_name = os.getenv("CONFIG_NAME")
config_url = os.getenv("CONFIG_URL")
tmp_epg_file = os.getenv("TMP_EPG_FILE", "tv.xml")

# sites/playtv_unifi_auth.py
playtv_unifi_user_id = os.getenv("PLAYTV_UNIFI_USER_ID")
playtv_unifi_password = os.getenv("PLAYTV_UNIFI_PASSWORD")
playtv_unifi_device_id = os.getenv("PLAYTV_UNIFI_DEVICE_ID")

# sites/starhubtvplus.py
starhubtvplus_client_uuid = os.getenv("STARHUBTVPLUS_CLIENT_UUID")
starhubtvplus_app_key = os.getenv("STARHUBTVPLUS_APP_KEY")
