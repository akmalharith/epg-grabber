# epg-grabber

![Docker Pulls](https://img.shields.io/docker/pulls/akmal/epg-grabber) ![GitHub Workflow Status](https://github.com/akmalharith/epg-grabber/workflows/Pipeline/badge.svg)

Yet another EPG scraper built in Python. This is another Internet-based scraper and it does provide a very rich EPG data set for some supported sites.

## Usage

1. Run the job with the following parameters.
```
docker run \
-e CONFIG_NAME=config_name \
-e CONFIG_URL=https://googa.host/file.txt \
-e EPG_DAYS=7 \
akmal/epg-grabber:latest
```
- `CONFIG_NAME` - name of your configuration
- `CONFIG_URL` - direct link to your configuration text file
- `EPG_DAYS` - no of days you want to scrape, maximum is 7 days
- `TMP_EPG_FILE` - file name of your XMLTV EPG file, `tv.xml` is the default

Some sites supported in this image have environment variables for authentication purposes. See `/config/env.py` for environment variables that needs to be supplied for those sites.

2. The XMLTV file is saved in the container and you will need to copy it out once you are done.
```
docker cp $container_id:/app/tv.xml tv.xml
```

## Examples

Below is the example configuration file [config_march_2022.txt](https://gist.githubusercontent.com/akmalharith/ceda6103157c06cab5231c3a0f121cd2/raw/config_march_2022.txt) hosted in GitHub Gist:
```txt
mewatch;Channel5.Sg
mewatch;Channel8.Sg
mewatch;ChannelU.Sg
```

Full list of available channels configuration is in `sites/channels_config/` directory.

Here is how you would run it
```sh
docker run \
-e CONFIG_NAME=config_example \
-e CONFIG_URL=https://gist.githubusercontent.com/akmalharith/ceda6103157c06cab5231c3a0f121cd2/raw/config_march_2022.txt \
-e EPG_DAYS=7 \
akmal/epg-grabber:latest
```

## Contributing

If you have a suggestion that would make this better like adding support for a new site or enriching the data, please fork the repo and create a pull request. Be sure to read the guides in CONTRIBUTING.md to understand the project structure.
