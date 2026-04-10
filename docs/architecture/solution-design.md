# Solution Design

更新日期：`2026-04-09`

这篇文档是当前版本的主方案。

它回答 6 个问题：

1. 这个项目要做成什么
2. 之前的方案已经做到哪一步
3. 最近这轮调研带来了什么新输入
4. 整体结构怎么设计
5. 目录和 schema 怎么设计
6. Phase 1 先落什么

## 1. 目标

这个项目要做的是一套：

- `local-first personal memory core for humans and agents`

它要解决的事情有 5 件：

1. 人和 agent 都可以往系统里写内容
2. 原始输入、加工中的内容、长期主库、平台入口要分开
3. 长期有效的知识、决策、流程、偏好、项目状态都能沉淀
4. 平台侧发生的新纠正可以回流
5. 整个系统对人类可读、可改、可审计

所以这个项目的核心循环是：

- `Capture -> Workspace -> Store -> Projections`

配套的两个关键动作是：

- `Consolidate`
- `Project`

## 2. 之前的方案做到哪一步了

前一版方案已经做对了 4 件事：

1. 确定了 `local-first`
2. 确定了平台入口必须是具体文件
3. 确定了 same-day correction 和长期整理不是一回事
4. 确定了长期 memory 不只是 topic knowledge

这些判断现在仍然成立。

但它还不够，主要差在 4 个点：

1. `Store` 还太平，缺少明确的分类模型
2. 没有正式的 `Workspace`，导致 generated / candidate 内容无处安放
3. 路径、frontmatter、视图的分工不清楚
4. Schema 还没有按 Obsidian Properties 的约束收平

## 3. 最近这轮调研带来了什么新输入

### 3.1 Karpathy

Karpathy 这条线给了两个很硬的输入：

1. 原始材料和编译后的知识必须分开
2. query 结果和 agent 产出要能写回

这直接支持了：

- `Capture / Workspace / Store` 的分离
- `source-backed / synthesized` 这条状态轴

### 3.2 Nick Milo

Nick Milo 这条线提醒了一件事：

- 主库必须是人类愿意长期使用的工作台

这要求系统里的关键文件本身就要可浏览、可跳转、可充当入口页。

### 3.3 Eugene / Cole / Huy / Sean

这几条实践共同坐实了 3 个判断：

1. 本地 Markdown 主库完全可行
2. agent 应该围绕真实文件工作
3. 维护成本必须低

这要求我们把目录、schema、projection 文件都设计成真实可用的文件系统，而不是抽象概念。

### 3.4 Obsidian

Obsidian 给出的最重要输入，不是“支持 Markdown”，而是这条组织原则：

- `single home, multiple views`

翻译成我们的设计就是：

1. `Path` 只表达主归属
2. `Properties` 记录正交维度
3. `Links / Bases / Projections` 提供多视图

这正好对应你提的那个问题：

- 同一篇文档既属于 `research / memory`
- 也属于 `ai-os` 项目
- 也是 `codex` 生成的
- 还被你 confirm 过

这些信息不该一起塞进目录。

同时也要再收一步：

- 很多“视图页”不必先抽成独立对象

一个普通的 `memory.md`、`project.md`、`topic.md`，完全可以同时承担：

1. 内容页
2. 入口页
3. 相关链接索引页

## 4. 总体结构

当前主方案保留 4 个结构块：

1. `Capture`
2. `Workspace`
3. `Store`
4. `Projections`

### 4.1 Capture

作用：

- 接住原始输入和回流事件

放什么：

- `daily`
- `inbox`
- imports
- clips
- platform feedback
- same-day correction items

特点：

- 先接住
- 不要求稳定
- 不直接当长期真相源

### 4.2 Workspace

作用：

- 放加工中的内容

放什么：

- candidate synthesis
- generated summary
- task-specific wiki
- review queue
- promote queue

特点：

- 允许脏
- 允许临时
- 允许 agent 大量工作
- 但不能直接当主库

### 4.3 Store

作用：

- 放长期、稳定、可审计的主库

这里是长期 memory 的真相源。

`Store` 里的主要 family 先只保留 3 类：

- `evidence`
- `knowledge`
- `state`

其中：

- `knowledge` 管 research / topic / entity / synthesis
- `state` 管 profile / project / decision / procedure / lesson / review / people / routine

这里要明确一条收敛规则：

- `navigation` 不是单独 family
- `capabilities` 也不是 Phase 1 的单独 family

原因很简单：

1. 很多入口页本来就是普通文件的一种写法
2. `procedure` 已经足够承载 Phase 1 的“可执行经验”
3. 先把主库做平、做稳，比先发明更多对象更重要

