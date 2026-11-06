"""Regression tests for MAL status transitions, without network requests."""
import unittest
from datetime import datetime, timedelta, timezone

from sync_mal import find_events, prepare_results

NOW = datetime(2026, 11, 6, 15, 0, tzinfo=timezone.utc)


def entry(mal_id, status, score=0):
    if status is None:
        return []
    return [{
        "mal_id": mal_id,
        "title": f"Test anime {mal_id}",
        "status": status,
        "score": score,
        "mal_url": f"https://myanimelist.net/anime/{mal_id}",
    }]


class ClassificationTests(unittest.TestCase):
    def test_all_state_transitions(self):
        states = (None, "plan_to_watch", "completed", "dropped")
        expected = {
            None: ["next_up"],
            "plan_to_watch": ["brief_needed"],
            "completed": ["next_up", "post_watch"],
            "dropped": ["next_up"],
        }
        for old in states:
            for new in states:
                with self.subTest(old=old, new=new):
                    events = find_events(entry(42, old), entry(42, new), NOW)
                    if old == new:
                        self.assertEqual(events, [])
                    else:
                        self.assertEqual(len(events), 1)
                        self.assertEqual(events[0]["signals"], expected[new])
                        self.assertEqual(events[0]["mal_id"], 42)
                        self.assertEqual(events[0]["previous_status"], old)
                        self.assertEqual(events[0]["status"], new)

    def test_multiple_ids_and_unchanged_snapshot(self):
        before = (entry(1, "plan_to_watch")
                  + entry(2, "plan_to_watch")
                  + entry(3, "completed")
                  + entry(4, "plan_to_watch"))
        after = (entry(1, "completed", 8)
                 + entry(2, "dropped")
                 + entry(3, "plan_to_watch")
                 + entry(5, "plan_to_watch"))
        changes = find_events(before, after, NOW)
        self.assertEqual(
            [(e["mal_id"], e["signals"]) for e in changes],
            [
                (1, ["next_up", "post_watch"]),
                (2, ["next_up"]),
                (3, ["brief_needed"]),
                (4, ["next_up"]),
                (5, ["brief_needed"]),
            ],
        )
        self.assertEqual(changes[0]["score"], 8)
        self.assertIsNone(changes[3]["score"])
        self.assertEqual(find_events(after, after, NOW), [])

    def test_created_completed_and_dropped(self):
        for status, expected in (
            ("completed", ["next_up", "post_watch"]),
            ("dropped", ["next_up"]),
        ):
            with self.subTest(status=status):
                events = find_events([], entry(101, status), NOW)
                self.assertEqual(events[0]["signals"], expected)

    def test_event_retention_and_unique_ids(self):
        new_events = find_events([], entry(45, "completed", 7), NOW)
        self.assertEqual(len(new_events), 1)
        old_event = dict(new_events[0])
        old_event["event_id"] = "old"
        old_event["detected_at"] = (NOW - timedelta(days=8)).isoformat()
        result = prepare_results({"events": [old_event]}, new_events, NOW)
        self.assertEqual(len(result["events"]), 1)
        self.assertEqual(result["events"][0]["signals"], ["next_up", "post_watch"])
        self.assertEqual(result["events"][0]["event_id"], new_events[0]["event_id"])
        rerun = prepare_results(result, new_events, NOW)
        self.assertEqual(len(rerun["events"]), 1)
        self.assertNotIn("ptw_exits_pending", rerun)

    def test_duplicate_ids_fail_closed(self):
        one = entry(6, "plan_to_watch")
        with self.assertRaises(ValueError):
            find_events(one + one, [], NOW)


if __name__ == "__main__":
    unittest.main()
