# X Thread Ingest

这份说明只解决一个问题：

- 如果你想把一条 X 帖子和它的社区回复研究完整，最小的抓取链路应该怎么做

## 为什么要单独做这件事

只看公开网页，通常拿不到完整线程。

常见缺口有：

- 回复分页抓不全
- quote tweet 很难完整看到
- 公开搜索结果只露出少量高热内容
- 删除、受保护、或无权限内容直接不可见

所以更稳的流程是：

1. 用 X API 抓原帖
2. 用 `conversation_id` 抓回复
3. 单独抓 quote tweets
4. 把原始 JSON 存下来
5. 再基于结构化结果写总结

## 仓库里现在提供的最小实现

代码：

- [fetch_x_thread.py](/Users/dxy-air/workspace/projects/memory_system/scripts/fetch_x_thread.py)
- [x_thread.py](/Users/dxy-air/workspace/projects/memory_system/src/memory_system/x_thread.py)

测试：

- [test_x_thread.py](/Users/dxy-air/workspace/projects/memory_system/tests/test_x_thread.py)

输出目录默认会长成：

```text
data/x_threads/<tweet_id>/
  raw/
    root.json
    replies-page-001.json
    quotes-page-001.json
  thread.json
  thread.md
```

## 它现在抓什么

### 1. 原帖

脚本先查：

- `GET /2/tweets/:id`

拿到原帖正文、作者、时间、metrics。

### 2. 回复

回复抓的是整个 conversation：

- `query=conversation_id:<tweet_id> -is:retweet`

这一步的关键不是“只抓直接回复”，而是把整条线程下可见的 replies 都拿下来。

脚本支持：

- `--scope recent`
- `--scope all`

其中：

- `recent` 只能覆盖最近 7 天
- 更老的帖子要用 `all`

### 3. Quote tweets

脚本还会单独抓：

- `GET /2/tweets/:id/quote_tweets`

因为 quote tweet 往往包含更完整的延展讨论，只看 replies 不够。

## 怎么用

先准备 token：

```bash
export X_BEARER_TOKEN=...
```

然后抓一条线程：

```bash
PYTHONPATH=src python3 scripts/fetch_x_thread.py 2039805659525644595 --scope recent
```

更老的线程：

```bash
PYTHONPATH=src python3 scripts/fetch_x_thread.py 2039805659525644595 --scope all
```

只先抓 replies，不抓 quote：

```bash
PYTHONPATH=src python3 scripts/fetch_x_thread.py 2039805659525644595 --skip-quotes
```

## 生成结果怎么用

### raw JSON

`raw/` 里的 JSON 是证据层。

作用：

- 保留原始抓取结果
- 之后要重新归纳时，不用再重新请求
- 能区分“原帖里真的有”还是“总结时自己脑补的”

### thread.json

这是规范化后的中间层。

里面会有：

- `root`
- `replies`
- `quotes`
- `participants`
- `stats`

这层适合后续继续做：

- 去重
- 聚类
- 回复树重建
- 主题抽取

### thread.md

这是一个初步报告模版。

它目前不会替你自动做高质量语义总结。

它做的是：

- 把原帖基本信息列出来
- 统计 reply / quote / participant 数量
- 给出高互动样本
- 预留 analyst notes 区块

这样你后面就可以基于这份模版继续写：

- 大家怎么评价
- 有哪些共识
- 有哪些非共识
- 对项目的输入

## 这套实现故意没做什么

当前版本是最小实现，没有上这些东西：

- 回复树重建
- 主题聚类
- 语义 dedupe
- LLM 自动归纳
- 情绪/立场分类
- 多条线程批量 ingest

原因很简单：

- 先把“抓全并留证据”做对，比先做 fancy summarize 更重要

## 已知限制

### 1. 不是绝对完整

即使用 API，也仍然拿不到：

- 已删除内容
- 受保护账号内容
- 当前 token 无权读取的内容

所以更准确的目标是：

- 抓到“当前账号可访问的完整公开线程”

### 2. `recent` 有时间窗口

X 官方文档明确说 recent search 是最近 7 天。

如果线程更老，就需要：

- `--scope all`
- 并且你的开发者权限要支持 all search

### 3. 报告只是 scaffold

`thread.md` 不是最终分析。

它只是把研究的底稿先搭出来，让后续总结建立在抓取证据上，而不是建立在零散网页片段上。

## 下一步最值得做什么

如果你要把这件事继续做深，我建议顺序是：

1. 加回复树重建
2. 加 quote/reply 分主题聚类
3. 再加 analyst summary 生成
4. 最后再把它接进长期 research KB

## 参考

- X conversation id: <https://docs.x.com/x-api/fundamentals/conversation-id>
- X recent search: <https://docs.x.com/x-api/posts/search/introduction>
- X quote posts: <https://docs.x.com/enterprise-api/posts/quote-tweets/introduction>