### 4.4 Projections

作用：

- 把 `Store` 的稳定内容投影成各平台真正会读的文件

典型对象：

- Claude Code 的 `CLAUDE.md` 相关 projection
- Codex 的 `AGENTS.md` / `AGENTS.override.md` / repo memory slice
- OpenClaw 的 `MEMORY.md`
- ChatGPT 的 summary / export package

注意：

- `Projections` 不是主库
- 它们是面向平台的派生视图

## 5. 分类模型：Path / Properties / Views

这是这次更新里最关键的部分。

### 5.1 Path 只表达主归属

目录只回答一个问题：

- 这份文件本体是什么

例如：

- `store/knowledge/topics/karpathy-llm-wiki.md`

它表达的是：

- 这是 `Store` 里的一个 `knowledge/topic`

目录不要继续编码下面这些信息：

- 它属于哪个项目
- 它属于哪个领域
- 它是谁生成的
- 它有没有被 confirm
- 它会出现在什么视图里

### 5.2 Properties 承载正交维度

上面那些信息都应该进 properties。

例如同一篇文档可以写：

- `project_refs: [ai-os]`
- `domain_refs: [memory, research]`
- `origin_author_id: codex`
- `status: confirmed`
- `confirmed_by: user`

这样文件仍然只有一个 canonical home，但能带多个维度。

### 5.3 Views 提供多入口

同一份内容可以同时出现在：

- `AI OS` 项目视图
- `memory` 主题视图
- `research` 视图
- `confirmed` 视图
- `codex-generated` 视图

这些都不靠复制文件，而靠：

- 文件里的相关链接
- `Bases`
- tags
- projections

一句话收住：

- `one file, one home, many views`

这里再补一条：

- `views` 是呈现方式，不是单独 family

## 6. 目录设计

### 6.1 推荐的仓库级目录

```text
capture/
  inbox/
  daily/
  imports/
  feedback/

workspace/
  candidates/
  ephemeral/
  reviews/
  promote/

store/
  evidence/
    sources/
    clips/
    observations/
    extracts/
  knowledge/
    topics/
    entities/
    syntheses/
    comparisons/
  state/
    profile/
    goals/
    projects/
    decisions/
    procedures/
    lessons/
    reviews/
    people/
    routines/

projections/
  claude/
  codex/
  openclaw/
  chatgpt/

templates/
indexes/
```

### 6.2 各目录的职责

- `capture/`
  放原始输入和回流事件
- `workspace/`
  放 generated / candidate / review 中的内容
- `store/`
  放 confirmed / clean / persistent 的长期主库
- `projections/`
  放面向平台的派生文件
- `templates/`
  放 note templates、projection templates
- `indexes/`
  放派生索引，不当真相源

### 6.3 一个具体例子

Karpathy 方案研究这篇文档，推荐这样落：

- 路径：`store/knowledge/topics/karpathy-llm-wiki.md`

它的其他信息写在 properties 里：

- `project_refs: [ai-os]`
- `domain_refs: [memory, knowledge-compiler]`
- `origin_author_id: codex`
- `status: confirmed`
- `confirmed_by: user`

它可以同时出现在这些 view 里：

- `store/knowledge/topics/memory.md` 里的相关链接
- `store/state/projects/ai-os.md` 里的相关链接
- `Bases` 里的 `origin_author_id = codex`
- `Bases` 里的 `status = confirmed`

也就是说：

- 文件自己就可以兼做索引页
- 不需要先额外造一个 `hub` 或 `MOC`

## 7. Schema

### 7.1 设计原则

Schema 这次要遵守 4 条规则：

1. 公共字段尽量统一
2. Frontmatter 尽量扁平，不用深层嵌套对象
3. 目录不表达的维度，进入 properties
4. `property` 用来做模型，`tag` 用来做视图

之所以强调“扁平”，是因为 Obsidian Properties 和 Bases 对扁平字段更友好。

### 7.2 推荐的公共 frontmatter

```yaml
---
id: kn_karpathy_llm_wiki
family: knowledge
kind: topic
title: Karpathy LLM Wiki
summary: Karpathy 的 LLM Wiki 方案研究笔记。

status: confirmed
cleanliness: clean
persistence: persistent
grounding: source-backed

project_refs:
  - ai-os
domain_refs:
  - memory
  - knowledge-compiler
view_refs:
  - ai-os
  - memory

origin_author_type: agent
origin_author_id: codex
origin_mode: generated

confirmed_by: user
confirmed_at: 2026-04-09

source_refs:
  - https://x.com/karpathy/status/2039805659525644595
  - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

tags:
  - ai-os
  - research
  - knowledge-compiler

created_at: 2026-04-09
updated_at: 2026-04-09
---
```

