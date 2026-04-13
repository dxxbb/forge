# Reframed Architecture

补充说明：

- 如果只看一篇当前主方案，请优先看：
- [personal-os-design.md](personal-os-design.md) (当前主方案)
- [solution-design-v2.md](solution-design-v2.md) (memory 子系统 Phase 1)

更新日期：`2026-04-09`

这篇文档不重复讲现有架构，而是回答 4 个更关键的问题：

1. 之前的方案已经做到什么程度
2. 今天这批调研带来了什么新输入
3. 基于这些输入，整个项目的架构应该怎样重设计
4. 新版本最关键的原则是什么

## 1. 之前的方案做到什么程度

先说结论：

- 之前的方案在外层结构上已经是对的
- 但在内部语义和治理上还不够

### 1.1 之前方案已经做对的部分

前一版最大的贡献，不是 node type 多不多，而是把几个硬边界先钉住了：

1. `local-first`
   主库必须是本地、可编辑、可审计的文件系统

2. `Capture / Store / Projections`
   至少把“输入”“主库”“平台入口”分开了

3. `平台入口是具体文件，不是抽象上下文`
   `CLAUDE.md`、`AGENTS.md`、`MEMORY.md`、ChatGPT summary 这些入口都已经明确了

4. `same-day correction`
   已经意识到“当天纠正当天生效”和“长期知识整理”不是一回事

5. `ChatGPT 不能假装自动同步`
   已经把平台能力差异写死了

这些判断现在看仍然成立。

### 1.2 之前方案不够的地方

问题主要有 5 个。

#### 1. `Store` 还是太平

虽然上一版已经有：

- `profile`
- `project`
- `decision`
- `topic`
- `procedure`
- `lesson`

但这个 `Store` 仍然像一个“typed note box”，还不是一个更强的 operating memory system。

它少了几个关键区分：

- `evidence` 和 `knowledge` 没明确分开
- `confirmed` 和 `candidate` 没明确分开
- `human-facing navigation` 没成为一等对象
- `operational state` 还不够完整

#### 2. `write-back` 讲到了，但 promotion gate 还不够硬

前一版已经有回流概念，但还没明确：

- 什么能直接进干净主库
- 什么只能先停在 generated / candidate 区
- 什么需要人工确认后才能 promote

这会导致一个风险：

- agent 产生的新内容会慢慢污染主库

#### 3. `research KB` 和 `operational memory` 还没真正拆清

前一版已经把 `profile / decision / procedure` 放进来了，这是对的。

但今天的调研说明：

- `topic knowledge`
- `goal / review / people / routine / project state`

这两类东西虽然都在 `Store` 里，但它们不是同一种对象。

#### 4. 人类使用路径还不够强

上一版已经知道 Obsidian 是前端，但还没有把：

- `hub`
- `MOC`
- `navigation page`

做成正式节点。

这会带来一个后果：

- agent 可能能用
- 但人类自己不一定愿意长时间在里面工作

#### 5. 缺少 `ephemeral workspace`

今天的调研提醒了一个很重要的问题：

- 不是所有合成都应该直接写进长期 KB

有些复杂任务需要：

- 临时工作区
- 临时 wiki
- 临时 synthesis

这部分在前一版里几乎没有位置。

## 2. 今天的调研带来了什么新输入

今天的输入，不是多了几个人名，而是把我们之前模糊感受到的几个方向坐实了。

### 2.1 Karpathy：`Store` 里的 research 部分应该是 compile，不是 append

Karpathy 给的不是“再做一个 wiki”，而是两条很硬的输入：

1. `knowledge` 不是原始材料堆
2. `query` 不是终点，应该继续写回

对我们项目的真正输入是：

- `research / topic knowledge` 这部分，应该按 `knowledge compiler` 来设计

### 2.2 Nick Milo：`Store` 必须是工作台，不是仓库

Nick Milo 最关键的输入不是 MOC 这个词，而是：

- `Store` 要能被人类长期逛、改、思考、推进项目

这意味着：

- `hub / MOC / navigation page` 必须成为正式节点

### 2.3 Eugene / Cole / Huy / Sean：本地文件型主库完全可行，但要围绕真实工作面

