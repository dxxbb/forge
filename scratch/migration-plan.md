---
kind: scratch
status: draft
exit: graduate to docs/design.md §migration after Phase 10 done, or rm
created: 2026-04-18
related_design: vault `workspace/project/forge/Scratch of personal OS.md`
---

# Vault Folder Migration Plan

把当前 vault 目录迁移到 scratch 里定稿的新结构。10 个 phase，每个 phase 一个 commit / PR，叶子到根逐层动。

## 用户拍板的设计决策

1. **Section/workspace 的子项**：`project/` 和 `topic/` 都进 `section/workspace/`，且 `workspace/` 自己有一个 `index.md`。
2. **Plan 归属**：`section detail/plan/` 不进 section，源放进 `user/life/master plan/`。
3. **`config/master.md` 直接平放**，不要 `master version/` 子目录。
4. **`output/openclaw/` 和 `output/claude.ai/` 现在就建空架子**（占位文件）。

## 路径映射总表

| 旧路径 | 新路径 |
|---|---|
| `system/operating-rule/` | `system/operating rule/` |
| `system/monitor-inbox/` | `system/monitor inbox/` |
| `system/change-log/` | `system/change log/` |
| `system/pr-review/` | `system/PR review/` |
| `ingest src/clipping/` | `knowledge base/src/clipping/` |
| `knowledge base/tech/...` | `knowledge base/wiki/topic/tech/...` |
| `knowledge base/index.md` | `knowledge base/wiki/index.md` |
| `conversation memory/daily/<date>/*` | `assist/memory collection/history/<date>/*` |
| `conversation memory/claude code memory/*` | `assist/memory collection/agents memory/memory of claude.md`（合并） |
| `assist/section detail/me/identity.md` | `assist/SP/section/about user/identity.md` |
| `assist/section detail/preference/assist.md` | `assist/SP/section/preference/assist.md` |
| `assist/section detail/project/forge.md` | `assist/SP/section/workspace/project/forge.md` |
| `assist/section detail/topic/` | `assist/SP/section/workspace/topic/` |
| `assist/section detail/knowledge base/` | `assist/SP/section/knowledge base/` |
| `assist/section detail/plan/` | （空，drop；plan 源进 `user/life/master plan/`） |
| `assist/section detail/index.md` | `assist/SP/section/index.md` |
| （新增） | `assist/SP/section/workspace/index.md` |
| `assist/sp/master.md` | `assist/SP/config/master.md` |
| `assist/view/claude code/CLAUDE.md` | `assist/SP/output/claude code/claude.md` |
| （新增空架子） | `assist/SP/output/openclaw/{agents,identity,memory,heartbeat}.md` |
| （新增空架子） | `assist/SP/output/claude.ai/` |
| `assist/tool/skills/doc-management.md` | `assist/learn and improve/skill/item/doc-management.md` |
| `assist/tool/skills/index.md` | `assist/learn and improve/skill/index.md` |
| （新建投影） | `assist/SP/section/skill/index.md`（pointer-only，引 learn-and-improve canonical） |
| Working Style 段（master.md inline） | `assist/learn and improve/preference/item/working-style.md` + `assist/SP/section/preference/working-style.md` |
| `user/about me/` | `user/me/about me, philosophy/` |
| （新增空架子） | `user/me/resume/bytedance/` |
| （新增）plan 源 | `user/life/master plan/` |

## Phase 顺序（叶子到根）

每个 phase 一次 commit，commit message 格式：`Migrate phase N: <short>`。

### Phase 1 — system/ 目录重命名（kebab → space）

- `git mv` 4 个目录（operating-rule / monitor-inbox / change-log / pr-review）
- `forge/scripts/*.py` 里 `STATE_FILE` `INBOX_DIR` `CHANGE_LOG_DIR` 等常量同步改
- 确认 hooks 和 `~/.claude/CLAUDE.md` symlink 不受影响
- **风险**：低
- **验证**：`watch.py --dry-run` 跑通；`approve.py` smoke test

