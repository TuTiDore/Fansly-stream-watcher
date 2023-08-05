import os
import json
import subprocess
import cloudscraper
from time import sleep
from dotenv import dotenv_values
from typing import List, Set, Dict, Tuple

BASE_URL = "https://fansly.com"
BASE_API = "https://apiv3.fansly.com/api/v1"

ENV = "config/.env"
BLACKLIST = "config/blacklist.config"

MINUTE = 60


def run():
    current_streams = set()

    while True:
        blacklist = get_blacklist()
        streams = get_current_stream_list()
        if len(streams) == 0:
            print("No followed streamers are online")
        else:
            print(f"Found streams {streams}")
            for stream_id, username in streams:
                if username.lower() in blacklist:
                    continue
                if stream_id in current_streams:
                    continue
                add_stream(stream_id)
                current_streams.add(stream_id)
        sleep(MINUTE)


def get_current_stream_list() -> List[str]:
    headers = get_headers()
    if headers.get("authorization") is None:
        print("Auth header not found in .env")
        return []
    if headers.get("User-Agent") is None:
        print("User agent not found in .env")
        return []

    params = {
        "ngsw-bypass": "true"
    }
    scraper = cloudscraper.create_scraper()
    res = scraper.get(
        f"{BASE_API}/streaming/followingstreams/online", headers=headers, params=params)
    if not res.ok:
        return []
    data = json.loads(res.text)
    response = data.get("response")
    if response is None:
        return []
    aggData = response.get("aggregationData")
    if aggData is None:
        return []
    accounts = aggData.get("accounts")
    if accounts is None:
        return []
    return [(s["id"], s["username"]) for s in accounts]


def add_stream(stream_id: str):
    env = dotenv_values(ENV)
    auth = env.get("FANSLY_HEADER_AUTH")
    user_agent = env.get("FANSLY_HEADER_USER_AGENT")

    print(f"Opening streamlink subprocess [stream_id={stream_id}]")
    url = f"{BASE_URL}/live/{stream_id}"
    output_filepath = "/app/media/{plugin}/{author}/{time}-{author}.ts"
    command = f"streamlink -o \"{output_filepath}\" --fansly-header-auth \"{auth}\" --fansly-header-user-agent \"{user_agent}\" \"{url}\" best"
    subprocess.Popen(command, shell=True)


def get_blacklist():
    if os.path.isfile(BLACKLIST):
        with open(BLACKLIST, 'r') as f:
            l = [n.lower() for n in f.read().split("\n")]
            return set(list(filter(None, l)))
    return set()


def get_headers():
    env = dotenv_values(ENV)
    auth = env.get("FANSLY_HEADER_AUTH")
    user_agent = env.get("FANSLY_HEADER_USER_AGENT")
    headers = {
        'authorization': auth,
        'User-Agent': user_agent,
    }
    return headers


if __name__ == "__main__":
    run()
