---
name: scraper-search-splash
description: 通过 Splash 渲染执行搜索并整理资料 - 支持 Splash JS 渲染、代理配置、内容提取
version: 1.0.0
tags:
  - search
  - scraping
  - splash
  - content-extraction
  - research
---

# Scraper Search Splash Skill

通过 Splash 渲染执行搜索并整理资料的 CLI 工具。

## 环境发现

```bash
# 1. 检查 Splash 是否可用
curl -s http://127.0.0.1:8050 | head -5

# 2. 检查依赖安装状态
cd skills/scraper-search-splash
pip list | grep -E "click|requests|beautifulsoup4|lxml"

# 3. 验证环境变量配置
echo "SPLASH_URL: ${SPLASH_URL:-http://127.0.0.1:8050}"
echo "HTTP_PROXY: ${HTTP_PROXY:-未设置}"
```

## 安装程序

```bash
cd skills/scraper-search-splash
pip install -q -r requirements.txt
```

## 执行工作流程

### 阶段 1: 搜索并抓取

```bash
# 基本搜索（默认启用 Splash）
./search search -q "关键词"

# 指定结果数量
./search search -q "关键词" -n 10

# 禁用 Splash（直接 HTTP）
./search search -q "关键词" --no-splash

# 使用代理
./search search -q "关键词" --proxy http://127.0.0.1:7890
```

### 阶段 2: 单 URL 抓取

```bash
# 抓取单个页面
./search fetch "https://example.com"

# 禁用 Splash
./search fetch "https://example.com" --no-splash
```

### 阶段 3: 输出格式

```bash
# 输出为 JSON
./search search -q "关键词" -f json -o results.json

# 输出为 Markdown
./search search -q "关键词" -f markdown -o results.md
```

## 错误处理程序

| 错误症状 | 诊断命令 | 解决方案 |
|----------|----------|----------|
| Splash 连接失败 | `curl -s http://127.0.0.1:8050` | 启动 Splash: `docker run -p 8050:8050 scrapinghub/splash` |
| 代理无效 | 检查 `--proxy` URL 格式 | 确认代理地址和端口 |
| 搜索无结果 | 检查网络连通性 | `curl -I https://www.bing.com` |
| 内容提取失败 | 使用 `--no-splash` 重试 | 可能是 JS 渲染超时 |

## 执行检查清单

```
[ ] 1. Splash 服务运行中 (http://127.0.0.1:8050)
[ ] 2. 依赖已安装 (requirements.txt)
[ ] 3. 网络可访问 Bing
[ ] 4. 代理配置正确（如使用）
[ ] 5. 输出文件有写入权限
```

## 工作流程图

```
┌─────────────────────────────────────────────────────────┐
│                    搜索抓取工作流                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  用户输入 query ──→ SearchEngine.search()               │
│                            │                            │
│                            ▼                            │
│                    获取链接列表                           │
│                            │                            │
│                            ▼                            │
│              ┌─────────────────────────────┐             │
│              │  use_splash=True?          │             │
│              └─────────────────────────────┘             │
│                    │                 │                 │
│                 Yes                 No                  │
│                  ▼                  ▼                   │
│         Splash 渲染          直接 HTTP 请求              │
│                  │                  │                   │
│                  └────────┬─────────┘                   │
│                           ▼                             │
│                  ContentExtractor                        │
│                  ├─ extract_title()                     │
│                  └─ extract_content()                   │
│                           │                             │
│                           ▼                             │
│                  OutputFormatter                         │
│                  └─ format_results()                   │
│                           │                             │
│                           ▼                             │
│                      输出结果                            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SPLASH_URL` | `http://127.0.0.1:8050` | 单个 Splash 服务器地址 |
| `SPLASH_URLS` | 同 SPLASH_URL | 多个 Splash 节点（逗号分隔），负载均衡 |
| `HTTP_PROXY` | 无 | HTTP 代理 |
| `HTTPS_PROXY` | 无 | HTTPS 代理 |

### 多节点配置示例

```bash
# 多个 Splash 节点负载均衡
export SPLASH_URLS="http://192.168.1.10:8050,http://192.168.1.11:8050,http://192.168.1.12:8050"

# 多个节点 + 不同代理
export SPLASH_URLS="http://node1:8050,http://node2:8050"
export SPLASH_PROXY="http://proxy:8080"  # Splash 自身的代理
```

## 快速参考

```bash
# 完整示例
cd skills/scraper-search-splash
./search search -q "Claude AI tutorial" -n 5 -f markdown -o tutorial.md

# 查看帮助
./search --help
./search search --help
./search fetch --help
```
