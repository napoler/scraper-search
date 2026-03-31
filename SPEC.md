# scraper-search 项目规范

## 1. 项目概述

**项目名称**: scraper-search
**项目类型**: Python CLI 工具
**核心功能**: 搜索关键词 → 获取链接正文 → 提取内容 → 整理为 Markdown/JSON 资料
**目标用户**: 需要收集和整理网络资料的用户

## 2. 功能需求

### 2.1 核心功能

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 关键词搜索 | 使用 Bing 搜索引警获取关键词相关链接 | P0 |
| 内容抓取 | HTTP 请求抓取链接 HTML 内容（支持 Splash 渲染） | P0 |
| 正文提取 | 使用 readability-lxml 提取页面正文 | P0 |
| 格式转换 | 将 HTML 转换为 Markdown 格式 | P0 |
| 结果输出 | 支持输出到文件或 stdout | P0 |
| 代理支持 | 支持 HTTP/HTTPS/SOCKS 代理配置 | P0 |

### 2.2 CLI 命令

```bash
# 搜索并提取内容
scraper-search search -q "关键词" -n 5 -o output.md

# 单 URL 抓取
scraper-search fetch "https://example.com" -o result.md

# 使用 Splash 渲染（支持 JavaScript 渲染的页面）
scraper-search fetch "https://example.com" --use-splash -o result.md

# 使用代理
scraper-search fetch "https://example.com" --proxy http://127.0.0.1:7890 -o result.md
```

### 2.3 输出格式

- **Markdown**: 适合阅读，包含标题、链接、内容
- **JSON**: 适合程序处理，包含完整元数据

## 3. 技术方案

### 3.1 技术栈

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| CLI 框架 | Click | 命令行界面 |
| HTTP 请求 | requests | 网页抓取 |
| Splash 客户端 | requests + JSON RPC | Splash 浏览器渲染支持 |
| 正文提取 | readability-lxml + html2text | 从 HTML 提取可读内容 |
| 搜索引警 | search-engines-kit | Bing 搜索支持 |
| 解析库 | BeautifulSoup | HTML 解析 |

### 3.2 项目结构

```
scraper-search/
├── src/scraper_search/
│   ├── __init__.py
│   ├── cli.py          # CLI 入口
│   ├── search.py       # 搜索引警封装
│   ├── fetcher.py       # HTTP 抓取
│   ├── readability.py    # 正文提取
│   └── formatter.py     # 输出格式化
├── tests/              # 测试目录
├── requirements.txt     # 依赖声明
├── pyproject.toml       # 项目配置
└── .env.example        # 环境变量模板
```

### 3.3 依赖管理

- `requirements.txt`: 依赖声明文件
- `pyproject.toml`: 项目元数据和构建配置
- `.python-version`: Python 版本固定 (3.10+)
- `.env.example`: 环境变量模板

## 4. 配置项

| 变量 | 默认值 | 说明 |
|------|--------|------|
| MAX_RETRIES | 3 | 请求最大重试次数 |
| REQUEST_DELAY_MIN | 1 | 请求间隔最小秒数 |
| REQUEST_DELAY_MAX | 3 | 请求间隔最大秒数 |
| REQUEST_TIMEOUT | 10 | 请求超时秒数 |
| SPLASH_URL | http://127.0.0.1:8050 | Splash 服务地址 |
| HTTP_PROXY | - | HTTP 代理地址 |
| HTTPS_PROXY | - | HTTPS 代理地址 |
| SOCKS_PROXY | - | SOCKS 代理地址 |

## 5. 验收标准

- [ ] CLI 命令 `scraper-search search -q "关键词"` 能正常工作
- [ ] CLI 命令 `scraper-search fetch URL` 能正常工作
- [ ] 输出 Markdown 格式内容可读
- [ ] 输出 JSON 格式包含完整元数据
- [ ] 支持 `-o` 参数输出到文件
- [ ] 依赖环境可通过 requirements.txt 安装
- [ ] 项目可通过 `pip install -e .` 安装
- [ ] 支持 `--use-splash` 参数使用 Splash 渲染
- [ ] 支持 `--proxy` 参数配置代理