### Phase 2 — `ingest src/clipping/` → `knowledge base/src/clipping/`

- `git mv "ingest src" "knowledge base/src"`（如 `ingest src` 下只有 `clipping/`）或仅 `git mv` clipping
- watch.py classify 里 `ingest src/` 前缀改 `knowledge base/src/`
- events/ingest.md SOP 同步改
- **风险**：中
- **验证**：dry-run 跑一遍，确认新 ingest commit 被识别为 ingest event

### Phase 3 — KB topic 移到 wiki/

- `git mv "knowledge base/tech" "knowledge base/wiki/topic/tech"`
- `git mv "knowledge base/index.md" "knowledge base/wiki/index.md"`
- `grep -rl "knowledge base/tech" .` 全部更新
- master.md upstream 字段 `knowledge base/index.md` → `knowledge base/wiki/index.md`
- KB topic 页内部 cross-link 也要 grep
- events/ingest.md SOP 改
- **风险**：中
- **验证**：deps.py --check-cycles；master.md rebuild 后 SP 里 KB section 链接还能点

### Phase 4 — conversation memory → assist/memory collection

- `conversation memory/daily/<date>/*.md` → `assist/memory collection/history/<date>/*.md`（git mv 保 history）
- `conversation memory/claude code memory/*` 内容**合并**进单个 `assist/memory collection/agents memory/memory of claude.md`（按 frontmatter / 时间排序，按累积观察的方式整合）
- watch.py classify：
  - `conversation memory/claude code memory/` → `assist/memory collection/agents memory/`
  - `conversation memory/` → `assist/memory collection/history/`
- `import_cc_history.py` / `import_cc_memory.py` 输出路径改
- **风险**：中（合并文件需要人工/agent 整理，不只是 mv）
- **验证**：import 脚本手动跑一次小批量

### Phase 5 — section detail → SP/section（含子项重命名）

按映射表搬。要点：
- `me/` → `about user/`
- `project/forge.md` → `workspace/project/forge.md`
- `topic/` → `workspace/topic/`（空但保留目录）
- `knowledge base/` 直接平移
- `plan/` drop（plan 源进 user/life/，phase 9 处理）
- `index.md` → `SP/section/index.md`
- 新增 `SP/section/workspace/index.md`（列 active project + topic）
- 更新 master.md upstream + selection_criterion 全部路径
- section-rebuild.md SOP 同步改
- **风险**：高（深层结构改名）
- **验证**：deps.py + master.md rebuild + view rebuild + 比对 CLAUDE.md 内容无意外丢失

### Phase 6 — assist/sp → assist/SP/config

- `git mv assist/sp/master.md assist/SP/config/master.md`
- view 文件 upstream 字段更新
- sp-rebuild.md SOP 改
- 注意 macOS 默认 case-insensitive，`sp` → `SP` 同名重命名要走 git case-sensitive 流程（先 mv 到中间名再 mv 到目标名）
- **风险**：中（macOS case-sensitivity 陷阱）
- **验证**：`git ls-files` 确认 SP 大小写正确

### Phase 7 — view → SP/output + 空架子 + symlink 重指

- `git mv "assist/view/claude code/CLAUDE.md" "assist/SP/output/claude code/claude.md"`
- 新建 `assist/SP/output/openclaw/{agents.md,identity.md,memory.md,heartbeat.md}` 空架子（每个 frontmatter `kind: derived, status: scaffold`）
- 新建 `assist/SP/output/claude.ai/` 空目录 + 占位 README 说明形态待定
- `~/.claude/CLAUDE.md` symlink 重指：先确认 mv 完成，再 `ln -sfn /Users/dxy-air/dxy_OS/assist/SP/output/claude code/claude.md /Users/dxy-air/.claude/CLAUDE.md`
- view-rebuild.md SOP 改
- **风险**：高（symlink 切换瞬间不能 SP rebuild 进行；先做 git，再切 symlink，最后验证）
- **验证**：`readlink ~/.claude/CLAUDE.md`；新开一个 Claude Code session 确认 SP 仍加载

