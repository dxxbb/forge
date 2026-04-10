# Personal AI OS / Life OS / Second Brain 实践者综述

更新日期：`2026-04-09`

这篇文档不看公司叙事，只看个人实践者。

重点回答 4 个问题：

1. 这些人在解决什么问题
2. 他们的数据流是什么
3. 他们之间有什么本质差异
4. 对我们这个项目有什么输入

这里说的“个人实践者”，不要求每个人都真的说过 `AI OS` 这个词。

更重要的是：

- 他是不是在用一套长期、可持续的个人工作流
- 让 AI、知识库、项目推进、行动或记忆形成闭环

## 1. 一句话结论

最近这批值得看的个人实践者，大致可以分成三类：

1. `knowledge compiler`
2. `agent + vault workflow`
3. `life management OS`

如果再压缩一点：

- `Karpathy` 代表“把知识编译成 wiki”
- `Nick Milo` 代表“把知识组织成可思考环境”
- `Eugene / Cole / Huy / Sean` 代表“让 agent 在本地 vault 上持续工作”
- `Akshay Hallur` 代表“把人生管理做成 operating system”

这几类都跟你的项目有关，但不是同一层。

## 2. 实践者清单

### 2.1 Andrej Karpathy

代表关键词：

- `LLM Wiki`
- `LLM Knowledge Bases`
- `knowledge compiler`

公开材料：

- <https://x.com/karpathy/status/2039805659525644595>
- <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

他解决的问题：

- 原始材料越来越多
- query-time 临时检索太碎
- AI 每次都像第一次看到这些内容

他的数据流：

- `raw sources -> wiki -> query -> write back -> lint`

他的核心价值：

- 让 LLM 从“答题器”变成“长期知识维护者”

他对你项目的输入：

- `compile` 比 `append` 更重要
- `index / log / schema` 要前置
- `research KB` 可以先独立成型

不是他重点解决的：

- 偏好、决策、行为约束
- 多平台 projection
- same-day correction

一句话定位：

- `knowledge compiler`

### 2.2 Nick Milo

代表关键词：

- `Linking Your Thinking`
- `MOCs`
- `thinking environment`

公开材料：

- <https://www.linkingyourthinking.com/>
- <https://www.youtube.com/@linkingyourthinking>
- <https://www.youtube.com/watch?v=qo4YZvC1q5I>

他解决的问题：

- 知识怎么组织成可思考、可创作、可推进项目的结构

他的数据流更像：

- `capture notes -> connect notes -> build MOCs -> grow ideas -> support projects`

他的核心价值：

- 强调“知识库不是仓库，而是工作台”

他对你项目的输入：

- `Store` 里不能只有原子节点
- 还要有 `hub / MOC / navigation page` 这类中间层
- 人类可读、可改、可逛的结构不能被 agent 优化完全吞掉

不是他重点解决的：

- agent 自动回流
- 多平台消费
- 稳定 memory governance

一句话定位：

- `knowledge gardener / thinking environment designer`

### 2.3 Eugene Vyborov

代表关键词：

- `Claude Code + Obsidian`
- `AI second brain`
- `automation workflow`

公开材料：

- <https://www.youtube.com/watch?v=Jsh_XbUynx0>

他解决的问题：

- 本地知识库怎么真的接上 agent
- 如何让第二大脑不是摆设，而是可运行 workflow

他的数据流大致是：

- `capture -> Obsidian vault -> agent organize/search/synthesize -> output back to vault`

他的核心价值：

- 把“vault + agent”从概念推到工程实现

他对你项目的输入：

- 本地文件型 KB 完全可以作为 agent 工作面
- Obsidian 很适合作为人类前端
- 自动组织、搜索、生成必须围绕真实文件来做

一句话定位：

- `agent-driven local second brain`

### 2.4 Cole Medin

代表关键词：

- `Claude Code`
- `Obsidian`
- `skills`

公开材料：

- <https://lilys.ai/notes/en/claude-code-20260127/second-brain-claude-obsidian-skills>

他解决的问题：

- 个人知识和 agent skill 怎么结合

他的数据流大致是：

- `capture -> vault -> agent uses vault + skills -> structured outputs -> write back`

他的核心价值：

