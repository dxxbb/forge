#!/usr/bin/env python3
"""
deps.py - compute the dependency graph of a personal OS vault.

Reads frontmatter from every *.md file under the vault root and builds
a reverse index: upstream_path -> [downstream_paths].

Usage:
    python3 deps.py --downstream <path>
    python3 deps.py --upstream <path>
    python3 deps.py --check-cycles
    python3 deps.py --graph                 # dump full graph as JSON

Vault path defaults to $PERSONAL_OS_VAULT or ~/dxy_OS.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("deps.py needs PyYAML: pip install pyyaml\n")
    sys.exit(1)


def vault_root() -> Path:
    env = os.environ.get("PERSONAL_OS_VAULT")
    if env:
        return Path(env).expanduser().resolve()
    return (Path.home() / "dxy_OS").resolve()


def read_frontmatter(path: Path) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    raw = text[3:end].strip()
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def scan_vault(root: Path) -> dict[str, dict]:
    """Return {rel_path: frontmatter_dict} for every md under root."""
    out: dict[str, dict] = {}
    for md in root.rglob("*.md"):
        if any(part.startswith(".") for part in md.relative_to(root).parts):
            continue
        fm = read_frontmatter(md)
        rel = str(md.relative_to(root))
        out[rel] = fm or {}
    return out


def build_forward(index: dict[str, dict]) -> dict[str, list[str]]:
    """Forward: downstream -> [upstream, ...]."""
    forward: dict[str, list[str]] = {}
    for path, fm in index.items():
        ups = fm.get("upstream") or []
        if isinstance(ups, str):
            ups = [ups]
        forward[path] = [str(u).strip() for u in ups if str(u).strip()]
    return forward


def build_reverse(forward: dict[str, list[str]]) -> dict[str, list[str]]:
    """Reverse: upstream -> [downstream, ...]."""
    rev: dict[str, list[str]] = {}
    for downstream, ups in forward.items():
        for up in ups:
            rev.setdefault(up, []).append(downstream)
    return rev


def transitive(graph: dict[str, list[str]], start: str) -> list[str]:
    """Transitive closure reachable from start in graph (excludes start)."""
    seen: set[str] = set()
    order: list[str] = []
    stack = [start]
    while stack:
        node = stack.pop()
        for nxt in graph.get(node, []):
            if nxt in seen:
                continue
            seen.add(nxt)
            order.append(nxt)
            stack.append(nxt)
    return order


def check_cycles(forward: dict[str, list[str]]) -> list[list[str]]:
    """Return a list of cycles (each cycle is a list of nodes). Empty = OK."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {n: WHITE for n in forward}
    for ups in forward.values():
        for u in ups:
            color.setdefault(u, WHITE)
    cycles: list[list[str]] = []

    def dfs(node: str, path: list[str]) -> None:
        color[node] = GRAY
        path.append(node)
        for nxt in forward.get(node, []):
            if color.get(nxt, WHITE) == GRAY:
                if nxt in path:
                    cycles.append(path[path.index(nxt):] + [nxt])
            elif color.get(nxt, WHITE) == WHITE:
                dfs(nxt, path)
        path.pop()
        color[node] = BLACK

    for node in list(color):
        if color[node] == WHITE:
            dfs(node, [])
    return cycles


def main() -> int:
    ap = argparse.ArgumentParser()
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--downstream", metavar="PATH")
    grp.add_argument("--upstream", metavar="PATH")
    grp.add_argument("--check-cycles", action="store_true")
    grp.add_argument("--graph", action="store_true")
    ap.add_argument("--vault", help="vault root (default: $PERSONAL_OS_VAULT or ~/dxy_OS)")
    args = ap.parse_args()

    root = Path(args.vault).expanduser().resolve() if args.vault else vault_root()
    if not root.is_dir():
        sys.stderr.write(f"vault not found: {root}\n")
        return 2

    index = scan_vault(root)
    forward = build_forward(index)
    reverse = build_reverse(forward)

    if args.check_cycles:
        cycles = check_cycles(forward)
        if cycles:
            sys.stderr.write("CYCLES DETECTED:\n")
            for c in cycles:
                sys.stderr.write("  " + " -> ".join(c) + "\n")
            return 1
        print("no cycles")
        return 0

    if args.graph:
        print(json.dumps({"forward": forward, "reverse": reverse}, indent=2, ensure_ascii=False))
        return 0

    if args.downstream:
        for p in transitive(reverse, args.downstream):
            print(p)
        return 0

    if args.upstream:
        for p in transitive(forward, args.upstream):
            print(p)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
