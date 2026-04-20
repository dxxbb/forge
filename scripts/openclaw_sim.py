#!/usr/bin/env python3
"""
openclaw_sim.py - simulate applying forge's openclaw view to a paocai workspace.

Steps:
  1. Mirror an openclaw workspace (default: ~/.cache/forge/paocai_memory) into a sandbox
     under ~/.cache/forge/openclaw-sim/workspace.
  2. Apply forge's openclaw view from the vault:
     - Replace USER.md with vault `01 assist/SP/output/openclaw/USER.md`.
     - Splice MEMORY.md between marker comments using vault `MEMORY.partial.md`;
       append (with markers) if markers don't yet exist.
  3. Compose the effective system prompt that openclaw would assemble at session
     start, following the documented load order:
        SOUL.md
        USER.md
        memory/YYYY-MM-DD.md (today + yesterday if present)
        MEMORY.md   (only when --main-session)

Outputs:
  - sandbox path
  - composed-SP text written to <sandbox>/effective_sp.md
  - optional diff lines (USER.md before/after, MEMORY.md before/after)

Usage:
  python3 openclaw_sim.py
  python3 openclaw_sim.py --main-session
  python3 openclaw_sim.py --source ~/.cache/forge/paocai_memory --vault ~/dxy_OS
  python3 openclaw_sim.py --print-sp     # print composed SP to stdout
  python3 openclaw_sim.py --diff         # show before/after diffs
  python3 openclaw_sim.py --check        # run fact-coverage assertions on composed SP

Vault path defaults to $PERSONAL_OS_VAULT or ~/dxy_OS.
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import os
import shutil
import sys
from pathlib import Path

DEFAULT_SOURCE = Path.home() / ".cache" / "forge" / "paocai_memory"
DEFAULT_SANDBOX = Path.home() / ".cache" / "forge" / "openclaw-sim" / "workspace"
SPLICE_BEGIN = "<!-- forge:knowledge-index:start -->"
SPLICE_END = "<!-- forge:knowledge-index:end -->"


def vault_root() -> Path:
    env = os.environ.get("PERSONAL_OS_VAULT")
    if env:
        return Path(env).expanduser().resolve()
    return (Path.home() / "dxy_OS").resolve()


def mirror(source: Path, sandbox: Path) -> None:
    if sandbox.exists():
        shutil.rmtree(sandbox)
    sandbox.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, sandbox, ignore=shutil.ignore_patterns(".git"))


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    return text[end + 4 :].lstrip("\n")


def apply_user(vault: Path, sandbox: Path) -> tuple[str, str]:
    src = vault / "01 assist" / "SP" / "output" / "openclaw" / "USER.md"
    dst = sandbox / "USER.md"
    before = dst.read_text(encoding="utf-8") if dst.exists() else ""
    payload = strip_frontmatter(src.read_text(encoding="utf-8"))
    dst.write_text(payload, encoding="utf-8")
    return before, payload


def splice_memory(vault: Path, sandbox: Path) -> tuple[str, str]:
    src = vault / "01 assist" / "SP" / "output" / "openclaw" / "MEMORY.partial.md"
    dst = sandbox / "MEMORY.md"
    before = dst.read_text(encoding="utf-8") if dst.exists() else ""
    block = strip_frontmatter(src.read_text(encoding="utf-8")).strip()

    if SPLICE_BEGIN in before and SPLICE_END in before:
        head = before.split(SPLICE_BEGIN, 1)[0].rstrip()
        tail = before.split(SPLICE_END, 1)[1].lstrip()
        new = head + "\n\n" + block + "\n\n" + tail
    else:
        sep = "" if before.endswith("\n") else "\n"
        new = before + sep + "\n" + block + "\n"

    dst.write_text(new, encoding="utf-8")
    return before, new


def collect_recent_daily(sandbox: Path, today: dt.date) -> list[Path]:
    yesterday = today - dt.timedelta(days=1)
    out: list[Path] = []
    for d in (today, yesterday):
        f = sandbox / "memory" / f"{d.isoformat()}.md"
        if f.is_file():
            out.append(f)
    return out


def compose_sp(sandbox: Path, *, main_session: bool, today: dt.date) -> str:
    parts: list[str] = []
    for name in ("SOUL.md", "USER.md"):
        p = sandbox / name
        if p.is_file():
            parts.append(f"# === {name} ===\n\n" + p.read_text(encoding="utf-8").strip())
    for f in collect_recent_daily(sandbox, today):
        parts.append(
            f"# === memory/{f.name} ===\n\n" + f.read_text(encoding="utf-8").strip()
        )
    if main_session:
        memory_md = sandbox / "MEMORY.md"
        if memory_md.is_file():
            parts.append(
                "# === MEMORY.md ===\n\n" + memory_md.read_text(encoding="utf-8").strip()
            )
    return "\n\n---\n\n".join(parts) + "\n"


# Fact-coverage assertions for the composed openclaw SP.
# Each tuple: (tier, question summary, list of phrases that ALL must appear).
# Phrases are matched as substrings (case-sensitive) against the composed SP text.
# This is a static stand-in for bench.py — it validates the SP carries the fact,
# not that an agent reasons over it correctly. Real LLM bench is the live setup.
FACT_CHECKS: list[tuple[str, str, list[str]]] = [
    # identity tier — facts forge owns under "about user"
    ("identity", "GitHub handle", ["dxxbb"]),
    ("identity", "birth year", ["1981"]),
    ("identity", "city", ["北京"]),
    ("identity", "MBTI", ["INTJ"]),
    ("identity", "former employer + role", ["字节跳动", "技术 leader"]),
    ("identity", "former product line", ["云相册", "剪映/CapCut"]),
    ("identity", "current state 2026", ["2026", "FIRE"]),
    ("identity", "2026 vision keyword", ["ikigai"]),
    ("identity", "thinking preference", ["系统思维", "第一性原理"]),
    ("identity", "working language", ["简体中文"]),
    # preferences tier — facts forge owns under "preference"
    ("preferences", "bypassPermissions mode", ["bypassPermissions"]),
    ("preferences", "research scope: english world too", ["不局限于中文"]),
    ("preferences", "research forums coverage", ["X", "Reddit", "YouTube", "小红书"]),
    ("preferences", "boundary: no fabrication", ["不要伪造引用或数据"]),
    ("preferences", "boundary: state uncertainty", ["不确定的事先说不确定"]),
    # knowledge tier — facts forge owns under "knowledge base" (only in main session)
    ("knowledge-main", "KB topic: claude-code page exists", ["tech/ai/claude-code/"]),
    ("knowledge-main", "KB topic: codex page exists", ["tech/ai/codex/"]),
    ("knowledge-main", "KB topic: personal-os practitioners page", ["practitioners.md"]),
    ("knowledge-main", "KB topic: memory patterns page", ["memory-patterns.md"]),
    # paocai-owned content — verifies we don't overwrite SOUL/MEMORY
    # NOTE: agent name "泡菜" only lives in IDENTITY.md and MEMORY.md. Per
    # paocai's AGENTS.md the startup chain is SOUL → USER → daily → MEMORY-if-main,
    # which means IDENTITY.md is not auto-loaded — in non-main sessions paocai
    # technically does not know its own name. That is a paocai-side issue, not
    # forge's; we only assert these checks in main-session mode where MEMORY.md
    # carries the name.
    ("paocai-self", "SOUL principle preserved", ["genuinely helpful"]),
    ("paocai-self-main", "agent name preserved (via MEMORY.md)", ["泡菜"]),
    ("paocai-self-main", "MEMORY 主题索引 (paocai's own) preserved", ["主题索引"]),
]


def run_checks(sp_text: str, *, main_session: bool) -> tuple[int, int, list[str]]:
    """Return (passed, total, failure_messages)."""
    failures: list[str] = []
    passed = 0
    total = 0
    for tier, summary, phrases in FACT_CHECKS:
        # *-main checks only validated in main session (MEMORY.md is loaded then)
        if tier.endswith("-main") and not main_session:
            continue
        total += 1
        missing = [p for p in phrases if p not in sp_text]
        if missing:
            failures.append(f"  [{tier}] {summary}: missing {missing}")
        else:
            passed += 1
    return passed, total, failures


def short_diff(label: str, before: str, after: str, n: int = 3) -> str:
    diff = list(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile=f"{label} (before)",
            tofile=f"{label} (after)",
            lineterm="",
            n=n,
        )
    )
    return "\n".join(diff) if diff else f"({label}: no change)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=str(DEFAULT_SOURCE),
                    help="path to upstream paocai workspace clone")
    ap.add_argument("--sandbox", default=str(DEFAULT_SANDBOX),
                    help="path to write the sandbox (will be wiped)")
    ap.add_argument("--vault", help="vault root (default $PERSONAL_OS_VAULT or ~/dxy_OS)")
    ap.add_argument("--main-session", action="store_true",
                    help="include MEMORY.md in composed SP (main-session-only file)")
    ap.add_argument("--today", default=dt.date.today().isoformat(),
                    help="date used to pick today/yesterday memory files (YYYY-MM-DD)")
    ap.add_argument("--print-sp", action="store_true",
                    help="print composed SP to stdout")
    ap.add_argument("--diff", action="store_true",
                    help="print USER.md and MEMORY.md before/after diffs")
    ap.add_argument("--check", action="store_true",
                    help="run static fact-coverage assertions on composed SP")
    args = ap.parse_args()

    source = Path(args.source).expanduser().resolve()
    sandbox = Path(args.sandbox).expanduser().resolve()
    vault = Path(args.vault).expanduser().resolve() if args.vault else vault_root()

    if not source.is_dir():
        sys.stderr.write(f"source workspace not found: {source}\n")
        return 2
    if not vault.is_dir():
        sys.stderr.write(f"vault not found: {vault}\n")
        return 2

    today = dt.date.fromisoformat(args.today)

    print(f"source:  {source}")
    print(f"sandbox: {sandbox}")
    print(f"vault:   {vault}")
    print(f"today:   {today.isoformat()}  (main_session={args.main_session})")

    mirror(source, sandbox)
    user_before, user_after = apply_user(vault, sandbox)
    mem_before, mem_after = splice_memory(vault, sandbox)

    sp = compose_sp(sandbox, main_session=args.main_session, today=today)
    sp_path = sandbox / "effective_sp.md"
    sp_path.write_text(sp, encoding="utf-8")

    print(f"\nWrote composed SP: {sp_path}  ({len(sp):,} chars)")

    if args.diff:
        print("\n" + short_diff("USER.md", user_before, user_after))
        print("\n" + short_diff("MEMORY.md", mem_before, mem_after))

    if args.print_sp:
        print("\n--- composed SP ---")
        print(sp)

    if args.check:
        passed, total, failures = run_checks(sp, main_session=args.main_session)
        print(f"\n--- fact coverage: {passed}/{total} passed ---")
        if failures:
            print("FAIL:")
            for f in failures:
                print(f)
            return 1
        print("OK")

    return 0


if __name__ == "__main__":
    sys.exit(main())
