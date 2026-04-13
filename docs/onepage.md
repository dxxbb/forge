# Personal OS · One Page

一份可独立阅读的入口文档。读完就能回答：这个项目是什么、为什么这么做、现在跑到哪里、下一步是什么。 适合直接放进 `personal_OS` 作为这个项目的门面页。

更新日期：`2026-04-13`

---

## 1. 一句话

把个人 AI assistant 背后的"知识 + 偏好 + 视图"做成一个 **build system**： **所有变更都是 git diff，所有处理都走 PR，所有 view 都是预编译产物，所有判断由 agent + guideline 做，所有管线由代码做。**

## 2. 为什么要做

现有个人 AI 方案在三件事上都不够：

1. **不知道你是谁** —— 每次开新会话都要重新介绍身份、偏好、上下文。
2. **学不会教训** —— 你纠正一次之后，下次会话又犯同样错误。
3. **没有审计** —— agent 记住了什么、为什么记住、什么时候变的，全不可见。

Personal OS 的目标是让这三件事都变成**可见的、可 review 的、可 revert 的 git 状态**。

## 3. 核心隐喻：Make / Bazel

| 传统 build system | Personal OS |
| --- | --- |
| 源代码 | `kind: source` 文件（身份、偏好原文、知识条目） |
| 编译产物 | `kind: derived` 文件（SP、view/CLAUDE.md） |
| `Makefile` 依赖图 | derived 文件 frontmatter 里的 `upstream:` |
| `make` | `scripts/approve.py` 里的 rebuild |
| CI review | git PR workflow |
| 事件触发 | `scripts/watch.py` 扫 git diff |

**不是"把知识存起来"，而是"每次上游变了，下游自动跟着变，新的 view 立刻可用"。**

## 4. 三个角色，互不越界

| 角色 | 职责 |
| --- | --- |
| **人** | 控制 review gate：approve / reject / request-changes。唯一能改 `user/` 和 `operating-rule/` 的角色。 |
| **Agent**（Claude Code） | 定期 monitor OS（默认每天 1 次），扫 inbox，读 guideline，评估对话，产 PR。不能直接改 main 上的 source。 |
| **Code**（scripts） | 扫 git diff、算依赖图、rebuild derived、squash merge。不做任何判断。 |

判断型工作归 agent，机械型工作归 code，决策型工作归人。这条线是整个系统的承重墙。

## 5. 数据流（一次完整的闭环）

```
对话/memo → commit 到 main
   ↓
watch.py 扫 git diff → system/monitor-inbox/ 产 TODO
   ↓
Agent monitor → 读 TODO + global.md + events/<type>.md
   ↓
Agent 评估 → 在 pr/<id>-... branch 上 commit 改动
   ↓
人 git diff main...pr/<id> 看改动
   ↓
 ┌──────────┬────────────────────┬─────────────┐
 ↓          ↓                    ↓
approve    request-changes      reject
 ↓          ↓                    ↓
rebuild    写 comment 文件       删 branch
下游       入队 pr_revision      记 change log
 ↓          ↓
squash     agent 再改一版 → 回到 "人 review"
merge
 ↓
新版 view 立刻可用
```

## 6. 顶层目录（vault）

vault 是一个**独立的 git repo**（不是本仓库）。

| 目录 | 作用 | 写入者 |
| --- | --- | --- |
| `user/` | 身份真相源（about me、philosophy、daily memo） | 人 |
| `knowledge base/` | 长期知识节点 | 人 + agent via PR |
| `workspace/` | 活跃项目、主题、阅读、写作 | 人 + agent via PR |
| `conversation memory/` | 对话 transcript 原始回流 | agent 直写 |
| `ingest src/` | clipper / book / 外部素材 | agent 直写 |
| `assist/` | section detail → sp → view 的依赖传播链 | agent via PR；derived 由脚本产 |
| `config store/` | 秘钥、配置 | 人（agent 禁碰） |
| `system/` | control plane：monitor-inbox、change-log、operating-rule、pr-review | 固定脚本 + 指定 agent |

**四个区域，四种写入规矩**：

1. **直写区**（`conversation memory/`、`ingest src/`、`assist/preference/improve/learning inbox/`）—— 原材料，agent 可以直接 commit 到 main。
2. **PR 区**（`user/`、`knowledge base/`、`assist/section detail|sp|view/`、`workspace/`）—— 下游有依赖传播或对 AI 行为有直接影响，必须走 PR + review。
3. **控制面**（`system/**`）—— 只能由 `watch.py` / `approve.py` / `request-changes.py` 等固定脚本写，带 `System-owned-by:` trailer，watcher 自动跳过。
4. **禁碰**（`config store/`、`system/operating-rule/`）—— agent 不能自己改游戏规则，也不该碰秘钥。

## 7. 文件约定

每个被系统管理的 markdown 文件靠 frontmatter 分类：

```yaml
---
kind: source          # 或 derived / system
---
```

derived 文件额外带：

```yaml
---
kind: derived
upstream:
  - user/about me/me.md
  - user/about me/philosophy.md
generated_by: pr-0042
last_rebuild_at: 2026-04-13T10:23:00
---
```

