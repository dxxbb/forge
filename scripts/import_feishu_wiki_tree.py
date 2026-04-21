#!/usr/bin/env python3
"""Fetch a Feishu wiki subtree to markdown via larksuite/cli skill commands.

Usage: feishu_import.py <wiki_token_or_url> <output_dir>

- Uses `lark-cli docs +fetch` (skill-maintained) for content.
- Uses `lark-cli wiki spaces/nodes` for subtree walk.
- Normalizes <mention-doc> -> [title](wiki-url); prepends `# title` if missing.
"""
import json
import pathlib
import re
import subprocess
import sys

FEISHU_DOMAIN = "dxyopc001.feishu.cn"


def _lark(args: list[str]) -> str:
    return subprocess.check_output(
        ["lark-cli", *args], stderr=subprocess.DEVNULL
    ).decode()


def resolve_node(token: str) -> dict:
    out = _lark([
        "api", "GET", "/open-apis/wiki/v2/spaces/get_node",
        "--params", json.dumps({"token": token}),
    ])
    return json.loads(out)["data"]["node"]


def list_children(space_id: str, parent_token: str) -> list[dict]:
    out = _lark([
        "api", "GET", f"/open-apis/wiki/v2/spaces/{space_id}/nodes",
        "--params", json.dumps({"parent_node_token": parent_token, "page_size": 50}),
        "--page-all",
    ])
    items: list[dict] = []
    for line in out.split("\n"):
        s = line.strip()
        if not s.startswith("{"):
            continue
        try:
            obj = json.loads(s)
        except json.JSONDecodeError:
            continue
        if obj.get("code") == 0 and "data" in obj:
            items.extend(obj["data"].get("items") or [])
    if not items:
        try:
            obj = json.loads(out[out.find("{"):])
            items = obj["data"].get("items") or []
        except Exception:
            items = []
    return items


def fetch_docx(obj_token: str) -> tuple[str, str]:
    out = _lark(["docs", "+fetch", "--doc", obj_token])
    obj = json.loads(out)
    return obj["data"].get("title") or "", obj["data"].get("markdown") or ""


def normalize(title: str, md: str) -> str:
    def _mention(m: re.Match) -> str:
        tok, text = m.group(1), m.group(2)
        return f"[{text}](https://{FEISHU_DOMAIN}/wiki/{tok})"
    md = re.sub(
        r'<mention-doc token="([^"]+)"[^>]*>([^<]*)</mention-doc>',
        _mention,
        md,
    )
    if title and not md.lstrip().startswith(f"# {title}"):
        md = f"# {title}\n\n{md}"
    return md.rstrip() + "\n"


def is_empty_shell(title: str, md: str) -> bool:
    """True when doc has no content beyond title + directory-placeholder tags."""
    stripped = md
    stripped = re.sub(r"^\s*#\s+.+$", "", stripped, count=1, flags=re.MULTILINE)
    stripped = re.sub(r'<sub-page-list[^>]*/>', "", stripped)
    return stripped.strip() == ""


def slugify(title: str) -> str:
    s = title.strip()
    trans = str.maketrans({
        ":": "-", "/": "-", "\\": "-",
        "*": "-", "?": "-", "|": "-",
        '"': "'", "<": "(", ">": ")",
    })
    s = s.translate(trans)
    s = re.sub(r"\s+", " ", s)
    return s or "untitled"


def walk(node_token: str, out_dir: pathlib.Path, seen: set[str]) -> None:
    if node_token in seen:
        return
    seen.add(node_token)

    node = resolve_node(node_token)
    obj_type = node.get("obj_type")
    obj_token = node.get("obj_token")
    title = node.get("title") or "untitled"
    space_id = node.get("space_id")
    has_child = bool(node.get("has_child"))

    if obj_type != "docx":
        print(f"  [skip non-docx] {title} (obj_type={obj_type})", file=sys.stderr)
        return

    slug = slugify(title)
    t, md = fetch_docx(obj_token)

    if is_empty_shell(t or title, md):
        print(f"  [skip empty shell] {title}", file=sys.stderr)
    else:
        body = normalize(t or title, md)
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / f"{slug}.md"
        target.write_text(body, encoding="utf-8")
        print(f"  wrote {target} ({len(body.splitlines())} lines)", file=sys.stderr)

    if has_child:
        children = list_children(space_id, node_token)
        for c in children:
            walk(c["node_token"], out_dir / slug, seen)


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: feishu_import.py <wiki_token_or_url> <output_dir>", file=sys.stderr)
        return 2
    src, out = sys.argv[1], sys.argv[2]
    m = re.search(r"/wiki/([A-Za-z0-9]+)", src)
    tok = m.group(1) if m else src
    walk(tok, pathlib.Path(out), set())
    return 0


if __name__ == "__main__":
    sys.exit(main())
