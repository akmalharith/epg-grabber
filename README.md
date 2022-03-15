# EPG Grabber

Yet another EPG scraper built in Python and actively maintained. This is another Internet-based scraper and it does provide a very rich EPG data set for some supported sites.

## Usage

1. Run the job with the following parameters
```
docker run akmal/epg-grabber \
-e CONFIG_NAME=config_name \
-e CONFIG_URL=https://googa.host/file.txt \
-e EPG_DAYS=7
```
- `CONFIG_NAME` - name of your configuration
- `CONFIG_URL` - direct link to your configuration text file
- `EPG_DAYS` - no of days you want to scrape, maximum is 7 days
- `TMP_EPG_FILE` - file name of your XMLTV EPG file, `tv.xml` is the default

Some sites supported in this image have mandatory environment variables. See here.

2. The XMLTV file is saved in the container and you will need to copy it out once you are done.
```
docker cp {container_id}:tv.xml tv.xml
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
docker run docker run akmal/epg-grabber \
-e CONFIG_NAME=config_example \
-e CONFIG_URL=https://gist.githubusercontent.com/akmalharith/ceda6103157c06cab5231c3a0f121cd2/raw/config_march_2022.txt \
-e EPG_DAYS=7
```

## Contributing

If you have a suggestion that would make this better like adding support for a new site, please fork the repo and create a pull request. Be sure to read the guides in CONTRIBUTING.md to understand the project structure.
