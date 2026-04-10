#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path

from memory_system.x_thread import (
    XApiClient,
    build_thread_snapshot,
    fetch_post_lookup,
    fetch_quote_pages,
    fetch_replies_pages,
    render_thread_report,
    write_thread_bundle,
)


DEFAULT_ROOT = Path("data/x_threads")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch an X thread into raw JSON and a markdown report.")
    parser.add_argument("tweet_id", help="Root tweet/post id.")
    parser.add_argument("--out-dir", type=Path, help="Output directory. Defaults to data/x_threads/<tweet_id>.")
    parser.add_argument("--scope", choices=["recent", "all"], default="recent", help="Search scope for replies.")
    parser.add_argument("--max-reply-pages", type=int, default=10)
    parser.add_argument("--max-quote-pages", type=int, default=10)
    parser.add_argument("--skip-quotes", action="store_true", help="Do not fetch quote posts.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    bearer_token = (
        os.getenv("X_BEARER_TOKEN")
        or os.getenv("X_API_BEARER_TOKEN")
        or os.getenv("TWITTER_BEARER_TOKEN")
    )
    if not bearer_token:
        parser.error("Missing X bearer token. Set X_BEARER_TOKEN.")

    out_dir = args.out_dir or (DEFAULT_ROOT / args.tweet_id)
    client = XApiClient(bearer_token)

    root_page = fetch_post_lookup(client, args.tweet_id)
    reply_pages = fetch_replies_pages(client, args.tweet_id, scope=args.scope, max_pages=args.max_reply_pages)
    quote_pages = [] if args.skip_quotes else fetch_quote_pages(client, args.tweet_id, max_pages=args.max_quote_pages)

    snapshot = build_thread_snapshot(root_page, reply_pages, quote_pages, scope=args.scope)
    report = render_thread_report(snapshot)
    write_thread_bundle(out_dir, root_page, reply_pages, quote_pages, snapshot, report)

    print(f"Wrote thread bundle to {out_dir}")
    print(f"- raw root: {out_dir / 'raw' / 'root.json'}")
    print(f"- snapshot: {out_dir / 'thread.json'}")
    print(f"- report: {out_dir / 'thread.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
