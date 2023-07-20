import os
import json
import subprocess
import cloudscraper
from time import sleep
from typing import List, Set, Dict, Tuple

BASE_URL = "https://fansly.com"
BASE_API = "https://apiv3.fansly.com/api/v1"

MINUTE = 60

auth = os.environ.get("FANSLY_HEADER_AUTH")
user_agent = os.environ.get("FANSLY_HEADER_USER_AGENT")
headers = {
    'authorization': auth,
    'User-Agent': user_agent,
}
params = {
    "ngsw-bypass": "true"
}

def run():
    current_streams = set()
    while True:
        stream_ids = get_current_stream_list()
        if len(stream_ids) == 0:
            print("No followed streamers are online")
        else:
            for stream_id in stream_ids:
                print(f"Checking if stream is already downloading [stream_id={stream_id}]")
                if stream_id in current_streams:
                    continue
                add_stream(stream_id)
                current_streams.add(stream_id)
        sleep(MINUTE)

def get_current_stream_list() -> List[str]:
    scraper = cloudscraper.create_scraper()
    res = scraper.get(f"{BASE_API}/streaming/followingstreams/online", headers=headers, params=params)
    data = json.loads(res.text)
    return [s["accountId"] for s in data["response"]["streams"]]

def add_stream(stream_id: str):
    print(f"Opening streamlink subprocess [stream_id={stream_id}]")
    url = f"{BASE_URL}/live/{stream_id}"
    output_filepath = "/app/media/{plugin}/{author}/{time:%Y%m%d%H%M%S}.ts"
    command = f"streamlink -o \"{output_filepath}\" --fansly-header-auth \"{auth}\" --fansly-header-user-agent \"{user_agent}\" \"{url}\" best"
    subprocess.Popen(command, shell=True)

if __name__ == "__main__":
    run()