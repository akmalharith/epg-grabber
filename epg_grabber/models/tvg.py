from pydantic import BaseModel, validator
from string import punctuation

# Details of a single programme transmission.


class Program(BaseModel):
    channel_name: str
    title: str
    description: str
    start: str
    stop: str
    # Although below are optional we need to set blank default value
    # for program_to_xml() to work
    episode: str = ""
    category: str = ""
    rating: str = ""


class Channel(BaseModel):
    id: str
    tvg_id: str
    tvg_name: str
    tvg_logo: str

    @validator("tvg_id", pre=True)
    def tvg_id_sanitize(cls, v):
        """Sanitize the characters in tvg_id, except a period"""
        if isinstance(v, str):
            v = [v.replace(char, "") for char in punctuation if char != "."][0].replace(
                " ", ""
            )

        return v
