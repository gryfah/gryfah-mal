import json
import os
import urllib.request
from datetime import datetime, timezone

USERNAME = "gryfah"
CLIENT_ID = os.environ["MAL_CLIENT_ID"]

FIELDS = ",".join(
    [
        "list_status",
        "start_date",
        "end_date",
        "start_season",
        "media_type",
        "num_episodes",
        "genres",
        "studios",
    ]
)

url = (
    f"https://api.myanimelist.net/v2/users/{USERNAME}/animelist"
    f"?fields={FIELDS}&limit=1000"
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
    list_status = entry.get("list_status", {})
    start_season = node.get("start_season") or {}

    anime.append(
        {
            "mal_id": node.get("id"),
            "title": node.get("title"),

            # Current Gryfah MAL status
            "status": list_status.get("status"),
            "score": list_status.get("score"),
            "episodes_watched": list_status.get("num_episodes_watched"),
            "is_rewatching": list_status.get("is_rewatching"),
            "updated_at_mal": list_status.get("updated_at"),

            # Gryfah viewing history
            "user_start_date": list_status.get("start_date"),
            "user_finish_date": list_status.get("finish_date"),

            # Anime release metadata
            "release_start_date": node.get("start_date"),
            "release_end_date": node.get("end_date"),
            "release_year": start_season.get("year"),
            "release_season": start_season.get("season"),
            "media_type": node.get("media_type"),
            "num_episodes": node.get("num_episodes"),

            # Useful recommendation metadata
            "genres": [
                genre.get("name")
                for genre in node.get("genres", [])
                if genre.get("name")
            ],
            "studios": [
                studio.get("name")
                for studio in node.get("studios", [])
                if studio.get("name")
            ],

            "mal_url": f"https://myanimelist.net/anime/{node.get('id')}",
        }
    )


# Oldest releases first.
# Entries without known release dates are placed last.
anime.sort(
    key=lambda item: (
        item["release_start_date"] is None,
        item["release_start_date"] or "9999-99-99",
        item["mal_id"] or 0,
    )
)


output = {
    "mal_user": USERNAME,
    "source": "MyAnimeList API v2",
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "count": len(anime),
    "sort": "release_start_date_ascending",
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
