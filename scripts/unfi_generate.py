import requests

response = requests.get(
    "https://raw.githubusercontent.com/mediahomes/assets-private/main/playlist/unifi.m3u?token=GHSAT0AAAAAACORICT2RLT4SZYWJNLM2OTCZSR7ULQ"
)

playlist = response.text.splitlines()

channels = []

epg_config = []

for p in playlist:
    if 'EXTINF' in p:
        items = p.split(",")
        display_name = items[1]

        items = items[0].split(" ")

        for item in items:
            if 'tvg-id' in item:
                id = item.split("=")[1].replace('"',"").split(".")[0]

            if 'tvg-logo' in item:
                icon = item.split("=")[1].split(",")[0].replace('"',"")


        channels.append(
            {
            "id": id,
            "display_name": {
                "@lang": "en",
                "#text": display_name
            },
            "icon": {
                "@src": icon
            }
        }
        )

        epg_config.append(id)

dict = {
    'channels' : channels
}

print(epg_config)