- 把知识库从“查询对象”往“行为能力底座”推进了一步

他对你项目的输入：

- `lesson -> skill / procedure` 这条路是成立的
- KB 不只服务问答，也服务 agent 能力演化

一句话定位：

- `knowledge + skills workflow`

### 2.5 Huy Tieu

代表关键词：

- `Claude + Obsidian + Git`
- `COG`
- `self-organizing second brain`

公开材料：

- <https://dev.to/huy_tieu/i-finally-built-a-second-brain-that-i-actually-use-6th-attempt-4075>

他解决的问题：

- 为什么大多数 second brain 都坚持不下来

他的数据流非常实用：

- `dump messy thoughts -> AI organizes -> plain markdown stays inspectable -> keep using`

他的核心价值：

- 把“长期能不能真的用下去”当成第一约束

他对你项目的输入：

- 维护成本必须低
- plain markdown + git 的可审计性很关键
- 系统设计不能过度依赖复杂手工整理

一句话定位：

- `pragmatic self-organizing second brain`

### 2.6 Sean O'Kana

代表关键词：

- `Cursor + Obsidian`
- `personal AI agent workflow`

公开材料：

- <https://www.youtube.com/watch?v=AQtTJXOi7a8>

他解决的问题：

- 本地 agent 怎么围绕个人 vault 连续工作

他的数据流大致是：

- `local notes -> agent context -> synthesis / planning / content work -> back into notes`

他的核心价值：

- 说明“本地文件 + coding agent”已经可以构成 early-stage personal AI OS

他对你项目的输入：

- repo / vault / agent 三者的边界要清晰
- 工具入口比抽象概念更重要

一句话定位：

- `local agent workflow`

### 2.7 Akshay Hallur

代表关键词：

- `Life OS`
- `CoreOS`
- `Notion`

公开材料：

- <https://www.youtube.com/watch?v=V9gE_6JfWoM>

他解决的问题：

- 如何把任务、项目、目标、习惯、知识、人生领域统一到一个个人系统里

他的数据流更像：

- `life areas -> goals -> projects -> tasks -> reviews -> knowledge`

他的核心价值：

- 把 `review cadence`、`life areas`、`people`、`goals` 这些 operating state 讲清楚了

他对你项目的输入：

- 你的系统不能只有知识层
- 还要有 `project / goal / review / people / routine` 这些操作层对象

不是他重点解决的：

- agent-native memory
- 自动治理
- 多平台 projection

一句话定位：

- `life management operating system`

## 3. 这些人的本质差异

### 3.1 Karpathy 和 Nick Milo 的差异

- `Karpathy` 重点是编译和维护
- `Nick Milo` 重点是组织和思考

前者更像：

- machine-maintained system

后者更像：

- human-thinking environment

### 3.2 Eugene / Cole / Huy / Sean 的共同点

这几个人虽然表达不同，但都指向一件事：

- `vault` 不该只是资料仓库
- 它应该是 agent 真正工作的本地表面

他们比纯 PKM 实践者更接近你的项目。

### 3.3 Akshay 这一类的作用

这类人不一定在做 AI memory，但他们把“人生操作层”讲得更完整：

- tasks
- goals
- reviews
- habits
- people
- life areas

这部分正好补你项目里容易缺的：

- `operational state`

## 4. 哪些最值得吸收到你的项目里

### 4.1 来自 Karpathy

- `compile`
- `index`
- `log`
- `schema`
- `write-back`

### 4.2 来自 Nick Milo

- `MOC / hub / navigation`
- 知识库作为工作台
- 人类浏览体验必须成立

### 4.3 来自 Eugene / Cole / Huy / Sean

- 本地文件是可行底座
- agent 应围绕真实文件工作
- 自动整理必须可审计
- `lesson -> procedure -> skill` 这条线是有现实感的

### 4.4 来自 Akshay

- `goal / project / review / people / routine` 这些对象不能缺

## 5. 对你项目的直接结论

如果把这些实践者放在一起看，我觉得你这个项目最合理的结构还是：

1. `Capture`
2. `Store`
3. `Projections`

但 `Store` 里面不能只有一种东西。

它至少要同时容纳两类内容：

