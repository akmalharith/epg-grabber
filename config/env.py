import os
from dotenv import load_dotenv

load_dotenv()

# For local developments, you can specify local.txt at the project dir
# without having to upload a text file on the internet
develop_mode = os.getenv("DEVELOP","false")
def develop():
    return develop_mode.lower() == "true"

# EPG configurations
epg_days = os.environ["EPG_DAYS"]
config_name = os.environ["CONFIG_NAME"]
config_url = os.environ["CONFIG_URL"]
tmp_epg_file = os.getenv("TMP_EPG_FILE", "tv.xml")

# sites/playtv_unifi_auth.py
playtv_unifi_user_id = os.environ["PLAYTV_UNIFI_USER_ID"]
playtv_unifi_password = os.environ["PLAYTV_UNIFI_PASSWORD"]
playtv_unifi_device_id = os.environ["PLAYTV_UNIFI_DEVICE_ID"]

# sites/thetennischannel.py 
thetennischannel_api_key = os.environ["THETENNISCHANNEL_API_KEY"]