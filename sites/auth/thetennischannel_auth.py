import os
from dotenv import load_dotenv


def get_api_key():
    load_dotenv()

    return os.environ['THETENNISCHANNEL_API_KEY']
