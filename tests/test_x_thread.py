from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from memory_system.x_thread import build_replies_query, build_thread_snapshot, render_thread_report, write_thread_bundle


ROOT_PAGE = {
    "data": {
        "id": "100",
        "text": "Root post",
        "author_id": "u1",
        "created_at": "2026-04-04T10:00:00.000Z",
        "conversation_id": "100",
        "public_metrics": {"reply_count": 2, "retweet_count": 1, "like_count": 10, "quote_count": 1},
    },
    "includes": {"users": [{"id": "u1", "username": "karpathy", "name": "Andrej Karpathy", "verified": True}]},
}

REPLY_PAGE = {
    "data": [
        {
            "id": "100",
            "text": "Root post duplicate from search",
            "author_id": "u1",
            "created_at": "2026-04-04T10:00:00.000Z",
            "conversation_id": "100",
            "public_metrics": {},
        },
        {
            "id": "101",
            "text": "This is useful for research workflows.",
            "author_id": "u2",
            "created_at": "2026-04-04T10:05:00.000Z",
            "conversation_id": "100",
            "public_metrics": {"reply_count": 0, "retweet_count": 0, "like_count": 5, "quote_count": 0},
        },
    ],
    "includes": {"users": [{"id": "u2", "username": "alice", "name": "Alice"}]},
}

QUOTE_PAGE = {
    "data": [
        {
            "id": "201",
            "text": "Good idea, but I'd keep AI output out of the clean vault.",
            "author_id": "u3",
            "created_at": "2026-04-04T11:00:00.000Z",
            "conversation_id": "201",
            "public_metrics": {"reply_count": 1, "retweet_count": 2, "like_count": 12, "quote_count": 0},
        }
    ],
    "includes": {"users": [{"id": "u3", "username": "bob", "name": "Bob"}]},
}


class XThreadTests(unittest.TestCase):
    def test_build_replies_query_uses_conversation_id(self) -> None:
        self.assertEqual(build_replies_query("2039805659525644595"), "conversation_id:2039805659525644595 -is:retweet")

    def test_build_thread_snapshot_dedupes_root_and_counts_participants(self) -> None:
        snapshot = build_thread_snapshot(ROOT_PAGE, [REPLY_PAGE], [QUOTE_PAGE], scope="recent")

        self.assertEqual(snapshot["stats"]["reply_count"], 1)
        self.assertEqual(snapshot["stats"]["quote_count"], 1)
        self.assertEqual(snapshot["stats"]["participant_count"], 2)
        self.assertEqual(snapshot["replies"][0]["id"], "101")
        usernames = {item["username"] for item in snapshot["participants"]}
        self.assertEqual(usernames, {"alice", "bob"})

    def test_render_thread_report_contains_sections(self) -> None:
        snapshot = build_thread_snapshot(ROOT_PAGE, [REPLY_PAGE], [QUOTE_PAGE], scope="recent")
        report = render_thread_report(snapshot)

        self.assertIn("# X Thread Report: 100", report)
        self.assertIn("## Top Participants", report)
        self.assertIn("## Sample Replies", report)
        self.assertIn("## Sample Quote Posts", report)
        self.assertIn("## Analyst Notes", report)

    def test_write_thread_bundle_creates_expected_files(self) -> None:
        snapshot = build_thread_snapshot(ROOT_PAGE, [REPLY_PAGE], [QUOTE_PAGE], scope="recent")
        report = render_thread_report(snapshot)

        with tempfile.TemporaryDirectory() as temp_dir:
            out_dir = Path(temp_dir) / "x_threads" / "100"
            write_thread_bundle(out_dir, ROOT_PAGE, [REPLY_PAGE], [QUOTE_PAGE], snapshot, report)

            self.assertTrue((out_dir / "raw" / "root.json").exists())
            self.assertTrue((out_dir / "raw" / "replies-page-001.json").exists())
            self.assertTrue((out_dir / "raw" / "quotes-page-001.json").exists())
            self.assertTrue((out_dir / "thread.json").exists())
            self.assertTrue((out_dir / "thread.md").exists())


if __name__ == "__main__":
    unittest.main()
