# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Run tests:
```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

Run a single test file:
```bash
PYTHONPATH=src python3 -m unittest tests.test_memory_system
```

Run CLI commands (always requires `PYTHONPATH=src`):
```bash
PYTHONPATH=src python3 -m memory_system seed --user demo
PYTHONPATH=src python3 -m memory_system search --user demo --query "your query"
PYTHONPATH=src python3 -m memory_system context --user demo --query "your query"
PYTHONPATH=src python3 -m memory_system remember --user demo --content "..." --kind preference --tier semantic --source manual --temperature hot
```

Rebuild the visualization site (`site/index.html`) from `site/content.md` and `site/diagrams/*.json`:
```bash
python3 scripts/build_site.py
```

Preview the site locally:
```bash
python3 -m http.server 8126 --bind 127.0.0.1 -d site
```

## Architecture

The reference implementation is a zero-dependency, local-first memory engine. Data is persisted to `data/memory_store.json` by default.

**Layer stack** (`src/memory_system/`):

- `models.py` — all core dataclasses: `MemoryRecord`, `ProfileState`, `ContextPacket`, `SearchResult`, plus the enums `MemoryKind`, `MemoryTier`, `MemoryTemperature`, `SourceKind`.
- `storage.py` — `JsonMemoryRepository`: reads/writes the JSON store. The only I/O layer; everything else is pure.
- `service.py` — `MemoryService`: orchestrates write (`remember`), retrieval (`search`), and context assembly (`assemble_context` / `render_context`). Also holds scoring logic (token overlap + recency + importance + temperature).
- `cli.py` — thin argparse wrapper over `MemoryService`; subcommands are `seed`, `remember`, `profile`, `search`, `context`.

**Key design invariants:**

- `MemoryRecord.active` is False once `invalid_at` is set. Superseded records are soft-deleted, not removed.
- Search scoring weights: token overlap 50%, temperature 20%, importance 20%, recency 10%. Records with zero token overlap are excluded entirely.
- `MemoryTemperature` (hot/warm/cold) is orthogonal to `MemoryTier` (working/profile/semantic/episodic/procedural). Temperature controls serving eagerness; tier controls memory classification.
- `ContextPacket` always contains: structured profile, hot memories (up to 5), query-relevant memories, recent episodes (up to 3), procedures (up to 3).

**Docs structure:**

- `docs/research/` — survey of current memory approaches (LangGraph, Mem0, Letta, etc.)
- `docs/architecture/` — reference architecture and platform review
- `docs/implementation/` — Obsidian KB SOP and phased roadmap
- `examples/phase1-kb-first/` — concrete KB layout example with projections for Claude, OpenClaw, and ChatGPT
- `site/` — static visualization page; source of truth is `content.md` + `diagrams/*.json`, not `index.html`
