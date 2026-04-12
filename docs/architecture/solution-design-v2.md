# Solution Design v2

更新日期：`2026-04-08`

作者：Claude Opus 4.6（基于全部调研材料独立写的版本，供对比）

## 0. 这篇文档解决什么

这篇文档回答 5 个问题：

1. 这个系统到底在解决什么问题
2. 系统的整体结构是什么
3. 一条信息从进入到被平台使用，完整走过哪些步骤
4. Phase 1 具体交付什么，不交付什么
5. 怎么判断 Phase 1 做完了

## 1. 问题定义

### 1.1 核心问题

你同时在用 Claude Code、Codex、OpenClaw、ChatGPT。

每个平台都有自己的 memory 机制，但它们之间不通。你在 Claude Code 里确认的一条偏好，Codex 不知道。你在 ChatGPT 里整理的一个项目结论，Claude Code 看不到。

所以你需要一个地方：

- 集中维护你的长期知识、偏好、决策、流程
- 然后把它们分发到各个平台

### 1.2 这个问题为什么不好解决

三个原因：

1. 四个平台的入口文件格式和发现机制完全不同
2. 不是所有内容都适合立刻进入长期主库 — agent 生成的草稿、未确认的结论、临时整理，都需要一个缓冲区
3. 平台侧会产生新的有价值信息（纠正、新规则），这些信息需要回流到主库，但不能无门槛地写回

### 1.3 不在 Phase 1 范围内的问题

- 自动从聊天记录中提取 memory
- vector / graph 检索
- 跨设备实时同步
- 多用户协作
- ChatGPT 自动读取本地文件

## 2. 设计原则

先把 6 条硬规则钉死，后面所有决策都从这里推导。

### 原则 1：一条信息只有一个 canonical home

不复制文件。一个知识点只在 Store 里存一份。平台看到的都是 projection（派生视图）。

### 原则 2：generated 内容不能直接进主库

agent 产出的总结、候选结论、临时编译，必须先停在 Workspace。只有通过 review 才能 promote 到 Store。

这条规则来自调研里最强的社区共识：**治理先于规模**。

### 原则 3：目录表达本体，properties 表达维度

一个文件的路径只回答"它是什么"。它属于哪个项目、谁生成的、有没有被确认 — 这些都进 frontmatter properties。

这是 Obsidian "single home, multiple views" 原则的直接应用。

### 原则 4：平台入口是具体文件，不是抽象概念

不说"把上下文喂给 agent"。而是说清楚：改 `~/.claude/CLAUDE.md` 的第 3 行。

### 原则 5：维护成本必须低

如果一套系统需要每天花 30 分钟手工整理才能运转，它会在两周内被放弃。

这条来自 Huy Tieu 的经验，也是所有"第二大脑"项目反复验证的硬约束。

### 原则 6：先能手工跑通，再谈自动化

Phase 1 不写脚本。先用手工操作验证整条链路。如果手工操作本身不顺畅，自动化只会放大问题。

## 3. 整体结构

```
Capture  →  Workspace  →  Store  →  Projections
              ↑                        |
              |     review gate        |
              +---- 回流 ← 平台 ←------+
```

四个结构块，两个关键动作（Consolidate 和 Project），一个治理门（review gate）。

### 3.1 Capture

**职责**：接住所有原始输入

放什么：
- `daily/YYYY-MM-DD.md` — 当天的观察、想法、待处理事项
- `inbox/` — 需要尽快处理的纠正和反馈
- `imports/` — 从外部导入的原始材料

不放什么：
- 稳定结论
- 已确认的偏好
- 长期有效的知识

Capture 的内容默认是**脏的、临时的、不保证正确的**。

### 3.2 Workspace

**职责**：放加工中的内容，隔离 generated 和 clean

放什么：
- `candidates/` — agent 生成的候选总结、待确认的结论
- `drafts/` — 人工或 agent 写的草稿
- `reviews/` — 等待 review 的内容，每条标注来源和目标

这是整个系统里最容易被跳过的一层，但它是防止主库被污染的唯一屏障。

**Workspace 的核心规则**：

1. 任何 agent 产出，默认进 Workspace，不进 Store
2. Workspace 里的内容可以被删除、合并、重写，没有历史包袱
3. 从 Workspace promote 到 Store，必须经过 review（Phase 1 是人工 review）

