import requests
from urllib.parse import quote

form_data = "activation_code=wwdwnkxev2"


def get_session() -> requests.Session:
    try:
        response = requests.post(
            "https://www.fetchtv.com.au/v3/authenticate",
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'},
            data=form_data)
    except Exception as e:
        raise(e)

    cookie = response.cookies
    raw_auth = "cookie=" + quote(cookie["auth"])

    try:
        session = requests.Session()
        session.post(
            "https://www.fetchtv.com.au/v2/subscriber/authenticate_with_cookie",
            headers={
                'content-type': 'application/x-www-form-urlencoded'},
            data=raw_auth)
    except Exception as e:
        raise(e)

    return session
