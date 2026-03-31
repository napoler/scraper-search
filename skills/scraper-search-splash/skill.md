---
name: scraper-search-splash
description: 通过 Splash 渲染执行搜索并整理资料 - 支持 Splash JS 渲染、代理配置
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

## 目录结构

```
scraper-search-splash/
├── skill.md              # 本文件
├── search                # 入口脚本
├── requirements.txt      # 依赖列表
└── scraper_search/      # 源码包
    ├── __init__.py
    ├── cli.py
    ├── fetcher.py
    ├── formatter.py
    ├── readability.py
    └── search.py
```

## 安装与使用

```bash
cd skills/scraper-search-splash
./search search -q "关键词"
```

## 命令

| 命令 | 说明 |
|------|------|
| `./search search -q "关键词"` | 搜索并抓取内容 |
| `./search fetch "URL"` | 抓取单个 URL |

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-q, --query` | 搜索关键词 | 必需 |
| `-n, --num` | 结果数量 | 5 |
| `-o, --output` | 输出文件 | stdout |
| `-f, --format` | 格式 (json/markdown) | markdown |
| `--no-splash` | 禁用 Splash | 默认启用 |
| `--proxy` | 代理 URL | 无 |

## 环境变量

```bash
SPLASH_URL=http://127.0.0.1:8050
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```