**没有 frontmatter → 默认视为 source**。理由：漏处理一个 source 比漏处理一个 derived 危险得多。

**依赖图的真相源是分散的**：每个 derived 文件自己声明依赖谁。反向查询（"改这个 source 会影响谁"）由 `scripts/deps.py` 扫全库 frontmatter 现算。

## 8. PR ≠ CR

CR 只有两种出口（过 / 不过），PR 有三种：**approve / reject / request-changes**。第三种是关键，它允许"方向对但细节不对"的提案经过多轮 comment 往返收敛。

**Comment 往返机制**：

- comment 文件 commit 在 PR branch 上（`system/pr-review/pr-<id>-comments-round<N>.md`）
- 每轮一个新文件，不 append
- agent 读 comment 后可以写 counter-argument（`pr-<id>-response-round<N>.md`）
- branch 删除时 comment 一起消失；squash merge 时 comment 不进 main
- guideline 要求 agent 在 `round >= 3` 时主动喊停

**约束**：每个 PR 只改一个 source 文件。`approve.py` 开头有断言强制执行。

## 9. Watcher 规则

- **只扫 main**（避免无限循环，branch 上的 WIP 对 watcher 不可见）
- 从 `system/.watcher-state` 的 `last_seen_commit` 扫到 HEAD
- 跳过带这些 trailer 的 commit：`Approved-by:` / `Rebuilt-by:` / `System-owned-by:`
- 跳过路径在 `system/**` 下的文件
- 跳过 `kind: derived` 和 `kind: system` 的文件
- 剩下的按路径前缀分类成 `event_type`，写进 `system/monitor-inbox/`

## 10. Guideline 的两层结构

```
system/operating-rule/
├── global.md                # 跨事件的硬约束 + agent 身份
└── events/
    ├── conversation.md      # MVP 唯一的事件处理规则
    ├── pr_revision.md       # PR 修订 / comment 回合
    └── ...                  # Phase 2+ 逐步加
```

Agent 处理 inbox 项时载入：`global.md + events/<event_type>.md + inbox TODO`。

**不用 YAML schema**：guideline 的灵魂是"灵活的 convention，由 agent 自由判断"，硬编码会扼杀这个空间。

## 11. 当前状态（2026-04-13）

- ✅ 调研完成（docs/research/ 6 篇，涵盖当前实践、社区模式、Karpathy wiki、practitioner 访谈）
- ✅ 架构方案敲定（build-system 模型 + 三角色边界 + comment round-trip）
- ✅ 文档重整（老 JSON prototype、老目录模型归档进 `_archive/`）
- 🚧 MVP Week 1 开工中：6 个目录骨架 + `watch.py` / `deps.py` / `approve.py` / `reject.py` / `request-changes.py` + `global.md` + `events/conversation.md` + `events/pr_revision.md`
- ⏳ Phase 2+：多事件类型、workspace 接入、自动化 watcher、组合式 SP、preference 完整闭环、fact staleness

MVP 验收红线：**一次对话 → 一条 inbox TODO → 一个 PR → 一次 approve → 一次 merge → 一个新版 CLAUDE.md**，整条链路零手工补位。

## 12. 显式推迟的问题

这些问题被讨论过，但**明确推迟**到 Phase 2+，不影响 MVP：

- Fact staleness / 冲突失效机制（MVP 靠 `git revert` 兜底）
- 并发 PR 冲突（MVP 量低，一次一个 PR）
- Lifecycle 和归档（`workspace/` 不在 MVP 里）
- 非 conversation 的 ingest 源处理规则
- 组合式 SP（master + role overlay）
- 自动化 watcher（MVP 手动跑，cron/launchd 是 Phase 2）

## 13. 相对其他方案的独特点

| 维度 | 别人 | Personal OS |
| --- | --- | --- |
| 检索 | vector / graph / LLM retrieval | **预编译 view**，零检索 |
| 触发 | 对话 hook / 人工指令 | **git diff + watcher** |
| Review | 无 | **三种出口的 PR workflow** |
| 下游传播 | 手工 or 无 | **依赖图 + rebuild** |
| 失效 | 无 or 黑盒 extract | **git revert** |
| 边界 | 全 agent 或全代码 | **外层代码 + 内层 agent** 明确分工 |

劣势也写清楚：实现复杂度比 Karpathy wiki / Mem0 高；依赖 git 熟练度；guideline 的初始版本一定是错的，需要多轮迭代。

## 14. 入口文档

- personal-os-design.md —— 整体运转机制（最详细）
- mvp-week1.md —— Week 1 交付物和验收闭环
- platform-landing-review.md —— 各 AI 平台 landing 能力对比
- [README](../README.md) —— 仓库地图

## 15. 设计原则

- **Local-first by default**
- **Git 是数据总线**：commit = 事件，branch = PR，log = 审计，revert = 撤销
- **Agent 是主角，scripts 是工具**
- **外层代码 + 内层 agent 的明确边界**
- **Review gate 防止 agent 污染主库**
- **依赖图 + rebuild 保证下游一致性**
- **预编译打败检索**