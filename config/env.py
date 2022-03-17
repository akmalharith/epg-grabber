import os
from dotenv import load_dotenv

load_dotenv()

# For local developments, you can specify local.txt at the project dir
# without having to upload a text file on the internet
develop_mode = os.getenv("DEVELOP", "false")


def develop():
    return develop_mode.lower() == "true"


# EPG configurations
epg_days = os.getenv("EPG_DAYS")
config_name = os.getenv("CONFIG_NAME")
config_url = os.getenv("CONFIG_URL")
tmp_epg_file = os.getenv("TMP_EPG_FILE", "tv.xml")

# sites/playtv_unifi_auth.py
playtv_unifi_user_id = os.getenv("PLAYTV_UNIFI_USER_ID")
playtv_unifi_password = os.getenv("PLAYTV_UNIFI_PASSWORD")
playtv_unifi_device_id = os.getenv("PLAYTV_UNIFI_DEVICE_ID")

# sites/thetennischannel.py
thetennischannel_api_key = os.getenv("THETENNISCHANNEL_API_KEY")
