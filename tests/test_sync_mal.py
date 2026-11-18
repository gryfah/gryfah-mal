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
        states = (None, "plan_to_watch", "watching", "on_hold", "completed", "dropped")
        def expected_signals(old, new):
            if new == "plan_to_watch":
                return ["brief_needed"]
            signals = []
            if old == "plan_to_watch" or new == "completed":
                signals.append("next_up")
            if new == "completed":
                signals.append("post_watch")
            return signals
        for old in states:
            for new in states:
                with self.subTest(old=old, new=new):
                    events = find_events(entry(42, old), entry(42, new), NOW)
                    if old == new:
                        self.assertEqual(events, [])
                    elif expected_signals(old, new):
                        self.assertEqual(len(events), 1)
                        self.assertEqual(events[0]["signals"], expected_signals(old, new))
                        self.assertEqual(events[0]["mal_id"], 42)
                        self.assertEqual(events[0]["previous_status"], old)
                        self.assertEqual(events[0]["status"], new)
                    else:
                        self.assertEqual(events, [])

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

    def test_metadata_only_edit_has_no_event(self):
        before = entry(90, "plan_to_watch", 0)
        after = entry(90, "plan_to_watch", 8)
        after[0]["title"] = "Updated display title"
        self.assertEqual(find_events(before, after, NOW), [])
        completed = entry(91, "completed", 7)
        rescored = entry(91, "completed", 9)
        self.assertEqual(find_events(completed, rescored, NOW), [])

    def test_created_completed_and_dropped(self):
        for status, expected in (
            ("completed", ["next_up", "post_watch"]),
            ("dropped", []),
        ):
            with self.subTest(status=status):
                events = find_events([], entry(101, status), NOW)
                if expected:
                    self.assertEqual(events[0]["signals"], expected)
                else:
                    self.assertEqual(events, [])

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
        self.assertEqual(rerun["ptw_exits_pending"], {})

    def test_ptw_watching_on_hold_completed_one_next_up(self):
        pending = {}
        first = find_events(entry(73, "plan_to_watch"),
                            entry(73, "watching"), NOW, pending)
        self.assertEqual(first[0]["signals"], ["next_up"])
        self.assertIn("73", pending)
        second = find_events(entry(73, "watching"), entry(73, "on_hold"),
                             NOW + timedelta(hours=1), pending)
        self.assertEqual(second, [])
        third = find_events(entry(73, "on_hold"), entry(73, "completed", 8),
                            NOW + timedelta(hours=2), pending)
        self.assertEqual(third[0]["signals"], ["post_watch"])
        self.assertEqual(pending, {})

    def test_ptw_exit_persists_across_sync_and_resets(self):
        pending = {}
        first = find_events(entry(74, "plan_to_watch"),
                            entry(74, "dropped"), NOW, pending)
        result = prepare_results({}, first, NOW, pending)
        self.assertEqual(result["ptw_exits_pending"]["74"], first[0]["event_id"])

        restored = dict(result["ptw_exits_pending"])
        later = find_events(entry(74, "dropped"), entry(74, "completed", 6),
                            NOW + timedelta(hours=2), restored)
        self.assertEqual(later[0]["signals"], ["post_watch"])
        self.assertNotIn("74", restored)
        back_to_ptw = find_events(entry(74, "completed"),
                                  entry(74, "plan_to_watch"),
                                  NOW + timedelta(hours=3), restored)
        self.assertEqual(back_to_ptw[0]["signals"], ["brief_needed"])
        again = find_events(entry(74, "plan_to_watch"), entry(74, "watching"),
                            NOW + timedelta(hours=4), restored)
        self.assertEqual(again[0]["signals"], ["next_up"])

    def test_new_dropped_does_not_trigger_next_up(self):
        self.assertEqual(find_events([], entry(101, "dropped"), NOW), [])

    def test_duplicate_ids_fail_closed(self):
        one = entry(6, "plan_to_watch")
        with self.assertRaises(ValueError):
            find_events(one + one, [], NOW)


if __name__ == "__main__":
    unittest.main()