这几个人共同坐实了三件事：

1. 本地文件完全能作为 agent 的长期工作面
2. 真正重要的是 agent 入口和文件落点
3. 维护成本不能太高，否则系统会废

对我们项目的输入是：

- `Store` 和 `Projections` 都要围绕真实文件来做
- `governance` 和 `usability` 必须和自动化一起设计

### 2.4 Akshay：`operational state` 不能再被当成附属信息

Akshay 这条线最重要的提醒是：

- 个人系统不只有知识条目

还要有：

- `goals`
- `projects`
- `reviews`
- `people`
- `routines`
- `life areas`

对我们来说，这意味着：

- `Store` 必须明确分出 `operational state`

### 2.5 Karpathy thread：真正先炸的是治理，不是规模

今天 thread 调研里最重要的不是“大家喜欢不喜欢”。

真正有输入的是这几个社区共识或强争议点：

1. `clean vs generated` 必须分开
2. `write-back` 很重要，但不该默认无门槛自动写回
3. `persistent KB` 和 `ephemeral KB` 应该分开
4. 跨设备 / 跨平台同步是核心能力，不是附属功能

这几个点，直接改变了我们应该怎么设计 `Store` 和 `Projections`。

## 3. 基于今天调研，应该怎么重设计

我的判断是：

- 外层结构不用推翻
- 还是保留 `Capture / Store / Projections`
- 真正要重做的是 `Store` 的内部模型，以及围绕它的 promotion / projection / review 逻辑

所以新版本不是“换三层”，而是：

- `三块外壳不变，内部语义重做`

## 4. 新版本的总图

### 4.1 外层结构仍然是三块

1. `Capture`
2. `Store`
3. `Projections`

### 4.2 但 `Store` 不再是一个平面盒子

`Store` 应该明确包含 5 类正式对象：

1. `Evidence`
2. `Knowledge`
3. `Operational State`
4. `Navigation`
5. `Capabilities`

这里的意思不是再加 5 层架构，而是：

- `Store` 里面至少要有这 5 类 node family

### 4.3 五类 node family

#### A. `Evidence`

作用：

- 保留原始来源
- 支撑追溯和重编译

典型对象：

- source note
- clipped article
- paper note
- raw observation
- conversation extract

这类对象的特点：

- 更接近原始证据
- 不等于最终知识结论

#### B. `Knowledge`

作用：

- 存稳定的 topic / entity / synthesis

典型对象：

- topic
- entity
- comparison
- synthesis

这部分最接近 Karpathy 的 wiki。

#### C. `Operational State`

作用：

- 存当前有效、会影响后续行为的状态

典型对象：

- profile
- goals
- projects
- decisions
- procedures
- lessons
- reviews
- people
- routines

这是前一版最应该补强的地方。

#### D. `Navigation`

作用：

- 给人类和 agent 都提供更稳定的入口

典型对象：

- hub
- MOC
- dashboard
- review page

这部分主要来自 Nick Milo 的输入。

#### E. `Capabilities`

作用：

- 把稳定经验升级成可复用动作

典型对象：

- procedure
- checklist
- skill spec
- command template

这里面：

- `procedure` 应该在 Phase 1/2 就落地
- `skill` 可以晚一点

## 5. 新版本最重要的不是 node 更多，而是状态更清楚

真正关键的不是再发明更多 note type，而是让每条内容都有更明确的状态。

至少要有这几条轴：

### 5.1 `confirmed / candidate`

- `confirmed`：已经进入干净主库
- `candidate`：还没完成 review，只能先停在工作区

### 5.2 `source-backed / synthesized`

- `source-backed`：能追到明确 source
- `synthesized`：已经是抽象、综合或规则化的结果

### 5.3 `clean / generated`

- `clean`：长期可信资产
- `generated`：agent 生成、临时整理或待确认内容

### 5.4 `persistent / ephemeral`

- `persistent`：长期留在主库
- `ephemeral`：围绕某个任务临时建立，任务结束后归档或提炼

这些状态轴，比再多加几个目录更重要。

## 6. 新版数据流应该怎样跑

这次架构重做后，整条流我建议写成 6 步。

