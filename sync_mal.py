"""Synchronize a MyAnimeList list and record meaningful status transitions."""

import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

USERNAME = "gryfah"
ANIME_FILE = Path("anime.json")
BACKUP_FILE = Path("anime_backup.json")
EVENTS_FILE = Path("results.json")
MAX_EVENTS = 200
EVENT_MAX_AGE = timedelta(days=7)

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
        "mean",
        "num_scoring_users",
    ]
)


def fetch_anime():
    client_id = os.environ["MAL_CLIENT_ID"]
    url = (
        f"https://api.myanimelist.net/v2/users/{USERNAME}/animelist"
        f"?fields={FIELDS}&limit=1000&nsfw=true"
    )
    all_entries = []
    while url:
        print(f"Fetching: {url}")
        req = urllib.request.Request(
            url,
            headers={
                "X-MAL-CLIENT-ID": client_id,
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
        season = node.get("start_season") or {}
        anime.append(
            {
                "mal_id": node.get("id"),
                "title": node.get("title"),
                "status": status.get("status"),
                "score": status.get("score"),
                "mal_mean_score": node.get("mean"),
                "mal_num_scoring_users": node.get("num_scoring_users"),
                "episodes_watched": status.get("num_episodes_watched"),
                "is_rewatching": status.get("is_rewatching"),
                "updated_at_mal": status.get("updated_at"),
                "user_start_date": status.get("start_date"),
                "user_finish_date": status.get("finish_date"),
                "release_start_date": node.get("start_date"),
                "release_end_date": node.get("end_date"),
                "release_year": season.get("year"),
                "release_season": season.get("season"),
                "media_type": node.get("media_type"),
                "num_episodes": node.get("num_episodes"),
                "genres": [g.get("name") for g in node.get("genres", []) if g.get("name")],
                "studios": [s.get("name") for s in node.get("studios", []) if s.get("name")],
                "mal_url": f"https://myanimelist.net/anime/{node.get('id')}",
            }
        )
    anime.sort(
        key=lambda item: (
            item["release_start_date"] is None,
            item["release_start_date"] or "9999-99-99",
            item["mal_id"] or 0,
        )
    )
    return anime


def index_by_mal_id(anime):
    indexed = {}
    for item in anime:
        mal_id = item.get("mal_id")
        if not isinstance(mal_id, int) or mal_id in indexed:
            raise ValueError(f"Missing or duplicated MAL ID: {mal_id!r}")
        indexed[mal_id] = item
    return indexed


def read_json(path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def write_json(path, data):
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
    temporary.replace(path)


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def find_events(previous, current, now):
    """Classify MAL changes by destination: PTW, completed, dropped, removed.

    Each changed mal_id produces one event with the corresponding action signals.
    No intermediary 'watching' state or PTW-exit bookkeeping is required.
    """
    old = index_by_mal_id(previous)
    new = index_by_mal_id(current)
    events = []
    detected_at = now.isoformat().replace("+00:00", "Z")
    event_prefix = now.strftime("%Y%m%dT%H%M%S%fZ")

    for mal_id in sorted(old.keys() | new.keys()):
        before = old.get(mal_id)
        after = new.get(mal_id)
        prior_status = before.get("status") if before else None
        status = after.get("status") if after else None
        if prior_status == status:
            continue

        signals = []
        if status == "plan_to_watch":
            # Profile builder still discovers missing briefs by scanning anime.json.
            signals.append("brief_needed")
        if status in ("completed", "dropped") or after is None:
            signals.append("next_up")
        if status == "completed":
            signals.append("post_watch")

        if signals:
            source = after or before
            events.append(
                {
                    "event_id": f"{event_prefix}-{mal_id}-{prior_status or 'new'}-to-{status or 'removed'}",
                    "detected_at": detected_at,
                    "mal_id": mal_id,
                    "title": source.get("title"),
                    "previous_status": prior_status,
                    "status": status,
                    "score": after.get("score") if after else None,
                    "signals": signals,
                    "mal_url": source.get("mal_url"),
                }
            )

    return events

def prepare_results(existing, additions, now):
    cutoff = now - EVENT_MAX_AGE
    kept = []
    for event in existing.get("events", []):
        timestamp = parse_time(event["detected_at"])
        if timestamp >= cutoff:
            kept.append(event)
    seen = {event["event_id"] for event in kept}
    kept.extend(event for event in additions if event["event_id"] not in seen)
    kept.sort(key=lambda event: (event["detected_at"], event["event_id"]))
    return {
        "schema_version": 1,
        "updated_at": now.isoformat().replace("+00:00", "Z"),
        "events": kept[-MAX_EVENTS:],
    }

def main():
    if not ANIME_FILE.is_file():
        raise RuntimeError("Missing anime.json baseline; refusing to generate false new events")
    previous_document = read_json(ANIME_FILE)
    previous_anime = previous_document["anime"]
    index_by_mal_id(previous_anime)

    previous_results = read_json(EVENTS_FILE) if EVENTS_FILE.is_file() else {}
    current_anime = fetch_anime()
    index_by_mal_id(current_anime)
    if not current_anime or (previous_anime and len(current_anime) < len(previous_anime) * 0.8):
        raise RuntimeError("Suspiciously incomplete MAL response; old data preserved")

    now = datetime.now(timezone.utc)
    # The first NSFW-inclusive fetch repairs a previously incomplete baseline.
    # Do not report the recovered historical entries as newly completed shows.
    if previous_document.get("nsfw_included") is True:
        events = find_events(previous_anime, current_anime, now)
    else:
        events = []
        print("NSFW-inclusive baseline initialized; transition detection skipped once")
    results = prepare_results(previous_results, events, now)
    current_document = {
        "mal_user": USERNAME,
        "source": "MyAnimeList API v2",
        "updated_at": now.isoformat(),
        "count": len(current_anime),
        "sort": "release_start_date_ascending",
        "nsfw_included": True,
        "anime": current_anime,
    }
    # The backup is the exact previous snapshot, not the freshly fetched list.
    write_json(BACKUP_FILE, previous_document)
    write_json(EVENTS_FILE, results)
    write_json(ANIME_FILE, current_document)
    print(f"Wrote {len(current_anime)} anime, {len(events)} new events, "
          f"{len(results['events'])} retained events")


if __name__ == "__main__":
    main()
