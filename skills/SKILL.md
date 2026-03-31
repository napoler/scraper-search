---
name: scraper-search-splash
description: 通过 Splash 渲染执行搜索并整理资料 - 使用 scraper-search CLI 工具，支持 Splash JS 渲染、代理配置，用于获取搜索结果正文内容。
version: 1.0.0
tags:
  - search
  - scraping
  - splash
  - content-extraction
  - research
---

# Scraper Search Splash Skill

## When to Activate

当以下任一条件满足时激活：

- 用户需要**搜索并整理**多个来源的资料
- 用户需要获取搜索结果的**详细内容**（不只是摘要）
- 用户提到"调研"、"资料收集"、"多来源"、"搜索结果详情"
- 用户需要抓取需要 JavaScript 渲染的页面内容
- 上下文包含 search、scrape、research、survey、collect、Splash 等关键词

## 核心依赖

**必须先安装 scraper-search CLI 工具**：

```bash
cd /mnt/data/dev/scraper-search
pip install -e .
```

## 核心功能

| 功能 | 说明 |
|------|------|
| 搜索执行 | 使用 Bing 搜索引擎获取搜索结果 |
| Splash 渲染 | 默认启用 Splash JS 渲染，支持动态页面 |
| 内容抓取 | 使用 readability-lxml 提取正文 |
| 代理支持 | 支持 HTTP/HTTPS/SOCKS 代理配置 |
| 格式输出 | 支持 JSON 和 Markdown 格式 |

## 使用流程

### Step 1: 安装依赖

```bash
cd /mnt/data/dev/scraper-search
pip install -e .
```

### Step 2: 执行搜索

**搜索命令（默认启用 Splash）**：

```bash
scraper-search search -q "关键词" -n 5
```

**参数说明**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-q, --query` | 搜索关键词 | 必需 |
| `-n, --num` | 返回结果数量 | 5 |
| `-o, --output` | 输出文件路径 | stdout |
| `-f, --format` | 输出格式 (json/markdown) | markdown |
| `--no-splash` | 禁用 Splash 渲染 | 默认启用 |
| `--splash-url` | Splash 服务器地址 | http://127.0.0.1:8050 |
| `--proxy` | 代理 URL | 无 |

### Step 3: 单 URL 抓取

```bash
# 抓取单个 URL 的正文内容
scraper-search fetch "https://example.com/article"

# 使用代理抓取
scraper-search fetch "https://example.com" --proxy "http://127.0.0.1:7890"

# 禁用 Splash（使用普通 HTTP）
scraper-search fetch "https://example.com" --no-splash
```

### Step 4: 环境变量配置

在 `.env` 文件中配置（参考 `.env.example`）：

```bash
# Splash 配置
SPLASH_URL=http://127.0.0.1:8050
SPLASH_PROXY=http://your-proxy:8080

# 代理配置
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
SOCKS_PROXY=socks5://127.0.0.1:7891

# 请求配置
MAX_RETRIES=3
REQUEST_DELAY_MIN=1
REQUEST_DELAY_MAX=3
REQUEST_TIMEOUT=10
```

## 使用示例

### 示例 1: 基本搜索

```bash
scraper-search search -q "Python 教程" -n 3
```

输出：
```markdown
🔍 Searching for: Python 教程
📋 Found 10 links
  [1/3] Fetching: https://example.com/python-guide
    ✅ Python 完全指南...
       本文介绍 Python 的基础知识...
```

### 示例 2: 搜索并保存到文件

```bash
scraper-search search -q "机器学习" -n 5 -o result.md -f markdown
```

### 示例 3: 使用代理

```bash
scraper-search search -q "AI 最新进展" --proxy "http://127.0.0.1:7890"
```

### 示例 4: 禁用 Splash（适合简单页面）

```bash
scraper-search search -q "简单页面" --no-splash
```

## 降级策略

```
Splash (默认) → 普通 HTTP (--no-splash)
     ↓                  ↓
 失败              失败
     ↓                  ↓
 报告错误         尝试代理
```

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| Splash 连接失败 | Splash 服务未启动 | 启动 Splash 或用 `--no-splash` |
| 403 Forbidden | 反爬限制 | 尝试代理或 `--no-splash` |
| 超时 | 网络慢/页面大 | 增加 `REQUEST_TIMEOUT` |
| 解析失败 | 页面结构特殊 | 手动检查页面内容 |

## 限制与注意事项

1. **法律合规**: 仅用于合法用途，遵守网站服务条款
2. **Splash 服务**: 需要本地运行 Splash 服务（Docker 或源码启动）
3. **代理成本**: 代理服务可能有频率或流量限制
4. **反爬限制**: 频繁请求可能触发限制，请合理使用延时
5. **内容版权**: 整理的资料仅供个人研究使用

## 输出格式

### Markdown 格式（默认）

```markdown
# 关键词资料整理

## 来源列表

1. [来源1标题](https://example.com/article1)
2. [来源2标题](https://example.com/article2)

## 详细内容

### 来源1: 来源1标题
**链接**: https://example.com/article1
**状态**: 200

### Content

正文内容...

---

### 来源2: 来源2标题
**链接**: https://example.com/article2
**状态**: 200

### Content

正文内容...

## 总结

- 共收集 N 个来源
```

### JSON 格式

```json
{
  "query": "关键词",
  "results": [
    {
      "title": "来源1标题",
      "url": "https://example.com/article1",
      "content": "正文内容...",
      "status": 200
    }
  ],
  "total": 5,
  "extracted_at": "2026-04-01T12:00:00Z"
}
```

## 快速参考

```bash
# 搜索（默认 Splash 渲染）
scraper-search search -q "关键词"

# 搜索 N 个结果
scraper-search search -q "关键词" -n 10

# 搜索并保存
scraper-search search -q "关键词" -o output.md

# 单 URL 抓取
scraper-search fetch "https://example.com"

# 使用代理
scraper-search fetch "https://example.com" --proxy "http://proxy:8080"

# 禁用 Splash
scraper-search fetch "https://simple-page.com" --no-splash
```

---

**创建日期**: 2026-04-01
