# Architecture Archive

这里存放被后续版本取代、但保留作为历史参考的架构文档。

## 为什么保留

被取代的文档仍然有价值，因为：

- 记录了架构演进的推理过程
- 当前方案里的一些决定需要对比旧方案才能理解
- 未来如果要回溯"为什么当初没走 X 路线"，这些旧文档是答案

## 当前归档

| 文件 | 原位置 | 归档日期 | 取代者 |
|---|---|---|---|
| `reference-architecture.md` | `docs/architecture/reference-architecture.md` | `2026-04-13` | `solution-design-v2.md` → `personal-os-design.md` |
| `solution-design-v1.md`(原名 `solution-design.md`) | `docs/architecture/solution-design.md` | `2026-04-13` | `solution-design-v2.md` → `personal-os-design.md` |

## 当前主文档

归档之外，`docs/architecture/` 下的活跃文档是：

- [personal-os-design.md](../personal-os-design.md) —— `2026-04-13` 起的当前主方案，整个 personal OS 的运转机制
- [solution-design-v2.md](../solution-design-v2.md) —— memory 子系统的 Phase 1 目录与交付物
- [reframed-architecture.md](../reframed-architecture.md) —— 架构演进推理过程，4 层语义切分的由来
- [platform-landing-review.md](../platform-landing-review.md) —— 各 AI 平台的 landing 能力对比，作为参考

