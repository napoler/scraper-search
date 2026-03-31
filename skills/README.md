# scraper-search Skills

本目录包含 scraper-search CLI 工具的相关 skill。

## Available Skills

| Skill | 说明 |
|-------|------|
| [scraper-search-splash](./scraper-search-splash/) | 通过 Splash 渲染执行搜索并整理资料 |

---

## scraper-search-splash

通过 Splash 渲染执行搜索并整理资料的 CLI 工具，支持 JS 渲染、代理配置、多节点负载均衡。

### 快速安装

```bash
# 克隆仓库
git clone https://github.com/napoler/scraper-search.git
cd scraper-search

# 安装依赖
cd skills/scraper-search-splash
pip install -r requirements.txt

# 赋予执行权限
chmod +x search
```

### 快速使用

```bash
# 搜索并抓取（默认启用 Splash）
./search search -q "关键词"

# 指定结果数量
./search search -q "关键词" -n 10

# 抓取单个 URL
./search fetch "https://example.com"

# 输出为 JSON
./search search -q "关键词" -f json -o results.json
```

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SPLASH_URL` | `http://127.0.0.1:8050` | Splash 服务器地址 |
| `SPLASH_URLS` | 同 SPLASH_URL | 多个 Splash 节点（逗号分隔） |
| `HTTP_PROXY` | 无 | HTTP 代理 |
| `HTTPS_PROXY` | 无 | HTTPS 代理 |

### 多节点配置

```bash
# 多个 Splash 节点负载均衡
export SPLASH_URLS="http://node1:8050,http://node2:8050,http://node3:8050"
```

### 完整命令

| 命令 | 说明 |
|------|------|
| `./search search -q "关键词"` | 搜索并抓取内容 |
| `./search fetch "URL"` | 抓取单个 URL |
| `./search search -q "词" --no-splash` | 禁用 Splash 直接请求 |

### 参数

- `-q, --query`: 搜索关键词
- `-n, --num`: 结果数量 (默认 5)
- `-o, --output`: 输出文件
- `-f, --format`: 格式 json/markdown (默认 markdown)
- `--no-splash`: 禁用 Splash (默认启用)
- `--proxy`: 代理 URL

### 前置要求

Splash 服务（可选，禁用 Splash 则不需要）：

```bash
# Docker 启动 Splash
docker run -p 8050:8050 scrapinghub/splash

# 或使用 Docker Compose
docker-compose up -d splash
```