### 3.3 Store

**职责**：长期主库，唯一真相源

Store 只收 **confirmed、clean、persistent** 的内容。

Phase 1 只保留两大类（family）：

**knowledge/**

| 子目录 | 放什么 | 例子 |
|---|---|---|
| `topics/` | 稳定的主题知识 | `memory-architecture.md` |
| `entities/` | 具体事物的说明 | `obsidian.md` |

**state/**

| 子目录 | 放什么 | 例子 |
|---|---|---|
| `profile/` | 个人偏好和约束 | `writing-style.md` |
| `projects/` | 项目状态和当前决策 | `memory-system.md` |
| `decisions/` | 明确的设计决策 | `phase-1-scope.md` |
| `procedures/` | 可复用的操作流程 | `weekly-review.md` |
| `lessons/` | 已验证的经验教训 | `dont-mock-db.md` |

**为什么 Phase 1 不做 evidence family**：

前版方案在 Store 里设了 evidence（sources / clips / observations / extracts）。但 Phase 1 还没有 ingestion pipeline，evidence 目录会长期为空。空结构增加认知负担，不增加实际价值。

等 Phase 2 做 capture ingestion 时再加 evidence。现在 Capture 层已经能接住原始材料。

### 3.4 Projections

**职责**：把 Store 的内容翻译成各平台会读的文件

| 平台 | 产出文件 | 落地位置 |
|---|---|---|
| Claude Code | `CLAUDE.memory.md` | `~/.claude/CLAUDE.md` imports 或 repo `.claude/` |
| Codex | `AGENTS.memory.md` | `~/.codex/AGENTS.md` 或 repo `AGENTS.md` |
| OpenClaw | `MEMORY.md` | agent workspace |
| ChatGPT | `project-summary.md` | 用户手工上传到 project files |

每个 projection 文件头部必须标注：

```yaml
---
generated_at: 2026-04-08
source_nodes:
  - store/state/profile/writing-style.md
  - store/state/projects/memory-system.md
  - store/state/decisions/phase-1-scope.md
delivery_status: synced  # synced / pending / stale
---
```

## 4. 目录结构

```
capture/
  daily/
    2026-04-08.md
  inbox/
    2026-04-08-fix-writing-style.md
  imports/

workspace/
  candidates/
  drafts/
  reviews/

store/
  knowledge/
    topics/
    entities/
  state/
    profile/
    projects/
    decisions/
    procedures/
    lessons/

projections/
  claude/
    CLAUDE.memory.md
  codex/
    AGENTS.memory.md
  openclaw/
    MEMORY.md
  chatgpt/
    project-summary.md

templates/
```

这比前版方案少了几个目录：

- 去掉了 `store/evidence/`（Phase 1 用不到）
- 去掉了 `store/knowledge/syntheses/` 和 `comparisons/`（Phase 1 先不发明这些子类型，有需要时直接放 topics 里）
- 去掉了 `workspace/ephemeral/` 和 `workspace/promote/`（Phase 1 只需要 candidates / drafts / reviews 三个桶）
- 去掉了 `indexes/`（Phase 1 不需要单独的索引目录，Store 文件自己就能兼做索引页）

## 5. Schema

### 5.1 公共 frontmatter

每个 Store 节点都带这组字段：

```yaml
---
id: st_profile_writing_style
kind: profile          # topic / entity / profile / project / decision / procedure / lesson
title: 写作风格偏好
status: confirmed      # confirmed / candidate / superseded / archived

project_refs: []       # 关联项目
domain_refs: [writing] # 关联领域

origin: manual         # manual / agent / import
source_refs: []        # 原始来源链接

created_at: 2026-04-08
updated_at: 2026-04-08
---
```

### 5.2 设计取舍

和前版方案对比，这里做了几个删减：

**去掉了 `family` 字段**。因为 family（knowledge / state）已经由目录路径表达了。`kind` 足够区分具体类型。同一个信息不需要在路径和 properties 里重复编码。

**去掉了 `cleanliness` / `persistence` / `grounding` 三个治理字段**。理由：

- `cleanliness`（clean / generated）：Store 里的内容全部是 clean 的。generated 内容在 Workspace 里，不进 Store。所以这个字段在 Store 节点上永远是 `clean`，没有区分度。
- `persistence`（persistent / ephemeral）：Store 里的内容全部是 persistent 的。ephemeral 内容在 Workspace 里。同理，没有区分度。
- `grounding`（source-backed / synthesized / mixed）：这个信息由 `source_refs` 是否为空隐式表达。有 source_refs 就是 source-backed，没有就是 synthesized。不需要单独字段。

这三个字段在 Workspace 节点上有意义，但 Workspace 里的文件不需要严格 schema — 它们是临时的。

**去掉了 `confirmed_by` / `confirmed_at`**。Phase 1 只有一个用户。所有进入 Store 的内容都是你自己确认的。等多用户或自动 promote 时再加。

**去掉了 `view_refs` 和 `tags`**。Phase 1 不需要 Bases 和 tag 视图。先把文件内的 `[[link]]` 用起来。

### 5.3 kind-specific 字段

只有两个 kind 需要额外字段：

**decision**：
```yaml
decision_status: active  # proposed / active / superseded
supersedes: st_decision_xxx  # 被替代的旧决策
```

**project**：
```yaml
project_status: active  # active / paused / done
current_decisions:
  - st_decision_phase_1_scope
```

其他 kind 不加专用字段。

## 6. 数据流

### 6.1 标准写入流

场景：你今天发现一条新的写作偏好 — "文档少用抽象句式，每节保留 1 个例子"。

```
第 1 步：记到 Capture
  → capture/daily/2026-04-08.md 追加一行

第 2 步：判断成熟度
  → 如果你确定这是长期偏好：直接进 Store
  → 如果不确定：先进 Workspace/candidates/

第 3 步：写入 Store
  → 更新 store/state/profile/writing-style.md

第 4 步：刷新 Projections
  → 更新 projections/claude/CLAUDE.memory.md
  → 更新 projections/codex/AGENTS.memory.md
  → 更新 projections/openclaw/MEMORY.md
  → 更新 projections/chatgpt/project-summary.md（标记 delivery_status: pending）
```

注意第 2 步。前版方案要求所有内容都经过 Workspace，这对确定性很高的偏好来说是多余的摩擦。

**规则**：人类手工输入的、你自己确定的内容，可以跳过 Workspace 直接进 Store。只有 agent 产出的、不确定的、需要 review 的内容，才必须走 Workspace。

这条规则的理由很简单：**review gate 的目的是防止 agent 污染主库，不是给人类自己设障碍**。

### 6.2 平台回流

场景：你在 Claude Code 里工作时，Claude 提出了一个有价值的项目建议。

```
第 1 步：记到 Capture
  → capture/inbox/2026-04-08-project-suggestion.md

第 2 步：进 Workspace
  → workspace/candidates/project-suggestion.md
  → 标注 origin: agent, source_refs: [claude-code-session-xxx]

第 3 步：你 review
  → 确认：promote 到 Store
  → 拒绝：删除或归档

第 4 步：刷新 Projections
```

### 6.3 同天纠正（快路径）

场景：你正在和 Claude Code 工作，发现它的输出风格不对，需要当天立刻纠正。

```
第 1 步：记到 capture/inbox/
  → 写一个 correction item：

  ---
  id: inbox_2026-04-08_writing_fix
  kind: correction
  apply_now: true
  targets: [claude, codex, openclaw]
  expires_at: 2026-04-09
  ---
  文档少用抽象句式，每节保留 1 个例子。

第 2 步：立刻更新目标平台的 projection
  → 在 CLAUDE.memory.md 底部追加这条纠正

第 3 步：当天或次日整理
  → 如果这条纠正值得长期保留：promote 到 Store
  → 关闭 inbox item（移到 capture/archive/ 或直接删除）
```

这条快路径的关键是：**先让平台能用，再慢慢整理进主库**。不要因为 review gate 而牺牲当天的工作效率。

## 7. Projection 生成规则

这是前版方案没有展开的部分。Phase 1 先写死一组简单规则。

### 7.1 每个 projection 包含什么

所有 projection 都从这三个来源组装：

1. `store/state/profile/*` — 所有 confirmed 的偏好
2. `store/state/projects/*` — 当前 active 项目的状态和决策
3. `store/state/procedures/*` — 相关的操作流程

Phase 1 不把 `store/knowledge/` 的内容放进 projection。原因：knowledge 是参考资料，不是行为指令。平台需要的是"你想让我怎么做"，不是"世界上有哪些知识"。

### 7.2 各平台的格式要求

**Claude Code**（`CLAUDE.memory.md`）：

```markdown
# Personal Memory

## 偏好
- 文档尽量简单直接
- 每节保留 1 个例子

## 当前项目：memory-system
- Phase 1：搭建 KB 骨架
- 当前决策：先做 knowledge base，不做 vector/graph

## 操作流程
- 每周日做一次 consolidation
```

**Codex**（`AGENTS.memory.md`）：

格式相同，但措辞更偏指令式（因为 Codex AGENTS.md 的惯例是指令）。

**OpenClaw**（`MEMORY.md`）：

格式相同，遵循 OpenClaw 的 MEMORY.md 惯例。

**ChatGPT**（`project-summary.md`）：

更偏叙述式，因为 ChatGPT project files 的使用场景更接近"背景阅读"。

### 7.3 什么时候该重新生成 projection

Phase 1 的规则很简单：

- 改了 Store 里的任何文件 → 重新生成所有 projection
- 做了同天纠正 → 只 patch 相关平台的 projection

不做 diff、不做增量、不做自动触发。手工跑就够了。

## 8. 平台落地

这部分直接复用 platform-landing-review.md 的结论，不再重复。只补充一张速查表：

| 动作 | Claude Code | Codex | OpenClaw | ChatGPT |
|---|---|---|---|---|
| 个人偏好 | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md` | workspace `MEMORY.md` | project instructions |
| 项目规则 | repo `CLAUDE.md` + import | repo `AGENTS.md` | workspace `MEMORY.md` | project files |
| 同天纠正 | 更新 projection + hook | 更新 repo `AGENTS.md` | 更新 workspace | 不支持自动 |
| 回流 | capture/inbox/ | capture/inbox/ | capture/inbox/ | 手工记录 |

## 9. Review Gate 最小规则

Phase 1 的 review gate 是纯手工的。规则只有 4 条：

1. **人类手工写入的、自己确认的内容**：可以直接进 Store
2. **agent 产出的内容**：必须先进 Workspace，人工 review 后才能 promote
3. **promote 操作**：把文件从 `workspace/` 移到 `store/`，补上 `status: confirmed`，更新 `created_at` / `updated_at`
4. **拒绝的内容**：直接删除，或移到 `workspace/archive/`（如果以后可能有用）

不做自动 review。不做半自动 review。不做 review dashboard。Phase 1 的 review 就是你自己打开文件，看一眼，确认，移动。

## 10. Phase 1 交付物

精确列表，不多不少：

### 必须交付

1. **目录骨架**：`capture/` + `workspace/` + `store/` + `projections/` + `templates/`
2. **公共 frontmatter schema**：§5 定义的字段集
3. **7 个 kind 的 note template**：topic / entity / profile / project / decision / procedure / lesson
4. **4 个平台的 projection template**：各一个
5. **1 个真实例子**：用你自己的真实数据，走完从 Capture 到 Projection 的全流程
6. **1 份操作 SOP**：daily capture → weekly consolidation → projection refresh 的手工步骤
7. **correction item schema**：`apply_now` / `targets` / `expires_at`

### 不交付

- 自动化脚本（Phase 1 全手工）
- evidence family（Phase 2 做）
- knowledge compiler（Phase 3 做）
- vector / graph（Phase 4+）
- Obsidian Bases 视图（用到时再做）
- indexes 目录（Store 文件自己兼做索引页）

## 11. 完成标准

Phase 1 做完的判断标准只有 5 条：

1. 你能在 Store 里找到你所有稳定的偏好、项目状态和决策
2. 三个文件型平台（Claude Code / Codex / OpenClaw）的 projection 是最新的
3. ChatGPT 有一份可上传的 project-summary.md
4. 你做了一次真实的同天纠正，并且第二天成功 consolidate 进了 Store
5. 你做了一次完整的 weekly review，没有觉得太累

第 5 条是最重要的。如果 weekly review 让你觉得累，说明系统设计有问题。

## 12. 和前版方案的主要差异

| 点 | 前版 (solution-design.md) | 本版 |
|---|---|---|
| Store family | evidence / knowledge / state | knowledge / state（evidence 延后） |
| Schema 字段 | 20+ 个公共字段 | 9 个公共字段 |
| 治理字段 | cleanliness / persistence / grounding | 不需要（被结构隔离取代） |
| Workspace 要求 | 所有内容都过 Workspace | 人类确认的可跳过，agent 产出必须过 |
| Projection 规则 | 未定义 | §7 写死了来源、格式和触发条件 |
| Review gate | 原则级 | 4 条具体操作规则 |
| Phase 1 scope | ~15 项交付物 | 7 项必须交付 |
| 自动化 | 提到了刷新脚本 | Phase 1 全手工 |

### 差异背后的一个核心判断

前版方案更像是一个**完整系统的蓝图**。它想一次性把所有状态轴、所有 family、所有治理规则都定义清楚。

本版方案更像是一个**能在明天开始使用的操作系统**。它砍掉了所有 Phase 1 用不到的结构，把省下来的设计预算花在了两个前版没有展开的地方：projection 生成规则和 review gate 具体操作。

这两个选择哪个更好，取决于你的偏好：

- 如果你更看重"架构完整性" → 前版更好
- 如果你更看重"明天就能用" → 本版更好

## 13. Naming Review

> 以下是对本文档所有目录命名的自我审查。每条标注问题严重程度：
> - `[问题]` — 命名有明确缺陷，建议改
> - `[可议]` — 有改进空间，但不阻塞
> - `[OK]` — 没问题

### 13.1 顶层四块名字

```
capture/  workspace/  store/  projections/  templates/
```

**`[问题]` 抽象层次不统一。**

这五个名字分别是：

| 名字 | 它在说什么 | 隐喻类型 |
|---|---|---|
| `capture` | 你在这里**做什么**（捕获） | 动作 |
| `workspace` | 这个地方**是什么**（工作区） | 场所 |
| `store` | 你在这里**做什么**（存储）或这里**是什么**（仓库） | 动作 + 场所，歧义 |
| `projections` | 这里**放的东西叫什么**（投影） | 产出物 |
| `templates` | 这里**放的东西叫什么**（模板） | 产出物 |

五个名字，三种隐喻。`capture` 是动词视角，`workspace` 是名词视角，`store` 两边都沾，`projections` 和 `templates` 是内容物视角。

如果统一成场所隐喻：`intake/ workshop/ vault/ views/ templates/`
如果统一成内容物隐喻：`inputs/ drafts/ records/ projections/ templates/`
如果统一成阶段隐喻：`capture/ process/ persist/ distribute/ —`

但这里有一个更深的问题：**统一隐喻未必是正确目标**。用户打开文件夹时，最重要的不是修辞一致，而是一眼知道"我该往哪放东西"。`capture` 作为动词恰好能指导行为（"东西先 capture 进来"），而 `store` 作为名词指向一个稳定的地方。混搭可能是对的，但需要有意识地选择，不能是随手写的。

**`[问题]` 单复数不统一。**

- 单数：`capture`、`workspace`、`store`
- 复数：`projections`、`templates`

没有规则。如果"容器用单数，内容物集合用复数"，那 `projections/` 应该叫 `projection/`（它是一个投影层）或者 `capture/` 应该叫 `captures/`（它是一堆捕获物）。

建议：**全部用单数**。目录名表达的是分区概念，不是"里面有好多个"。文件系统里 `src/` 不叫 `sources/`，`lib/` 不叫 `libraries/`。

**`[问题]` `store` 是整个系统最重要的结构块，但名字最通用。**

`store` 既是动词又是名词，而且是英语里最泛化的词之一。它不携带任何这个系统特有的语义。你说 "Store 里只收 confirmed、clean、persistent 的内容" — 但 `store` 这个词本身暗示的是"什么都能放"。

对比几个候选：
- `vault` — 暗示"贵重的、锁起来的"，和 Obsidian vault 术语重叠可能是好事也可能混淆
- `canon` — 暗示"正典、权威版本"，直接表达"只收确认过的"这个语义
- `core` — 暗示"核心"，但太泛
- `library` — 暗示"整理过的藏书"，但偏研究
- `registry` — 暗示"注册、登记"，偏事务

如果要名字本身就表达"这里只放确认过的长期内容"，`canon` 或 `vault` 比 `store` 更准确。但也更不寻常。这是一个取舍。

### 13.2 Capture 内部

```
capture/
  daily/
  inbox/
  imports/
```

**`[问题]` `daily` 是形容词，不是名词。**

`daily/` — daily 什么？daily notes? daily logs? daily entries? 作为目录名它不自明。其他两个（`inbox`、`imports`）至少是名词。

候选：`journal/`、`log/`、`daily-notes/`、`days/`

`journal/` 最好 — 它是名词，含义清楚（每天记一笔），而且 Obsidian 社区的惯例就是 daily journal。

**`[可议]` `inbox` 单数 vs `imports` 复数。**

`inbox` 是单数（概念上只有一个收件箱），`imports` 是复数（里面有很多导入物）。逻辑上可以自洽，但放在一起视觉不一致。如果全部用单数：`inbox/`、`import/`。

### 13.3 Workspace 内部

```
workspace/
  candidates/
  drafts/
  reviews/
```

**`[问题]` `candidates` 和 `reviews` 的边界模糊。**

这不完全是命名问题，但命名暴露了设计问题。一个 agent 生成的候选结论，在被 review 之前放在 `candidates/`。当它准备被 review 时，它移到 `reviews/`？还是就地 review？如果就地 review，那 `reviews/` 里放什么？

实际上这三个目录可能会退化成一个：所有东西都扔进 `candidates/` 或 `drafts/`，`reviews/` 永远为空。

如果 Workspace 的本质就是"一个缓冲区"，也许不需要三个子目录。一个 `workspace/` 平铺就够了，用 frontmatter 的 `status: candidate | draft | ready-for-review` 来区分状态。

**`[可议]` `drafts` 和 `candidates` 的区别不明显。**

在文档里的定义是：
- `candidates` = agent 生成的候选总结、待确认的结论
- `drafts` = 人工或 agent 写的草稿

但一个 agent 写的草稿，是 draft 还是 candidate？一个人写了一半的结论，是 draft 还是 candidate？实际使用时用户会犹豫。

### 13.4 Store 内部

```
store/
  knowledge/
    topics/
    entities/
  state/
    profile/
    projects/
    decisions/
    procedures/
    lessons/
```

**`[问题]` `knowledge` 和 `state` 不在同一个抽象层。**

- `knowledge` 回答的是 "内容的性质是什么"（知识）
- `state` 回答的是 "内容的角色是什么"（状态）

一个平行的命名应该是：
- `knowledge/` + `operations/`（都是"内容的领域"）
- `research/` + `practice/`（都是"活动类型"）
- `what-i-know/` + `how-i-work/`（都是"对我的意义"）

`state` 这个词的问题是它太抽象了。profile 是"状态"吗？lesson 是"状态"吗？procedure 是"状态"吗？`decisions` 勉强算当前状态，但 `lessons` 更像是沉淀下来的知识，`procedures` 更像是操作手册。

`state` 这个 family 实际上是一个 **catch-all**：凡是不属于 topic/entity 的，都扔进 state。这说明双 family 分法本身可能有问题。

**`[问题]` `lessons` 放在 `state/` 下面不对。**

一条 lesson（比如"不要 mock 数据库"）不是"当前状态"，它是"已验证的经验"。它更接近 knowledge 而不是 state。如果硬要分：

- `knowledge/` 放"关于世界的知识"
- `state/` 放"关于我当前处境的信息"

那 lesson 两边都不完全对。它是"从我的经历中提炼出的知识" — 既不是世界知识，也不是当前状态。

这再次暗示：**双 family 分法可能不适合 Phase 1**。Phase 1 只有 7 个 kind，也许直接平铺更诚实：

```
store/
  topics/
  entities/
  profile/
  projects/
  decisions/
  procedures/
  lessons/
```

少了一层目录，代价是 Store 打开后看到 7 个文件夹。好处是每个 kind 的归属不再需要先回答"我属于 knowledge 还是 state"这个不总有清晰答案的问题。

**`[问题]` `profile/` 单数 vs 其他全部复数。**

`profile/` 是单数，`projects/`、`decisions/`、`procedures/`、`lessons/` 都是复数。

文档里的隐含理由是"概念上只有一个 profile"。但 `profile/` 目录下实际可能有多个文件（`writing-style.md`、`communication.md`、`tools.md`）。它和 `projects/` 下面有多个项目文件没有本质区别。

建议统一成复数，或者如果 profile 确实只是一个文件，那它不需要是目录，直接 `store/profile.md`。

### 13.5 Projections 内部

```
projections/
  claude/
  codex/
  openclaw/
  chatgpt/
```

**`[OK]` 用平台短名做子目录，清晰无歧义。**

唯一可议的是 `claude/` 是不是应该叫 `claude-code/` 以区分 Claude API 等其他产品。但 Phase 1 不需要这个区分。

### 13.6 Projection 文件命名

```
CLAUDE.memory.md
AGENTS.memory.md
MEMORY.md
project-summary.md
```

**`[问题]` 四个文件的命名规则完全不同。**

- `CLAUDE.memory.md` — 遵循平台约定（`CLAUDE.md`）+ 自创后缀（`.memory`）
- `AGENTS.memory.md` — 同上
- `MEMORY.md` — 遵循平台约定
- `project-summary.md` — 自创名

这些名字的设计目标是"最终同步到平台时，名字要匹配平台的发现机制"。所以它们**应该**不一致 — 因为四个平台的约定本来就不同。

但 `CLAUDE.memory.md` 这个名字有一个具体问题：Claude Code 的 `@import` 可以引入任意文件，不要求文件名以 `CLAUDE` 开头。叫 `memory-projection.md` 再被 `CLAUDE.md` import 进去，可能更清楚。`CLAUDE.memory.md` 暗示它自己就是一个 `CLAUDE.md` 变体，但它不会被 Claude Code 自动发现 — 它必须被 import。

### 13.7 Schema 里的命名

```yaml
id: st_profile_writing_style
kind: profile
status: confirmed
origin: manual
```

**`[可议]` `origin` 这个字段名。**

`origin: manual` — origin 通常指"起源地"，但这里它表达的是"创建方式"（人工 vs agent vs 导入）。`created_by` 或 `author_type` 更直接。不过 `origin` 也勉强能读通。

**`[OK]` `kind` 比 `type` 好。**

`type` 在很多语言里是保留字，而且太泛。`kind` 更具体，也是 Kubernetes 等系统的惯例。

### 13.8 动作命名

文档里有两个关键动作：

- `Consolidate` — 从 Capture/Workspace 整理进 Store
- `Project` — 从 Store 生成 Projections

**`[可议]` `Project` 作为动词容易和 `project`（项目）混淆。**

"do a Project" vs "create a project" — 在口头或文字讨论中会产生歧义。候选：`Publish`、`Distribute`、`Emit`、`Sync`。

`Consolidate` 没有这个问题，它足够独特。

### 13.9 总结：命名的根本问题

上面这些问题背后有一个共同原因：

**命名时没有先选定一套一致的隐喻系统。**

如果把整个系统比作图书馆：
- `intake desk` → `workshop` → `stacks` → `lending copies`
- 动作：`catalog`（整理上架）、`circulate`（发出借阅副本）

如果把整个系统比作出版流程：
- `manuscripts` → `editing` → `canon` → `editions`
- 动作：`edit`（整理）、`publish`（发行）

如果比作软件构建：
- `source` → `build` → `artifact` → `deploy`
- 动作：`build`（编译）、`deploy`（部署）

现在的命名是从这几套隐喻里各取了一些词，所以读起来每个词都合理，但放在一起缺少一根线把它们串起来。

这不一定要现在解决。但如果要解决，**应该先选一个隐喻**，然后从它推导出所有名字。

## 14. 一句话总结

一个本地文件型 memory core：Capture 接住输入，Workspace 隔离 agent 产出，Store 只收确认过的长期内容，Projections 把 Store 翻译成四个平台各自的入口文件。Phase 1 全手工，7 个交付物，5 条完成标准。
