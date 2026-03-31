# scraper-search Skills

本目录包含 scraper-search CLI 工具的相关 skill。

## Available Skills

| Skill | 说明 |
|-------|------|
| [scraper-search-splash](./scraper-search-splash/) | 通过 Splash 渲染执行搜索并整理资料 |

## scraper-search-splash

独立的搜索抓取工具，可直接运行。

```bash
cd skills/scraper-search-splash
pip install -r requirements.txt
./search search -q "关键词"
```

### 目录结构

```
scraper-search-splash/
├── skill.md              # Skill 说明
├── search               # 入口脚本
├── requirements.txt     # 依赖
└── scraper_search/      # 源码
    ├── __init__.py
    ├── cli.py
    ├── fetcher.py
    ├── formatter.py
    ├── readability.py
    └── search.py
```

### 命令

| 命令 | 说明 |
|------|------|
| `./search search -q "关键词"` | 搜索并抓取 |
| `./search fetch "URL"` | 抓取单个 URL |
| `./search search -q "词" --no-splash` | 禁用 Splash |

### 参数

- `-q, --query`: 搜索关键词
- `-n, --num`: 结果数量 (默认 5)
- `-o, --output`: 输出文件
- `-f, --format`: 格式 json/markdown (默认 markdown)
- `--no-splash`: 禁用 Splash (默认启用)
- `--proxy`: 代理 URL
