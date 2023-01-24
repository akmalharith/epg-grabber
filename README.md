| This is the v0.4.0 release and it is not backwards compatible. v0.3.0 can still be accessed from Docker hub via `akmal/epg-grabber:v0.3.0`. Docker image will no longer be supported for now.|
|---|

# epg-grabber

Yet another EPG scraper built in Python. This is another Internet-based scraper and it does provide a very rich EPG data set for some supported sites.

## Installation
``` bash
pip install git+https://github.com/akmalharith/epg-grabber.git@v0.4.0
```

## Usage

The epg-grabber now comes with a CLI to help you run your scraping jobs.

Run `py-epg-cli --help` for options and help.
``` bash
$ py-epg-cli --help                                          
usage: py-epg-cli [-h] [--show] {local} ...

epg-grabber. Built in Python, this is another Internet-based scraper and it provides a very rich EPG data set for some supported sites.

optional arguments:
  -h, --help  show this help message and exit
  --show      List all supported sites.

mode:
  {local}
```
Run `py-epg-cli local` to scrape EPG. Pass `--help` for full options and help.
``` bash 
$ py-epg-cli local --help
usage: py-epg-cli local [-h] -f FILE -o OUTPUT [-d DAYS] [-w WORKERS]

Run EPG grabbing locally by suppling an input config file.

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  File of the EPG config
  -o OUTPUT, --output OUTPUT
                        XMLTV EPG file output
  -d DAYS, --days DAYS  No of days. Defaults to 1. Setting no. of days here will override the one in your input configuration file.
  -w WORKERS, --workers WORKERS
                        No of workers for parallelism. Defaults to 1.
```
Run `py-epg-cli`, to check the list of supported sites, 
``` bash
$ py-epg-cli --show 
To view channel metadata for a site, pass --show {site}.
        astro_com_my
        mewatch_sg
        rtmklik_rtm_gov_my
        visionplus_id
        tonton_com_my
        epgsky_com
        cinemaworld_asia
```
To see the channels and channel metadata, pass the site name in the `--show` command.
``` bash 
$ py-epg-cli --show astro_com_my 
{
  "channels": [
    {
      "id": "395",
      "display_name": {
        "@lang": "en",
        "#text": "TV1 HD"
      }
    },
    ...
    ...
  ]
}
```
Since the output is JSON, you can save it for further examination.
```
$ py-epg-cli --show astro_com_my > astro_com_my.json
```

## Example

`input.json` is a JSON file that contains a list of supported site configs and the site channels.
```
$ cat input.json
{
    "configs": [
        {
            "site": "astro_com_my",
            "channels": [
                "395"
            ]
        }
    ]
}
```
Running `py-epg-cli`:
``` bash
$ py-epg-cli local --file input.json --output tv.xml
2023-01-23 21:28:53.523 | INFO     | epg_grabber.app:run:77 - Starting epg-grabber...
2023-01-23 21:28:53.565 | INFO     | epg_grabber.app:_run_by_config_item:33 - Grabbing programs for 395.astro_com_my...
2023-01-23 21:28:54.567 | INFO     | epg_grabber.app:_run_by_config_item:62 - Completed for 395.astro_com_my! Found 40 programmes.
2023-01-23 21:28:54.575 | INFO     | epg_grabber.app:save_to_file:130 - XMLTV file tv.xml generated.
```
You can parallelize the scraping by sites by passing `--workers` to `py-epg-cli`. Defaults to `1`.

## Contributing

If you have a suggestion that would make this better like adding support for a new site or enriching the data, please fork the repo and create a PR. Be sure to read the guides in `CONTRIBUTING.md` to understand the project structure.
