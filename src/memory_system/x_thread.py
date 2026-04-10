from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_BASE_URL = "https://api.x.com"
DEFAULT_TWEET_FIELDS = [
    "author_id",
    "conversation_id",
    "created_at",
    "in_reply_to_user_id",
    "public_metrics",
    "referenced_tweets",
]
DEFAULT_USER_FIELDS = [
    "created_at",
    "name",
    "protected",
    "username",
    "verified",
]
DEFAULT_EXPANSIONS = [
    "author_id",
    "in_reply_to_user_id",
    "referenced_tweets.id",
    "referenced_tweets.id.author_id",
]


class XApiError(RuntimeError):
    """Raised when the X API returns a non-success response."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_replies_query(tweet_id: str) -> str:
    return f"conversation_id:{tweet_id} -is:retweet"


def build_fields_params() -> dict[str, str]:
    return {
        "expansions": ",".join(DEFAULT_EXPANSIONS),
        "tweet.fields": ",".join(DEFAULT_TWEET_FIELDS),
        "user.fields": ",".join(DEFAULT_USER_FIELDS),
    }


def _request_json(url: str, bearer_token: str) -> dict[str, Any]:
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {bearer_token}",
            "User-Agent": "memory-system-x-thread/0.1",
        },
    )
    try:
        with urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:  # pragma: no cover - exercised in live use
        body = exc.read().decode("utf-8", errors="replace")
        raise XApiError(f"X API error {exc.code} for {url}: {body}") from exc


class XApiClient:
    def __init__(self, bearer_token: str, api_base_url: str = API_BASE_URL) -> None:
        self.bearer_token = bearer_token
        self.api_base_url = api_base_url.rstrip("/")

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        query = urlencode({key: value for key, value in (params or {}).items() if value is not None})
        url = f"{self.api_base_url}{path}"
        if query:
            url = f"{url}?{query}"
        return _request_json(url, self.bearer_token)


def _users_by_id(includes: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    users = {}
    for user in (includes or {}).get("users", []):
        users[user["id"]] = user
    return users


def normalize_post(post: dict[str, Any], includes: dict[str, Any] | None = None) -> dict[str, Any]:
    users = _users_by_id(includes)
    author = users.get(post.get("author_id"), {})
    metrics = post.get("public_metrics", {})
    return {
        "id": post["id"],
        "text": post.get("text", ""),
        "author_id": post.get("author_id"),
        "author_name": author.get("name"),
        "author_username": author.get("username"),
        "author_verified": author.get("verified", False),
        "created_at": post.get("created_at"),
        "conversation_id": post.get("conversation_id"),
        "in_reply_to_user_id": post.get("in_reply_to_user_id"),
        "referenced_tweets": post.get("referenced_tweets", []),
        "public_metrics": {
            "reply_count": metrics.get("reply_count", 0),
            "retweet_count": metrics.get("retweet_count", 0),
            "like_count": metrics.get("like_count", 0),
            "quote_count": metrics.get("quote_count", 0),
            "bookmark_count": metrics.get("bookmark_count", 0),
            "impression_count": metrics.get("impression_count", 0),
        },
    }


def normalize_page(page: dict[str, Any]) -> list[dict[str, Any]]:
    includes = page.get("includes")
    return [normalize_post(item, includes) for item in page.get("data", [])]


def _sort_posts(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(posts, key=lambda item: (item.get("created_at") or "", item["id"]))


def _dedupe_posts(posts: list[dict[str, Any]], exclude_ids: set[str] | None = None) -> list[dict[str, Any]]:
    exclude_ids = exclude_ids or set()
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for post in posts:
        post_id = post["id"]
        if post_id in seen or post_id in exclude_ids:
            continue
        seen.add(post_id)
        deduped.append(post)
    return _sort_posts(deduped)


def fetch_post_lookup(client: XApiClient, tweet_id: str) -> dict[str, Any]:
    params = build_fields_params()
    return client.get(f"/2/tweets/{tweet_id}", params)


def fetch_replies_pages(client: XApiClient, tweet_id: str, scope: str = "recent", max_pages: int = 10) -> list[dict[str, Any]]:
    if scope not in {"recent", "all"}:
        raise ValueError("scope must be 'recent' or 'all'")
    path = "/2/tweets/search/recent" if scope == "recent" else "/2/tweets/search/all"
    params: dict[str, Any] = {
        "query": build_replies_query(tweet_id),
        "max_results": 100,
        **build_fields_params(),
    }
    pages: list[dict[str, Any]] = []
    for _ in range(max_pages):
        page = client.get(path, params)
        pages.append(page)
        next_token = page.get("meta", {}).get("next_token")
        if not next_token:
            break
        params["next_token"] = next_token
    return pages


def fetch_quote_pages(client: XApiClient, tweet_id: str, max_pages: int = 10) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "max_results": 100,
        **build_fields_params(),
    }
    pages: list[dict[str, Any]] = []
    for _ in range(max_pages):
        page = client.get(f"/2/tweets/{tweet_id}/quote_tweets", params)
        pages.append(page)
        next_token = page.get("meta", {}).get("next_token")
        if not next_token:
            break
        params["pagination_token"] = next_token
    return pages


def build_thread_snapshot(
    root_page: dict[str, Any],
    reply_pages: list[dict[str, Any]],
    quote_pages: list[dict[str, Any]],
    scope: str,
) -> dict[str, Any]:
    root = normalize_post(root_page["data"], root_page.get("includes"))
    replies = _dedupe_posts(
        [post for page in reply_pages for post in normalize_page(page)],
        exclude_ids={root["id"]},
    )
    quotes = _dedupe_posts([post for page in quote_pages for post in normalize_page(page)])

    participants: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"username": None, "name": None, "reply_count": 0, "quote_count": 0, "post_count": 0}
    )
    for post in replies:
        key = post.get("author_id") or post["id"]
        bucket = participants[key]
        bucket["username"] = post.get("author_username")
        bucket["name"] = post.get("author_name")
        bucket["reply_count"] += 1
        bucket["post_count"] += 1
    for post in quotes:
        key = post.get("author_id") or post["id"]
        bucket = participants[key]
        bucket["username"] = post.get("author_username")
        bucket["name"] = post.get("author_name")
        bucket["quote_count"] += 1
        bucket["post_count"] += 1

    participant_rows = sorted(
        participants.values(),
        key=lambda item: (-item["post_count"], -item["quote_count"], item["username"] or ""),
    )

    return {
        "tweet_id": root["id"],
        "fetched_at": utc_now_iso(),
        "scope": scope,
        "root": root,
        "replies": replies,
        "quotes": quotes,
        "stats": {
            "reply_count": len(replies),
            "quote_count": len(quotes),
            "participant_count": len(participant_rows),
        },
        "participants": participant_rows,
    }


def _top_posts(posts: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    def score(item: dict[str, Any]) -> tuple[int, int, str]:
        metrics = item.get("public_metrics", {})
        engagement = (
            metrics.get("like_count", 0)
            + metrics.get("quote_count", 0)
            + metrics.get("retweet_count", 0)
            + metrics.get("reply_count", 0)
        )
        return (-engagement, -(metrics.get("impression_count", 0)), item["id"])

    return sorted(posts, key=score)[:limit]


def _excerpt(text: str, max_chars: int = 180) -> str:
    squashed = " ".join(text.split())
    if len(squashed) <= max_chars:
        return squashed
    return f"{squashed[: max_chars - 1].rstrip()}…"


def render_thread_report(snapshot: dict[str, Any]) -> str:
    root = snapshot["root"]
    stats = snapshot["stats"]
    lines: list[str] = []
    lines.append(f"# X Thread Report: {root['id']}")
    lines.append("")
    lines.append(f"- fetched_at: `{snapshot['fetched_at']}`")
    lines.append(f"- scope: `{snapshot['scope']}`")
    lines.append(f"- root_author: `@{root.get('author_username') or 'unknown'}`")
    lines.append(f"- replies_captured: `{stats['reply_count']}`")
    lines.append(f"- quotes_captured: `{stats['quote_count']}`")
    lines.append(f"- participants_captured: `{stats['participant_count']}`")
    lines.append("")
    lines.append("## Root Post")
    lines.append("")
    lines.append(f"- author: `@{root.get('author_username') or 'unknown'}`")
    lines.append(f"- created_at: `{root.get('created_at') or 'unknown'}`")
    lines.append(f"- excerpt: {_excerpt(root.get('text', ''))}")
    lines.append("")

    if snapshot["participants"]:
        lines.append("## Top Participants")
        lines.append("")
        lines.append("| user | replies | quotes | total |")
        lines.append("| --- | ---: | ---: | ---: |")
        for row in snapshot["participants"][:10]:
            user = row["username"] or "(unknown)"
            lines.append(f"| @{user} | {row['reply_count']} | {row['quote_count']} | {row['post_count']} |")
        lines.append("")

    top_replies = _top_posts(snapshot["replies"])
    if top_replies:
        lines.append("## Sample Replies")
        lines.append("")
        for item in top_replies:
            lines.append(f"- `@{item.get('author_username') or 'unknown'}`: {_excerpt(item.get('text', ''))}")
        lines.append("")

    top_quotes = _top_posts(snapshot["quotes"])
    if top_quotes:
        lines.append("## Sample Quote Posts")
        lines.append("")
        for item in top_quotes:
            lines.append(f"- `@{item.get('author_username') or 'unknown'}`: {_excerpt(item.get('text', ''))}")
        lines.append("")

    lines.append("## Analyst Notes")
    lines.append("")
    lines.append("- 支持观点：")
    lines.append("- 反对或保留意见：")
    lines.append("- 更进一步的想法：")
    lines.append("- 对本项目的输入：")
    lines.append("")
    lines.append("## Limits")
    lines.append("")
    lines.append("- `recent` search 只能覆盖最近 7 天；更老的线程要用 `all` search 权限。")
    lines.append("- 受保护、已删除、或当前 token 无权访问的内容抓不到。")
    lines.append("- quote/reply 能抓多少，取决于你的 X API 权限和分页上限。")
    return "\n".join(lines)


def write_thread_bundle(
    out_dir: Path,
    root_page: dict[str, Any],
    reply_pages: list[dict[str, Any]],
    quote_pages: list[dict[str, Any]],
    snapshot: dict[str, Any],
    report: str,
) -> None:
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "root.json").write_text(json.dumps(root_page, ensure_ascii=False, indent=2), encoding="utf-8")
    for index, page in enumerate(reply_pages, start=1):
        filename = raw_dir / f"replies-page-{index:03d}.json"
        filename.write_text(json.dumps(page, ensure_ascii=False, indent=2), encoding="utf-8")
    for index, page in enumerate(quote_pages, start=1):
        filename = raw_dir / f"quotes-page-{index:03d}.json"
        filename.write_text(json.dumps(page, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "thread.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "thread.md").write_text(report, encoding="utf-8")