### 7.3 公共字段分组

身份字段：

- `id`
- `family`
- `kind`
- `title`
- `summary`

治理字段：

- `status`
- `cleanliness`
- `persistence`
- `grounding`

范围字段：

- `project_refs`
- `domain_refs`
- `view_refs`

来源字段：

- `origin_author_type`
- `origin_author_id`
- `origin_mode`
- `source_refs`

确认字段：

- `confirmed_by`
- `confirmed_at`

时间字段：

- `created_at`
- `updated_at`

### 7.4 推荐的公共枚举

`status`

- `candidate`
- `confirmed`
- `superseded`
- `archived`
- `invalid`

`cleanliness`

- `generated`
- `clean`

`persistence`

- `ephemeral`
- `persistent`

`grounding`

- `source-backed`
- `synthesized`
- `mixed`

### 7.5 family-specific 字段

公共字段之外，可以按 family 增加少量专用字段。

例如：

`state/decisions`

- `decision_status: proposed | active | superseded`
- `effective_from`
- `supersedes`

`state/projects`

- `project_status: active | paused | done | archived`

原则是：

- 公共字段保持稳定
- 专用字段少而清楚

## 8. Property 和 Tag 的分工

这部分需要写死，不然后面会越用越乱。

适合做 property 的：

- `family`
- `kind`
- `status`
- `project_refs`
- `origin_author_id`
- `confirmed_by`

适合做 tag 的：

- `#research`
- `#ai-os`
- `#memory`
- `#generated`

规则：

1. 决定系统行为和治理的字段，必须是 property
2. 只用于轻量筛选和浏览的，才用 tag
3. 不要把 `confirmed`、`origin`、`project` 这种关键语义只放在 tag 上

## 9. 数据流

### 9.1 标准路径

1. 新输入先进入 `Capture`
2. agent 或人类在 `Workspace` 里整理、总结、合并
3. review 后 promote 到 `Store`
4. 从 `Store` 刷新 `Projections`
5. 平台通过各自正式入口消费 projection

### 9.2 平台回流

1. 平台侧确认的新纠正先回到 `Capture`
2. 需要当天生效时，可以先做小范围 projection patch
3. 晚些时候再进 `Workspace`
4. review 后 promote 到 `Store`
5. 再统一重建 projection

### 9.3 一个具体例子

你今天在 Claude Code 里确认了一条规则：

- 文档每节保留 1 个例子

落地顺序应该是：

1. 先记到 `capture/feedback/`
2. 需要当天生效时，先更新 Claude projection
3. 晚些时候整理成 `store/state/profile/user-writing-preferences.md`
4. 再同步回 Claude / Codex / OpenClaw 的 projection

## 10. 关键设计决策

1. 外层结构保留 `Capture / Workspace / Store / Projections`
2. `Store` Phase 1 只保留 `evidence / knowledge / state`
3. `Path` 只表达主归属
4. `Properties` 记录正交维度
5. 普通文件自己就可以兼做索引页
6. `projection` 是平台视图，不是真相源
7. generated / candidate 内容必须先过 `Workspace`
8. `procedure` 是 Phase 1 的最小 capability

## 11. 关键原则

1. 外层结构保持简单，复杂度放进 schema 和 review gate
2. Path 只表达主归属
3. Properties 承载正交维度
4. Views 和 projections 提供多入口
5. Store 只收 confirmed / clean / persistent 的内容
6. Workspace 必须存在，不能让 generated 内容直接冲主库
7. projection 是平台视图，不是真相源
8. source traceability 要前置
9. 人和 agent 必须共用主库，但不共用所有工作区

## 12. Phase 1 边界

Phase 1 先落下面这些：

1. `Capture / Workspace / Store / Projections` 目录骨架
2. 扁平的公共 frontmatter schema
3. `Path / Properties / Views` 这套分类规则
4. Obsidian-compatible 的 templates、普通文件索引写法、Bases 视图约定
5. Claude Code / Codex local / OpenClaw 的 projection 形态
6. ChatGPT export-only 方案
7. review-gated promotion 规则

Phase 1 不先做这些：

- vector-first retrieval
- graph-first storage
- 自动 skill synthesis
- 复杂 Web UI
- 普通 ChatGPT 自动读取本地主库

## 13. 一句话总结

新版方案可以压成一句话：

- `一个本地文件型 memory core，前面接 Capture，后面接 Projections，中间用 Workspace 做 review-gated promotion；Store 先只保留 evidence / knowledge / state，普通文件自己就可以兼做索引页。`
