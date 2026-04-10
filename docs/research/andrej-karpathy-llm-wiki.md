# Andrej Karpathy 的 LLM Wiki 调研

更新日期：`2026-04-09`

这篇文档只分析公开能确认的部分：

- `Andrej Karpathy` 最近公开的 `LLM Wiki / LLM Knowledge Bases` 方案，到底是什么
- 它的层级、数据流和关键设计点是什么
- 哪些是他自己明确写出来的，哪些只是合理推断

主源：

- <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

补充材料：

- <https://deepakness.com/raw/llm-knowledge-bases/>
- <https://academy.dair.ai/blog/llm-knowledge-bases-karpathy>

## 1. 一句话结论

Karpathy 这套东西，本质上不是一个 `memory system`，也不是一个 `RAG stack`。

它更像一个：

- `LLM-driven knowledge compiler`

也就是：

1. 人先收集原始材料
2. LLM 把原始材料增量整理成 wiki
3. 之后问问题时，主要对 wiki 提问，不是每次都回到 raw 文件里重新检索
4. 查询结果还能继续写回 wiki

所以它的核心不是 `retrieve`，而是 `compile`。

## 2. 已确认的核心结构

Karpathy 在 gist 里把结构直接写成了三层：

1. `Raw sources`
2. `The wiki`
3. `The schema`

### 2.1 Raw sources

这是原始资料层。

Karpathy 明确说：

- 这里放文章、论文、图片、数据文件等
- 这些文件是 `immutable`
- LLM 只读，不改
- 这是 `source of truth`

这说明他把“原始证据”和“编译后的知识”严格分开了。

### 2.2 The wiki

这是编译后的知识层。

Karpathy 明确说：

- 它是一个 markdown 文件目录
- 里面有 summaries、entity pages、concept pages、comparisons、overview、synthesis
- LLM 负责创建、更新、交叉链接、保持一致性
- 人主要读取它，很少直接写它

关键点是：

- `wiki` 不是原始材料库
- `wiki` 是一层持久化的知识产物
- 它会随着 ingest、query、lint 持续更新

### 2.3 The schema

这是控制层。

他明确说：

- schema 是一个文档
- 例如 `CLAUDE.md` 或 `AGENTS.md`
- 它告诉 LLM：wiki 怎么组织、有哪些约定、ingest/query/maintain 应该怎么做

这层本质上是：

- `wiki compiler spec`

## 3. 它真正的数据流

这套方案不能简单看成：

- `raw -> wiki -> answer`

真正的数据流至少有四段。

### 3.1 Ingest flow

第一段是写入原始资料：

- 人把文章、论文、repo、图片放进 `raw/`
- 然后让 LLM 处理这份 source

Karpathy 给了很具体的 ingest 动作：

1. 读 source
2. 跟人讨论关键点
3. 写 summary page
4. 更新 index
5. 更新相关 entity / concept pages
6. append 一条 log

他还说，一个 source 可能会改动 `10-15` 个 wiki 页面。

### 3.2 Compile flow

第二段是编译流。

这不是单独一次大 batch，而是增量编译：

- 新 source 进来
- LLM 不是只给它做单独摘要
- 而是把它并入现有 wiki
- 同时更新旧页面里的说法、交叉引用和整体综合判断

所以它更像：

- `incremental compilation`

### 3.3 Query flow

第三段是查询流。

Karpathy 明确写了：

- 查询时先读 `index.md`
- 再钻到相关页面
- 再综合答案
- 最终答案可以是 markdown、表格、Marp 幻灯片、matplotlib 图、canvas

这里有两个关键点：

- 查询的主要对象已经不是 raw source，而是 wiki
- query 结果可以回写 wiki

这说明 query 不是纯消费，也是在继续生产知识。

### 3.4 Maintenance flow

第四段是维护流，也就是他所谓的 `lint` 或 `health check`。

Karpathy 明确写了 lint 要看这些东西：

- 页面之间的矛盾
- 被新 source 取代的旧说法
- 没有入链的 orphan pages
- 被提到但还没有独立页面的重要概念
- 缺失的 cross-reference
- 可以用 web search 补上的数据缺口

这说明维护流本质上是：

- `knowledge quality control`

## 4. 两个特殊文件：index 和 log

### 4.1 index.md

这是内容导航文件。

他明确说：

- 它列出 wiki 里所有页面
- 每页有链接
- 每页有一行摘要
- 查询时 LLM 先读 index，再决定深入哪些页面

这个设计说明：

- 他的“检索”优先靠显式结构化索引，不优先靠 embedding

### 4.2 log.md

这是时间线文件。

他明确说：

- log 是 append-only
- 记录 ingest、query、lint 发生了什么
- 通过统一前缀，可以直接用 unix 工具做简单分析

所以：

- `index` 管内容地图
- `log` 管时间顺序

