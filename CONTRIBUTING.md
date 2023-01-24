## Contributing ## 

Thanks to Pydantic it's super easy to make this tool extendable and clean.

### Development environment ###

Always use virtual environment for development.
```
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install .
```

### Add new site ###

1. Place your site file in `sites` dir. 
``` bash
sites
├── ...
├── ...
├── ...
└── new_site.py
```
2. Write the following mandatory functions with exact names, take note of type hints and make sure to return using the right models.

``` python
# new_site.py 
from epg_grabber.models import Programme, Channel, ChannelMetadata

def generate() -> ChannelMetadata:
    ...
    channels: ChannelMetadata = ...
    return channels

def get_programs(channel_id: str, days: int = 1, channel_xml_id: str = None) -> List[Programme]:
    ...
    programmes: List[Programme] = ...
    return programs
```
3. Generate channel metadata. 
``` bash
cd scripts 
python generate --site new_site
```
If your site works it will add a JSON file under `sites/channel_metadata` as part of the package.
``` bash
sites
├── channel_metadata
│   ├── ...
│   ├── ...
│   └── new_site.json
├── ...
├── ...
└── new_site.py
```

### Tests

Tests are very early and lacking, since Pydantic's validators are really powerful. It is advised that you add a test case in`tests/test_get_program.py`, with the site name and a channel ID. (We will dynamicize the configs in the future.)

``` python
# test_get_program.py 

site_test_config = {
    "configs": [
        {
            "site": "new_site",
            "channels": ["395"],
        },
        ...
    ]
}
```
To run the test
``` bash
$ python -m pytest
============================= test session starts ==============================
platform darwin -- Python 3.9.13, pytest-7.2.1, pluggy-1.0.0
rootdir: /Users/johndoe/Code/epg-grabber
collected 7 items

tests/test_get_program.py .......                                        [100%]

============================== 7 passed in 7.21s ===============================
```