### Phase 8 — tool/skills → learn and improve/skill；preference 抽源

- `git mv assist/tool/skills/doc-management.md assist/learn and improve/skill/item/doc-management.md`
- `git mv assist/tool/skills/index.md assist/learn and improve/skill/index.md`
- 新建 `assist/SP/section/skill/index.md` —— pointer 只列 skill 名 + path（引 learn-and-improve canonical）
- 把 master.md 现 inline 的 "Working Style" 段抽出：
  - 源进 `assist/learn and improve/preference/item/working-style.md`
  - 投影进 `assist/SP/section/preference/working-style.md`
- master.md upstream 改：原来 `section detail/preference/assist.md` 删 / 替换
- **风险**：中（要重做我前面那次 wiring）
- **验证**：rebuild SP，CLAUDE.md 里 Skills + Working Style 都还在

### Phase 9 — user/about me → user/me；plan 进 user/life

- `git mv user/about me user/me/about me, philosophy`（或拆分）
- 新建 `user/me/resume/bytedance/` 空架子
- 把任何之前 inline 在 master.md / section/me 里的 plan 内容抽出，放 `user/life/master plan/`（如果没有内容，只创建空架子）
- section/about user 的 upstream 引用更新到 `user/me/...`
- **风险**：低
- **验证**：deps.py orphan check

### Phase 10 — scripts classify() 合并 + 最终审查

- watch.py classify() 全表重写：
  - `knowledge base/src/` → `ingest`
  - `assist/memory collection/history/` → `conversation`
  - `assist/memory collection/agents memory/` → `cc_memory`
  - `assist/learn and improve/skill/` → `skill_change`（新事件，可能要加到 events/）
  - `assist/learn and improve/preference/` → `preference_change`（新事件）
  - `workspace/white board/` → `whiteboard`（新事件）
  - `workspace/project/` `workspace/topic/` `workspace/reading/` `workspace/writing/` 不变
  - `user/daily memo/` `user/me/` `user/life/` 各自分类
- forge/CLAUDE.md 项目级配置更新（提到 `_archive/` 之类）
- 跑 watch.py + bench.py 一遍校验
- 决定 `scratch/migration-plan.md`：graduate 到 `docs/design.md §Migration history` 还是 `git rm`

## 跨 phase 风险 / 注意

1. **macOS case-insensitive FS**：`assist/sp/` → `assist/SP/`、`assist/view/` 不变但 `assist/SP/output/` 是新名。同一目录里 `sp` 和 `SP` 在 macOS HFS+/APFS 默认是同一名。**Phase 6 必须**走两步 mv：`git mv assist/sp assist/sp_tmp && git mv assist/sp_tmp assist/SP`。
2. **watch.py 幻觉 TODO**：纯 `git mv` 是 R100，watch.py 跳过；但若 mv 同时改内容（比如更新 frontmatter）会变 R0xx，触发 TODO。**对策**：每个 phase 拆两次 commit —— 先纯 mv（R100，watch 跳过），再改内容（这次 watch 看到的是 modify，会触发，但路径已是新路径）。
3. **change-log 历史不动**：里面 `source_path` 是历史 frozen 引用，改了反而失真。
4. **symlink 切换窗口**：Phase 7 mv 完到 ln -sfn 完成之间 `~/.claude/CLAUDE.md` 短暂断链，Claude Code session 在这段开会读不到 SP。建议在没活跃 session 时做。
5. **Inbox 老 TODO**：迁移开始前 inbox 应清零（处理或标 skipped），免得跨 phase 状态错乱。

## 落地节奏建议

- Phase 1-3 一组：风险低，可在一个工作时段连做
- Phase 4-5 一组：中风险，需要小心 import 脚本和 section detail 拆分
- Phase 6-7 一组：高风险，建议单独时段，前后做 backup
- Phase 8-10 一组：收尾，做完跑全套 verification

每组之间停一下，确认 SP rebuild 后的 CLAUDE.md 没意外丢失内容、Claude Code 新 session 能正常加载，再进下一组。