## 5. 它的层级到底是什么

如果压缩成最本质的层级，这套方案可以理解成：

1. `Evidence`
2. `Compiled knowledge`
3. `Operating spec`

对应原文：

- `Evidence` = `Raw sources`
- `Compiled knowledge` = `The wiki`
- `Operating spec` = `The schema`

## 6. 这套方案最关键的设计点

### 6.1 把 LLM 从 retriever 变成 compiler

普通 RAG 是 query time 才去找材料。

Karpathy 的重点是：

- 平时先把材料编译成结构化知识

### 6.2 把知识维护从人转给 LLM

人主要负责：

- 找 source
- 提问题
- 做判断

LLM 主要负责：

- 摘要
- 归档
- 交叉引用
- 页面更新
- bookkeeping

### 6.3 让每次 query 都能沉淀

很多系统的 query 只是一次性消费。

Karpathy 明确把 query 输出再写回 wiki。

这意味着：

- 知识库不只吃 source
- 还吃 exploration

### 6.4 用显式结构代替隐式 embedding

在个人规模下，他优先依赖：

- index
- 页面链接
- summary
- category

embedding 搜索在他那里是可选增强，不是基础层。

### 6.5 用 lint 把 wiki 当成可维护系统

很多知识库项目只做 ingest 和 query，不做 maintenance。

Karpathy 明确把 lint 独立出来，说明他把 wiki 看成持续演化的系统。

### 6.6 把 Obsidian 当 IDE，不当后端

Karpathy 明确写了：

- `Obsidian is the IDE`

这句话很关键。

Obsidian 在他这里的角色是：

- 浏览
- graph view
- 看文件
- 看 slide 和图表

不是数据库，也不是 agent runtime。

## 7. 它擅长什么，不擅长什么

### 7.1 它擅长的

- 长期研究型主题
- 会不断积累 source 的问题
- 需要跨多文档综合判断的问题
- 希望把问答结果继续沉淀下来的场景

### 7.2 它不擅长的

- 高频、强实时更新的数据面
- 超大规模开放语料
- 完全不做人工选择的全自动摄入
- 需要严格事务一致性的业务系统

### 7.3 它目前没有重点解决的

从 Karpathy 自己的 gist 看，这套方案没有重点解决：

- 多平台同步
- 权限体系
- 删除与 retention policy
- 多用户协作冲突
- 强结构化数据库写入
- same-day correction 这类“行为约束立刻生效”的 agent memory 问题

所以这更像：

- `knowledge system`

而不是完整的：

- `personal operating memory system`

## 8. 对我们这个项目的启发

### 8.1 Phase 1 应该尽量学他的 compile 思路

也就是：

- 先把 `Capture -> Store` 做成 compile，不是简单 append

### 8.2 Store 里应当有 index / log 这类显式导航层

即便后面接 BM25、vector、graph，也不该跳过显式 index。

### 8.3 schema 不能省

我们现在说的 `AGENTS.md / CLAUDE.md / projection rules`，本质上就是我们的 schema 层。

### 8.4 他的方案解决的是 knowledge compilation，不是全部 memory

他的系统里最强的是：

- `raw -> wiki -> query -> lint`

而我们这个项目还要继续解决：

- `profile`
- `decision`
- `procedure`
- `platform projection`
- `same-day correction`

所以更准确地说：

- Karpathy 的方案是我们 `Store` 里 `topic / research` 这部分的直接参考
- 它不是我们整个系统的完整替代品

## 9. 已确认和推断的边界

### 9.1 已确认

这些是 Karpathy 自己在 gist 里明确写了的：

- 三层：`raw sources / wiki / schema`
- 三类操作：`ingest / query / lint`
- 两个特殊文件：`index.md / log.md`
- raw immutable
- wiki 由 LLM 维护
- schema 可用 `CLAUDE.md` 或 `AGENTS.md`
- query 输出可以回写 wiki
- Obsidian 是 IDE
- 可选接 search CLI / MCP

### 9.2 补充确认

这些点来自更早公开帖的转述，多处来源一致：

- 他用 `Obsidian Web Clipper` 做一部分网页摄入
- 图片会本地下载
- 原始内容先统一进 `raw/`

### 9.3 推断

下面这些，在现有公开材料里没有被他完整写死，所以只能当推断：

- wiki 的精确目录树
- frontmatter schema
- 单 source ingest 的具体 prompt
- lint 的调度方式
- 是否有多 agent 协作
- 是否有专门的增量 diff / patch 机制

这些点不能写成“他就是这么做的”。

## 10. 参考来源

- Karpathy gist: <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>
- DeepakNess 对早期公开帖的转述: <https://deepakness.com/raw/llm-knowledge-bases/>
- DAIR.AI 的结构化拆解: <https://academy.dair.ai/blog/llm-knowledge-bases-karpathy>
