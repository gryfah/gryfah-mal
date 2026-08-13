import json
import os
import urllib.request
from datetime import datetime, timezone

USERNAME = "gryfah"
CLIENT_ID = os.environ["MAL_CLIENT_ID"]

url = (
    f"https://api.myanimelist.net/v2/users/{USERNAME}/animelist"
    "?fields=list_status&limit=1000"
)

all_entries = []

while url:
    print(f"Fetching: {url}")

    req = urllib.request.Request(
        url,
        headers={
            "X-MAL-CLIENT-ID": CLIENT_ID,
            "User-Agent": "gryfah-mal-sync/1.0",
        },
    )

    with urllib.request.urlopen(req, timeout=60) as response:
        payload = json.load(response)

    all_entries.extend(payload.get("data", []))

    url = payload.get("paging", {}).get("next")


anime = []

for entry in all_entries:
    node = entry.get("node", {})
    status = entry.get("list_status", {})

    anime.append(
        {
            "mal_id": node.get("id"),
            "title": node.get("title"),
            "status": status.get("status"),
            "score": status.get("score"),
            "episodes_watched": status.get("num_episodes_watched"),
            "is_rewatching": status.get("is_rewatching"),
            "updated_at_mal": status.get("updated_at"),
            "start_date": status.get("start_date"),
            "finish_date": status.get("finish_date"),
            "mal_url": f"https://myanimelist.net/anime/{node.get('id')}",
        }
    )


output = {
    "mal_user": USERNAME,
    "source": "MyAnimeList API v2",
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "count": len(anime),
    "anime": anime,
}


with open("anime.json", "w", encoding="utf-8") as f:
    json.dump(
        output,
        f,
        ensure_ascii=False,
        indent=2,
    )


print(f"Wrote {len(anime)} anime to anime.json")
