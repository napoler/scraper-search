# scraper-search Skills

本目录包含 scraper-search CLI 工具的相关 skill。

## Available Skills

| Skill | 说明 |
|-------|------|
| [scraper-search-splash](./scraper-search-splash/) | 通过 Splash 渲染执行搜索并整理资料 |

## 安装

```bash
cd /mnt/data/dev/scraper-search
pip install -e .
```

## 快速使用

```bash
# 搜索（默认 Splash 渲染）
scraper-search search -q "关键词"

# 单 URL 抓取
scraper-search fetch "https://example.com"

# 使用代理
scraper-search search -q "关键词" --proxy "http://127.0.0.1:7890"
```