- `research / topic knowledge`
- `operational state`

更具体一点：

- `Karpathy` 告诉你怎么做 `research KB`
- `Nick Milo` 告诉你怎么让 `Store` 真能被人类使用
- `Eugene / Cole / Huy / Sean` 告诉你怎么让 agent 在这套东西上长期工作
- `Akshay` 告诉你 operating layer 里还该有什么对象

所以这批人合起来给你的输入，不是“选一个抄”，而是：

- `Karpathy + Nick Milo + local agent workflow + life review model`

## 6. 对我们项目的输入矩阵

这一节只回答一个问题：

- 这些人各自到底给我们这个项目什么输入

不再泛泛地说“有启发”，而是明确成：

- 哪些该吸收
- 哪些要改造后吸收
- 哪些不该直接照搬

### 6.1 Karpathy：给我们 `research KB compiler`

最直接的输入：

- `Capture -> Store` 不能只是堆笔记，必须有 `compile`
- `index / log / schema` 应该是一等公民
- `query -> write back` 这条闭环值得保留
- `lint / health check` 不能晚到最后才做

落到我们项目里，最适合进入这些位置：

- `Store/topics`
- `Store/research`
- `Consolidate`
- `Project` 前的质量检查

不该直接照搬的部分：

- 不要把整个系统都当成 `wiki`
- 不要假设 `topic knowledge` 就覆盖 `decision / profile / procedure`

一句话：

- Karpathy 给我们的是 `knowledge compiler`，不是整个 `personal memory OS`

### 6.2 Nick Milo：给我们 `human-facing Store`

最直接的输入：

- `Store` 里不能只有原子 note
- 必须有 `MOC / hub / navigation page`
- 人类浏览路径要清楚，不然知识再多也不成系统
- 知识不只是存下来，还要能长成项目和产出

落到我们项目里，最适合进入这些位置：

- `Store/topics`
- `Store/projects`
- `Store/navigation`

我建议后续可以显式加一种节点：

- `hub`

作用是：

- 给人类和 agent 提供同一个可导航入口

不该直接照搬的部分：

- 不要把系统重心放成“手工连接一切”
- 我们仍然要保留 agent 自动整理和回流

一句话：

- Nick Milo 给我们的是 `Store 的人类可用性`

### 6.3 Eugene Vyborov：给我们 `vault-first agent workflow`

最直接的输入：

- agent 应该围绕真实文件工作，而不是围绕抽象数据库工作
- Obsidian-compatible vault 完全可以作为主工作面
- 自动整理、搜索、生成，都应该落回文件

落到我们项目里，最适合进入这些位置：

- `Store`
- `Projections`
- `Obsidian frontend`

他给我们的实际架构启发是：

- `Store` 应该优先设计成文件系统真相源
- `Projections` 要能直接落进 agent 真会读的入口文件

不该直接照搬的部分：

- 不要把“能接上 Claude Code”误当成系统已经完成
- 我们还要继续做治理、回流和平台差异

一句话：

- Eugene 给我们的是 `本地文件型主库真的能跑起来`

### 6.4 Cole Medin：给我们 `lesson -> skill`

最直接的输入：

- 知识库不只服务查询，也服务 agent 能力演化
- `lesson -> procedure -> skill` 这条链是成立的
- 个人知识和 agent skill 不应该分成两个完全孤立系统

落到我们项目里，最适合进入这些位置：

- `Store/lessons`
- `Store/procedures`
- 后续的 `skills` 层

这对 roadmap 的直接含义是：

- `Evolve` 不能停留在抽象概念
- 它最后要落到 `procedure` 和 `skill`

不该直接照搬的部分：

- 不要过早把系统做成 skill factory
- 先把 `lesson` 和 `procedure` 变稳，再谈 skill synthesis

一句话：

- Cole 给我们的是 `Evolve` 这条线的现实感

### 6.5 Huy Tieu：给我们 `长期能用下去的约束`

最直接的输入：

- 维护成本必须很低
- markdown + git 的可审计性很值钱
- 系统如果要求太多手工整理，最后一定废

落到我们项目里，最适合进入这些位置：

- `Capture`
- `Consolidate`
- `governance`

这对设计的直接要求是：

