#!/bin/bash
# Install script for scraper-search-splash skill

set -e

echo "=== scraper-search-splash 安装程序 ==="

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3，请先安装 Python"
    exit 1
fi

echo "✓ Python 版本: $(python3 --version)"

# 检查 pip
if ! command -v pip &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "❌ 错误: 未找到 pip，请先安装 pip"
    exit 1
fi

# 安装依赖
echo ""
echo "=== 安装依赖 ==="
if command -v pip &> /dev/null; then
    pip install -r requirements.txt
else
    python3 -m pip install -r requirements.txt
fi

# 赋予执行权限
echo ""
echo "=== 设置执行权限 ==="
chmod +x search
chmod +x *.sh 2>/dev/null || true

echo ""
echo "=== 安装完成 ==="
echo ""
echo "快速使用:"
echo "  ./search search -q \"关键词\""
echo "  ./search fetch \"https://example.com\""
echo ""
echo "查看帮助:"
echo "  ./search --help"
