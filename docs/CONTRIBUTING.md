## Structure
The structure of the project is as below
```sh
epg_grabber
├── config
├── helper
└── sites
    ├── auth
    ├── channels_config
    ├── channels_metadata
    └── {site}.py
```

### `auth/`

This is a directory that contains helper for authentication or session related methods. If the site needs authentication, pass the necessary credentials via environment variables. Environment variables can be added in `config/env.py`.

### `channels_config/`

This is the full list of all sites and its channels. It is generated as below, with site and tvg-id joined with a semicolon separator. You can copy the entry here into your configuration file if you wish to scrape that channel data.
```txt
site;tvg-id
```
This is automatically generated during a new version build, or you can force it by running `python generate.py` at the root folder.


### `channels_metadata/`

Metadata for a given channel that is used during the scraping. This is so we reduce calls to the host for these informations everytime we scrape a particular site.
```json
[{
    "id": "97098",
    "tvg_id": "Channel5.Sg",
    "tvg_name": "Channel 5",
    "tvg_logo": ""
}]
```
This is automatically generated during a new version build, or you can force it by running `python generate.py` at the root folder.


### `site.py`

The following are the mandatory methods, declared as the convention of a `site.py` module that is the brain of the scraping for a given site.

1. `get_all_channels()`

This is where we retrieve all channel information for a given site. A single channel is parsed into the Channel class and all channels are appended into a list
```py

def get_all_channels() -> List[Channel]:
    """Retrieves all available channels for scraping

    Returns:
        list[Channel]: List of channels that was scraped
    """
```

2. `get_programs_by_channel(channel_name)`

Where all the programs for that channel in that `site.py` is scraped. A single program is parsed into Program class and all programs are appended into a list.
```py
def get_programs_by_channel(channel_name: str, *args) -> List[Program]:
    """The main function that does the scraping given the channel_name

    Args:
        channel_name (String): Channel name

    Returns:
        list[Programs]: List of programs that was scraped
    """
```