- `Capture` 必须足够低摩擦
- `Consolidate` 必须能明显减少人的维护负担
- 任何高级结构都不能靠大量手工 upkeep 才成立

不该直接照搬的部分：

- 不要把“简单”理解成“没有结构”
- 我们仍然需要显式状态和平台投影

一句话：

- Huy 给我们的是 `可持续使用` 这个硬约束

### 6.6 Sean O'Kana：给我们 `repo / vault / agent boundary`

最直接的输入：

- 本地 agent 已经足够强，可以持续围绕个人文件工作
- 真正重要的是工具入口和边界，不是抽象名词

落到我们项目里，最适合进入这些位置：

- `Projections`
- `Codex / Claude Code / Cursor` 这类平台入口

这对我们项目的直接要求是：

- `AGENTS.md`
- `CLAUDE.md`
- `MEMORY.md`

这些入口文件必须作为一等对象被设计，而不是临时导出一下

一句话：

- Sean 给我们的是 `平台接入必须很具体`

### 6.7 Akshay Hallur：给我们 `operational state`

最直接的输入：

- 个人系统不能只有知识条目
- 还要有：
  - `goals`
  - `projects`
  - `reviews`
  - `people`
  - `routines`
  - `life areas`

落到我们项目里，最适合进入这些位置：

- `Store/profile`
- `Store/projects`
- `Store/reviews`
- `Store/people`

这对我们项目最重要的提醒是：

- 你的系统不能只做 `knowledge memory`
- 还要做 `operational memory`

不该直接照搬的部分：

- 不要把 Notion life dashboard 直接当成 memory architecture
- 那条线更偏操作层，不够覆盖 agent memory 问题

一句话：

- Akshay 给我们的是 `operational state object model`

## 7. 优先级排序

如果只从“对我们项目的实际输入”来排优先级，我现在会这样排：

### 第一层：应该直接吸收

- `Karpathy`
- `Nick Milo`
- `Huy Tieu`

原因：

- 分别补 `compile`
- `human-facing structure`
- `sustainability`

### 第二层：应该作为实现参考

- `Eugene Vyborov`
- `Sean O'Kana`

原因：

- 他们更像“怎么把系统接到本地 agent 上”

### 第三层：应该作为后续演化参考

- `Cole Medin`
- `Akshay Hallur`

原因：

- 一个补 `Evolve`
- 一个补 `operational state`

## 8. 对我们项目的最终收束

如果把这些输入最终压成几条明确要求，我觉得你这个项目至少应该做到：

1. `Store` 既能被 agent 用，也能被人类逛
2. `Store` 里既有 `topic knowledge`，也有 `operational state`
3. `Consolidate` 是 compile，不是 append
4. `Projections` 是一等对象，不是附属导出
5. `Evolve` 最后要落到 `procedure / skill`
6. `governance` 必须前置，至少要有 clean/generated、confirmed/candidate、source-backed/synthesized 这些状态

## 6. 一个简短总结

如果压成一句话：

- `Karpathy` 解决知识编译
- `Nick Milo` 解决知识组织
- `Eugene / Cole / Huy / Sean` 解决 agent 如何真正工作在这套知识上
- `Akshay` 解决人生操作层的对象和 review 节奏

这几类东西合起来，才比较接近你在找的：

- `personal AI OS / life OS / personal operating memory system`

## 9. 参考链接

- Karpathy: <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>
- Nick Milo: <https://www.linkingyourthinking.com/>
- Nick Milo YouTube: <https://www.youtube.com/@linkingyourthinking>
- Tiago x Nick Milo: <https://www.youtube.com/watch?v=qo4YZvC1q5I>
- Eugene Vyborov: <https://www.youtube.com/watch?v=Jsh_XbUynx0>
- Cole Medin: <https://lilys.ai/notes/en/claude-code-20260127/second-brain-claude-obsidian-skills>
- Huy Tieu: <https://dev.to/huy_tieu/i-finally-built-a-second-brain-that-i-actually-use-6th-attempt-4075>
- Sean O'Kana: <https://www.youtube.com/watch?v=AQtTJXOi7a8>
- Akshay Hallur: <https://www.youtube.com/watch?v=V9gE_6JfWoM>