### 6.1 Capture

先接住输入：

- 聊天
- 笔记
- 网页
- 论文
- 平台回流
- 同天纠正

### 6.2 Compile to candidate

新信息不要直接进 clean store。

先做：

- 提取
- 归类
- 关联
- 初步 synthesis

输出到：

- `candidate`
- 或 `ephemeral workspace`

### 6.3 Review and promote

这是新版本最关键的 gate。

只有通过 review 的内容，才进入：

- `Knowledge`
- `Operational State`
- `Navigation`
- `Capabilities`

### 6.4 Project

从 `clean store` 生成：

- `CLAUDE.md`
- `AGENTS.md`
- `MEMORY.md`
- ChatGPT summary

这一步应该明确做到：

- projection 是派生视图
- 不是新的真相源

### 6.5 Use

平台或人类真正使用的是：

- human frontend：Obsidian 等
- platform entry：Claude / Codex / OpenClaw / ChatGPT

不是默认直读整个 `Store`

### 6.6 Evolve

当某些 lesson、decision、procedure 反复出现后：

- `lesson -> procedure`
- `procedure -> skill/checklist/template`

## 7. 我建议的新架构图应该怎么理解

如果用一句最简的话来描述新版：

- `Capture` 接住世界
- `Store` 维护干净主库
- `Projections` 把主库送到各平台入口

但这次最关键的变化是：

- `Store` 不再是一个平面 KB
- 而是一个有明确 node family 和状态轴的 clean memory core

所以真正的中枢不再只是：

- `knowledge base`

而是：

- `clean, typed, review-gated memory store`

## 8. 关键原则

### 8.1 外层保持简单，内部保持清晰

不要把架构层越分越多。

外层还是：

- `Capture`
- `Store`
- `Projections`

复杂度应该进 `Store` 的 node family 和状态轴，而不是堆更多层。

### 8.2 治理优先于规模

先解决：

- 污染
- 来源
- promotion
- 送达
- 回流

再谈：

- vector
- graph
- 大规模索引

### 8.3 平台入口必须具体

不要再说抽象的“喂上下文”。

真正要设计的是：

- `CLAUDE.md`
- `AGENTS.md`
- `MEMORY.md`
- ChatGPT summary / instructions

### 8.4 人类和 agent 共享主库，但不共享所有工作区

这是 clean/generated 分层的核心。

- 主库应该尽量共享
- 生成区、候选区、临时区不一定都暴露给人类主视图

### 8.5 写回必须真实存在，但不应该无门槛

write-back 很重要。

但不能默认：

- 所有 agent 产出都直接进 clean store

必须经过：

- candidate
- review
- promote

### 8.6 navigation 是一等对象

如果没有：

- hub
- MOC
- review page
- dashboard

系统就更像 agent 的数据库，不像人的 operating environment。

### 8.7 `research KB` 和 `operational memory` 要共存，但不能混为一谈

这点是今天所有调研合起来最重要的输入之一。

我们不是只做：

- topic wiki

也不是只做：

- life dashboard

而是要把两者放进同一个 `Store`，但保持对象边界清楚。

## 9. 对 roadmap 的直接影响

如果按这个新版架构重做，roadmap 的优先级也应该跟着变。

### Phase 1 应该优先做什么

1. `Store` 新 node families
2. `clean / generated / candidate / persistent / ephemeral` 状态轴
3. `hub / MOC / review` 节点
4. `profile / goals / projects / decisions / procedures / people / routines`
5. review-gated promotion

### Phase 2 应该优先做什么

1. `evidence -> knowledge` compiler loop
2. `platform import-back`
3. same-day correction 快路径
4. projection freshness 和 delivery status

### Phase 3 以后再做什么

1. skill synthesis
2. graph / vector enhancement
3. richer connectors
4. automated health checks

## 10. 一句话总结

如果只用一句话说这次重设计：

- 不是把项目从 `Capture / Store / Projections` 推翻重来
- 而是把它从“KB-first 的外壳”升级成“有 clean/generated 分层、有 review gate、有 research knowledge 和 operational state 共存的 personal memory core”

这才是今天这批调研真正带来的变化。
