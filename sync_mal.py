import json
import time
import urllib.request
from datetime import datetime, timezone

USERNAME = "gryfah"
BASE_URL = f"https://api.jikan.moe/v4/users/{USERNAME}/animelist"

all_entries = []
page = 1

while True:
    url = f"{BASE_URL}?page={page}"

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "gryfah-mal-sync/1.0"
        }
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.load(response)

    all_entries.extend(payload.get("data", []))

    pagination = payload.get("pagination", {})

    if not pagination.get("has_next_page"):
        break

    page += 1

    # Jikan limits requests; be polite.
    time.sleep(1)

anime = []

for entry in all_entries:
    node = entry.get("node", {})
    list_status = entry.get("list_status", {})

    anime.append(
        {
            "mal_id": node.get("mal_id"),
            "title": node.get("title"),
            "url": node.get("url"),
            "status": list_status.get("status"),
            "score": list_status.get("score"),
            "episodes_watched": list_status.get("episodes_seen"),
            "is_rewatching": list_status.get("is_rewatching"),
            "updated_at_mal": list_status.get("updated_at"),
        }
    )

output = {
    "mal_user": USERNAME,
    "source": "Jikan / MyAnimeList",
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "count": len(anime),
    "anime": anime,
}

with open("anime.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Wrote {len(anime)} anime to anime.json")
